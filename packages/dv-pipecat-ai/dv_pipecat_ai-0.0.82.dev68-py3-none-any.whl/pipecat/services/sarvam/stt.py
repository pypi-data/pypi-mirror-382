"""Sarvam AI Speech-to-Text service implementation.

This module provides a streaming Speech-to-Text service using Sarvam AI's WebSocket-based
API. It supports real-time transcription with Voice Activity Detection (VAD) and
can handle multiple audio formats for Indian language speech recognition.
"""

import asyncio
import base64
import json
from enum import StrEnum
from typing import Literal, Optional
from urllib.parse import urlencode

from loguru import logger
from pydantic import BaseModel

from pipecat.audio.resamplers.resampy_resampler import ResampyResampler
from pipecat.frames.frames import (
    CancelFrame,
    EndFrame,
    ErrorFrame,
    StartFrame,
    TranscriptionFrame,
)
from pipecat.services.stt_service import STTService
from pipecat.transcriptions.language import Language
from pipecat.utils.time import time_now_iso8601
from pipecat.utils.tracing.service_decorators import traced_stt

try:
    import websockets
    from sarvamai import AsyncSarvamAI
    from sarvamai.speech_to_text_translate_streaming.socket_client import (
        AsyncSpeechToTextTranslateStreamingSocketClient,
    )
    from websockets.protocol import State
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error("In order to use Sarvam, you need to `pip install pipecat-ai[sarvam]`.")
    raise Exception(f"Missing module: {e}")


def language_to_sarvam_language(language: Language) -> str:
    """Convert Language enum to Sarvam language code.

    Args:
        language: The Language enum to convert.

    Returns:
        The corresponding Sarvam language code string.

    Raises:
        ValueError: If the language is not supported by Sarvam.
    """
    match language:
        case Language.BN_IN:
            return "bn-IN"
        case Language.GU_IN:
            return "gu-IN"
        case Language.HI_IN:
            return "hi-IN"
        case Language.KN_IN:
            return "kn-IN"
        case Language.ML_IN:
            return "ml-IN"
        case Language.MR_IN:
            return "mr-IN"
        case Language.TA_IN:
            return "ta-IN"
        case Language.TE_IN:
            return "te-IN"
        case Language.PA_IN:
            return "pa-IN"
        case Language.OR_IN:
            return "od-IN"
        case Language.EN_US:
            return "en-US"
        case Language.EN_IN:
            return "en-IN"
        case Language.AS_IN:
            return "as-IN"
        case _:
            raise ValueError(f"Unsupported language: {language}")


class TranscriptionMetrics(BaseModel):
    """Metrics for transcription performance."""

    audio_duration: float
    processing_latency: float


class TranscriptionData(BaseModel):
    """Data structure for transcription results."""

    request_id: str
    transcript: str
    language_code: Optional[str]
    metrics: Optional[TranscriptionMetrics] = None
    is_final: Optional[bool] = None


class TranscriptionResponse(BaseModel):
    """Response structure for transcription data."""

    type: Literal["data"]
    data: TranscriptionData


class VADSignal(StrEnum):
    """Voice Activity Detection signal types."""

    START = "START_SPEECH"
    END = "END_SPEECH"


class EventData(BaseModel):
    """Data structure for VAD events."""

    signal_type: VADSignal
    occured_at: float


class EventResponse(BaseModel):
    """Response structure for VAD events."""

    type: Literal["events"]
    data: EventData


class SarvamSTTService(STTService):
    """Sarvam speech-to-text service.

    Provides real-time speech recognition using Sarvam's WebSocket API.
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "saaras:v2.5",
        language: Language = Language.HI_IN,
        **kwargs,
    ):
        """Initialize the Sarvam STT service.

        Args:
            api_key: Sarvam API key for authentication.
            model: Sarvam model to use for transcription.
            language: Language for transcription. Defaults to Hindi (India).
            **kwargs: Additional arguments passed to the parent STTService.
                Note: Sarvam requires 16kHz audio. If your input is a different
                sample rate, it will be automatically resampled to 16kHz.
        """
        super().__init__(**kwargs)

        self.set_model_name(model)
        self._api_key = api_key
        self._model = model
        self._language = language
        self._target_sample_rate = 16000  # Sarvam requires 16kHz

        self._client = AsyncSarvamAI(api_subscription_key=api_key)
        self._websocket = None
        self._websocket_connection = None
        self._listening_task = None
        self._resampler = ResampyResampler()

        # Register VAD event handlers
        self._register_event_handler("on_speech_started")
        self._register_event_handler("on_speech_ended")

    def can_generate_metrics(self) -> bool:
        """Check if this service can generate processing metrics.

        Returns:
            True, as Sarvam service supports metrics generation.
        """
        return True

    async def set_model(self, model: str):
        """Set the Sarvam model and reconnect.

        Args:
            model: The Sarvam model name to use.
        """
        await super().set_model(model)
        logger.info(f"Switching STT model to: [{model}]")
        self._model = model
        await self._disconnect()
        await self._connect()

    async def set_language(self, language: Language):
        """Set the language and reconnect.

        Args:
            language: The Language enum to use.
        """
        logger.info(f"Switching STT language to: [{language}]")
        self._language = language
        await self._disconnect()
        await self._connect()

    async def start(self, frame: StartFrame):
        """Start the Sarvam STT service.

        Args:
            frame: The start frame containing initialization parameters.
        """
        await super().start(frame)
        await self._connect()

    async def stop(self, frame: EndFrame):
        """Stop the Sarvam STT service.

        Args:
            frame: The end frame.
        """
        await super().stop(frame)
        await self._disconnect()

    async def cancel(self, frame: CancelFrame):
        """Cancel the Sarvam STT service.

        Args:
            frame: The cancel frame.
        """
        await super().cancel(frame)
        await self._disconnect()

    async def run_stt(self, audio: bytes):
        """Send audio data to Sarvam for transcription.

        Args:
            audio: Raw audio bytes to transcribe.

        Yields:
            Frame: None (transcription results come via WebSocket callbacks).
        """
        if not self._websocket_connection or self._websocket_connection.state != State.OPEN:
            logger.warning("WebSocket not connected, cannot process audio")
            yield None
            return

        try:
            # Resample audio to 16kHz if needed
            if self.sample_rate != self._target_sample_rate:
                audio = await self._resampler.resample(
                    audio, self.sample_rate, self._target_sample_rate
                )

            # Convert audio bytes to base64 for Sarvam API
            audio_base64 = base64.b64encode(audio).decode("utf-8")

            message = {
                "audio": {
                    "data": audio_base64,
                    "encoding": "audio/wav",
                    "sample_rate": self._target_sample_rate,
                }
            }
            await self._websocket_connection.send(json.dumps(message))

        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed")
            await self.push_error(ErrorFrame("WebSocket connection closed"))
        except Exception as e:
            logger.error(f"Error sending audio to Sarvam: {e}")
            await self.push_error(ErrorFrame(f"Failed to send audio: {e}"))

        yield None

    async def _connect(self):
        """Connect to Sarvam WebSocket API directly."""
        logger.debug("Connecting to Sarvam")

        try:
            # Build WebSocket URL and headers manually
            ws_url = (
                self._client._client_wrapper.get_environment().production
                + "/speech-to-text-translate/ws"
            )

            # Add query parameters
            query_params = {"model": self._model, "vad_signals": "true"}
            query_string = urlencode(query_params)
            ws_url = ws_url + f"?{query_string}"

            # Get headers
            headers = self._client._client_wrapper.get_headers()
            headers["Api-Subscription-Key"] = self._api_key

            # Connect to WebSocket directly
            self._websocket_connection = await websockets.connect(
                ws_url, additional_headers=headers
            )

            # Create the socket client wrapper
            self._websocket = AsyncSpeechToTextTranslateStreamingSocketClient(
                websocket=self._websocket_connection
            )

            # Start listening for messages
            self._listening_task = asyncio.create_task(self._listen_for_messages())

            logger.info(f"Connected to Sarvam successfully with model: {self._model}")

        except websockets.exceptions.InvalidStatusCode as e:
            error_msg = f"Failed to connect to Sarvam: HTTP {e.status_code}"
            if e.status_code == 403:
                error_msg += f" - Access denied. Your API key may not have access to model '{self._model}'. Available models: saaras:v2, saaras:v2.5"
            elif e.status_code == 401:
                error_msg += " - Invalid API key"
            logger.error(error_msg)
            self._websocket = None
            self._websocket_connection = None
            await self.push_error(ErrorFrame(error_msg))
        except Exception as e:
            logger.error(f"Failed to connect to Sarvam: {e}")
            self._websocket = None
            self._websocket_connection = None
            await self.push_error(ErrorFrame(f"Failed to connect to Sarvam: {e}"))

    async def _disconnect(self):
        """Disconnect from Sarvam WebSocket API."""
        if self._listening_task:
            self._listening_task.cancel()
            try:
                await self._listening_task
            except asyncio.CancelledError:
                pass
            self._listening_task = None

        if self._websocket_connection and self._websocket_connection.state == State.OPEN:
            try:
                await self._websocket_connection.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {e}")
            finally:
                logger.debug("Disconnected from Sarvam WebSocket")
                self._websocket_connection = None
                self._websocket = None

    async def _listen_for_messages(self):
        """Listen for messages from Sarvam WebSocket."""
        try:
            while self._websocket_connection and self._websocket_connection.state == State.OPEN:
                try:
                    message = await self._websocket_connection.recv()
                    response = json.loads(message)
                    await self._handle_response(response)

                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error receiving message from Sarvam: {e}")
                    break

        except asyncio.CancelledError:
            logger.debug("Message listening cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in message listener: {e}")
            await self.push_error(ErrorFrame(f"Message listener error: {e}"))

    async def _handle_response(self, response):
        """Handle transcription response from Sarvam.

        Args:
            response: The response object from Sarvam WebSocket.
        """
        logger.debug(f"Received response: {response}")

        try:
            if response["type"] == "error":
                error_msg = response.get("data", {}).get("message", "Unknown error")
                logger.error(f"Sarvam API error: {error_msg}")
                await self.push_error(ErrorFrame(f"Sarvam API error: {error_msg}"))
                # Close connection on error
                await self._disconnect()
                return

            if response["type"] == "events":
                parsed = EventResponse(**response)
                signal = parsed.data.signal_type
                timestamp = parsed.data.occured_at
                logger.debug(f"VAD Signal: {signal}, Occurred at: {timestamp}")

                if signal == VADSignal.START:
                    await self.start_metrics()
                    logger.debug("User started speaking")
                    await self._call_event_handler("on_speech_started")
                elif signal == VADSignal.END:
                    logger.debug("User stopped speaking")
                    await self._call_event_handler("on_speech_ended")

            elif response["type"] == "data":
                await self.stop_ttfb_metrics()
                parsed = TranscriptionResponse(**response)
                transcript = parsed.data.transcript
                language_code = parsed.data.language_code
                if language_code is None:
                    language_code = "hi-IN"
                language = self._map_language_code_to_enum(language_code)

                if transcript and transcript.strip():
                    await self.push_frame(
                        TranscriptionFrame(
                            transcript,
                            self._user_id,
                            time_now_iso8601(),
                            language,
                            result=response,
                        )
                    )

                await self.stop_processing_metrics()

        except Exception as e:
            logger.error(f"Error handling Sarvam response: {e}")
            await self.push_error(ErrorFrame(f"Failed to handle response: {e}"))

    def _map_language_code_to_enum(self, language_code: str) -> Language:
        """Map Sarvam language code (e.g., "hi-IN") to pipecat Language enum."""
        logger.debug(f"Audio language detected as: {language_code}")
        mapping = {
            "bn-IN": Language.BN_IN,
            "gu-IN": Language.GU_IN,
            "hi-IN": Language.HI_IN,
            "kn-IN": Language.KN_IN,
            "ml-IN": Language.ML_IN,
            "mr-IN": Language.MR_IN,
            "ta-IN": Language.TA_IN,
            "te-IN": Language.TE_IN,
            "pa-IN": Language.PA_IN,
            "od-IN": Language.OR_IN,
            "en-US": Language.EN_US,
            "en-IN": Language.EN_IN,
            "as-IN": Language.AS_IN,
        }
        return mapping.get(language_code, Language.HI_IN)

    async def start_metrics(self):
        """Start TTFB and processing metrics collection."""
        await self.start_ttfb_metrics()
        await self.start_processing_metrics()
