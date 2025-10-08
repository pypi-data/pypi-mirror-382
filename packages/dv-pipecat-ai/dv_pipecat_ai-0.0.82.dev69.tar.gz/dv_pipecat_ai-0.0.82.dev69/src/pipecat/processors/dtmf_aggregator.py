import asyncio

from pipecat.frames.frames import (
    BotSpeakingFrame,
    CancelFrame,
    DTMFUpdateSettingsFrame,
    EndFrame,
    Frame,
    InputDTMFFrame,
    StartInterruptionFrame,
    StartUserIdleProcessorFrame,
    StopUserIdleProcessorFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    WaitForDTMFFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.utils.time import time_now_iso8601


class DTMFAggregator(FrameProcessor):
    """Aggregates DTMF frames using idle wait logic.
    The aggregator accumulates digits from incoming InputDTMFFrame instances.
    It flushes the aggregated digits by emitting a TranscriptionFrame when:
      - No new digit arrives within the specified timeout period,
      - The termination digit (“#”) is received, or
      - The number of digits aggregated equals the configured 'digits' value.
    """

    def __init__(
        self,
        timeout: float = 3.0,
        end_on: set[str] = None,
        reset_on: set[str] = None,
        digits: int = None,
        **kwargs,
    ):
        """:param timeout: Idle timeout in seconds before flushing the aggregated digits.
        :param digits: Number of digits to aggregate before flushing.
        """
        super().__init__(**kwargs)
        self._aggregation = ""
        self._idle_timeout = timeout
        self._digits = digits
        self._digit_event = asyncio.Event()
        self._digit_aggregate_task = None
        self._end_on = end_on if end_on else set()
        self._reset_on = reset_on if reset_on else set()
        self._stopped_idle_processor = False

    async def _start_idle_processor(self):
        await self.push_frame(StartUserIdleProcessorFrame(), FrameDirection.UPSTREAM)
        self._stopped_idle_processor = False

    async def _stop_idle_processor(self):
        await self.push_frame(StopUserIdleProcessorFrame(), FrameDirection.UPSTREAM)
        self._stopped_idle_processor = True

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        # Handle DTMF frames.
        await super().process_frame(frame, direction)
        await self.push_frame(frame, direction)
        if isinstance(frame, InputDTMFFrame):
            # Start the digit aggregation task if it's not running yet.
            if self._digit_aggregate_task is None:
                self._digit_aggregate_task = self.create_task(self._digit_agg_handler(direction))

            # Append the incoming digit.
            if frame.button.value in self._reset_on:
                self._aggregation = ""
            elif frame.button.value in self._end_on:
                await self.flush_aggregation(direction)
                self._aggregation = ""
            else:
                self._digit_event.set()
                self._aggregation += frame.button.value

                # Flush if the aggregated digits reach the specified length.
                if self._digits and len(self._aggregation) == self._digits:
                    await self.flush_aggregation(direction)
                    self._aggregation = ""
            if self._stopped_idle_processor:
                await self._start_idle_processor()

        elif isinstance(frame, (EndFrame, CancelFrame)):
            # For EndFrame, flush any pending aggregation and stop the digit aggregation task.
            if self._aggregation:
                await self.flush_aggregation(direction)
            if self._digit_aggregate_task:
                await self._stop_digit_aggregate_task()
        elif isinstance(frame, WaitForDTMFFrame):
            self.logger.debug("Received WaitForDTMFFrame: Waiting for DTMF input")
            if self._digit_aggregate_task is None:
                self._digit_aggregate_task = self.create_task(
                    self._digit_agg_handler(direction, raise_timeout=True)
                )
                self._digit_event.set()
            await self._stop_idle_processor()
        elif isinstance(frame, StartInterruptionFrame):
            self.logger.debug("Received StartInterruptionFrame: Starting idle processor")
            if self._stopped_idle_processor:
                await self._start_idle_processor()
            if self._aggregation:
                await self.flush_aggregation(direction)
        elif isinstance(frame, BotSpeakingFrame):
            if self._digit_aggregate_task is not None:
                self._digit_event.set()
        elif isinstance(frame, DTMFUpdateSettingsFrame):
            await self._update_settings(frame.settings)
            # Don't pass the settings frame downstream

    async def _update_settings(self, settings: dict) -> None:
        """Update DTMF aggregator settings dynamically.
        
        Args:
            settings: Dictionary containing new DTMF settings
                     Supported keys: timeout, digits, end, reset
        """
        settings_changed = False
        
        if "timeout" in settings and settings["timeout"] is not None:
            new_timeout = float(settings["timeout"])
            if new_timeout != self._idle_timeout:
                self.logger.debug(f"Updating DTMF timeout from {self._idle_timeout} to {new_timeout}")
                self._idle_timeout = new_timeout
                settings_changed = True
        
        if "digits" in settings:
            new_digits = settings["digits"]
            if new_digits != self._digits:
                self.logger.debug(f"Updating DTMF digits from {self._digits} to {new_digits}")
                self._digits = new_digits
                settings_changed = True
        
        if "end" in settings:
            # Convert single string to set if needed
            end_value = settings["end"]
            if end_value is None:
                new_end_on = set()
            elif isinstance(end_value, str):
                new_end_on = {end_value} if end_value else set()
            else:
                new_end_on = set(end_value)
            
            if new_end_on != self._end_on:
                self.logger.debug(f"Updating DTMF end_on from {self._end_on} to {new_end_on}")
                self._end_on = new_end_on
                settings_changed = True
        
        if "reset" in settings:
            # Convert single string to set if needed
            reset_value = settings["reset"]
            if reset_value is None:
                new_reset_on = set()
            elif isinstance(reset_value, str):
                new_reset_on = {reset_value} if reset_value else set()
            else:
                new_reset_on = set(reset_value)
            
            if new_reset_on != self._reset_on:
                self.logger.debug(f"Updating DTMF reset_on from {self._reset_on} to {new_reset_on}")
                self._reset_on = new_reset_on
                settings_changed = True
        
        if settings_changed:
            self.logger.info(f"DTMF settings updated successfully")

    async def _digit_agg_handler(self, direction: FrameDirection, raise_timeout=False):
        """Idle task that waits for new DTMF activity. If no new digit is received within
        the timeout period, the current aggregation is flushed.
        """
        while True:
            try:
                # Wait for a new digit signal with a timeout.
                await asyncio.wait_for(self._digit_event.wait(), timeout=self._idle_timeout)
            except asyncio.TimeoutError:
                # No new digit arrived within the timeout period; flush aggregation if non-empty.
                await self.flush_aggregation(direction, raise_timeout)
            finally:
                # Clear the event for the next cycle.
                self._digit_event.clear()

    async def flush_aggregation(self, direction: FrameDirection, raise_timeout=False):
        """Flush the aggregated digits by emitting a TranscriptionFrame downstream."""
        if self._aggregation:
            # Todo: Change to different frame type if we decide to handle it in llm processor separately.
            aggregated_frame = TranscriptionFrame(
                f"User inputted: {self._aggregation}.", "", time_now_iso8601()
            )
            aggregated_frame.metadata["push_aggregation"] = True
            await self.push_frame(StartInterruptionFrame())
            await self.push_frame(aggregated_frame, direction)
            self._aggregation = ""
        elif raise_timeout and self._stopped_idle_processor:
            transcript_frame = TranscriptionFrame(
                "User didn't press any digits on the keyboard.", "", time_now_iso8601()
            )
            transcript_frame.metadata["push_aggregation"] = True
            await self.push_frame(transcript_frame)
            if self._stopped_idle_processor:
                await self._start_idle_processor()

    async def _stop_digit_aggregate_task(self):
        """Cancels the digit aggregation task if it exists."""
        if self._digit_aggregate_task:
            await self.cancel_task(self._digit_aggregate_task)
            self._digit_aggregate_task = None

    async def cleanup(self) -> None:
        """Cleans up resources, ensuring that the digit aggregation task is cancelled."""
        await super().cleanup()
        if self._digit_aggregate_task:
            await self._stop_digit_aggregate_task()
