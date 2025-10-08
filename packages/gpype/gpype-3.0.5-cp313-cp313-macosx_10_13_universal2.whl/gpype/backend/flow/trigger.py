from __future__ import annotations

import numpy as np

from ...common.constants import Constants
from ..core.i_port import IPort
from ..core.io_node import IONode
from ..core.o_port import OPort

#: Default input port identifier
PORT_IN = Constants.Defaults.PORT_IN
#: Default output port identifier
PORT_OUT = Constants.Defaults.PORT_OUT


class Trigger(IONode):
    """Event-triggered data extraction node for BCI applications.

    Monitors trigger events and extracts time-locked data segments around
    trigger occurrences. Maintains a rolling buffer of input data and outputs
    complete data epochs when target trigger values are detected. Commonly
    used in event-related potential (ERP) analysis.
    """

    #: Default pre-trigger window in seconds
    DEFAULT_TIME_PRE = 0.7
    #: Default post-trigger window in seconds
    DEFAULT_TIME_POST = 0.2

    #: Port name for trigger input
    PORT_TRIGGER = "trigger"

    class Configuration(IONode.Configuration):
        """Configuration class for Trigger parameters."""

        class Keys(IONode.Configuration.Keys):
            """Configuration key constants for the Trigger."""

            #: Pre-trigger time configuration key
            TIME_PRE = "time_pre"
            #: Post-trigger time configuration key
            TIME_POST = "time_post"
            #: Target trigger value configuration key
            TARGET = "target"

    def __init__(
        self,
        time_pre: float = None,
        time_post: float = None,
        target: float = None,
        **kwargs,
    ):
        """Initialize the Trigger node with timing and target configurations.

        Args:
            time_pre: Time in seconds before trigger to include in epoch.
                Must be > 0. Defaults to 0.7 seconds.
            time_post: Time in seconds after trigger to include in epoch.
                Must be > 0. Defaults to 0.2 seconds.
            target: Trigger value(s) that cause epoch extraction. Can be
                single value or list. Defaults to [1].
            **kwargs: Additional configuration parameters passed to IONode.

        Raises:
            ValueError: If time_pre or time_post is <= 0.
        """
        # Set default values if not provided
        if time_pre is None:
            time_pre = self.DEFAULT_TIME_PRE
        if time_post is None:
            time_post = self.DEFAULT_TIME_POST
        if target is None:
            target = [1]

        # Ensure target is always a list for consistent handling
        if type(target) is not list:
            target = [target]

        # Validate timing parameters
        if time_pre <= 0:
            raise ValueError("time_pre must be greater than 0.")
        if time_post <= 0:
            raise ValueError("time_post must be greater than 0.")

        # Configure input ports: data port and trigger port
        input_ports = [
            IPort.Configuration(),  # Main data input
            IPort.Configuration(
                name=self.PORT_TRIGGER, timing=Constants.Timing.INHERITED
            ),
        ]

        # Configure output port with asynchronous timing (trigger-dependent)
        output_ports = [OPort.Configuration(timing=Constants.Timing.ASYNC)]

        # Initialize parent IONode with all configurations
        super().__init__(
            time_pre=time_pre,
            time_post=time_post,
            target=target,
            input_ports=input_ports,
            output_ports=output_ports,
            **kwargs,
        )

        # Initialize internal state variables
        self._buf_input = None  # Rolling input data buffer
        self._buf_output = None  # Output buffer (legacy, unused)
        self._frame_size = None  # Total epoch frame size
        self._target = None  # Target trigger values
        self._countdown = None  # List of active countdown timers
        self._samples_pre = None  # Pre-trigger samples count
        self._samples_post = None  # Post-trigger samples count
        self._last_trigger = None  # Last seen trigger value

    def setup(
        self, data: dict[str, np.ndarray], port_context_in: dict[str, dict]
    ) -> dict[str, dict]:
        """Set up the Trigger node and initialize internal buffers.

        Validates input requirements, calculates buffer sizes based on
        sampling rate and timing parameters, and initializes the rolling
        input buffer for data collection.

        Args:
            data: Initial data dictionary for port configuration.
            port_context_in: Input port context with sampling rates, frame
                sizes, and channel counts.

        Returns:
            Output port context with updated frame size and timing
            information for the extracted epochs.

        Raises:
            ValueError: If input frame size is not 1 or sampling rate is
                not provided.
        """
        # Call parent setup to get base output context
        port_context_out = super().setup(data, port_context_in)

        # Validate input frame size requirement for precise timing
        frame_size_in = port_context_in[PORT_IN][Constants.Keys.FRAME_SIZE]
        if frame_size_in != 1:
            raise ValueError("Input frame size must be 1.")

        # Get configuration parameters
        tpre_key = self.Configuration.Keys.TIME_PRE
        tpost_key = self.Configuration.Keys.TIME_POST
        time_pre = self.config[tpre_key]
        time_post = self.config[tpost_key]

        # Get sampling rate for time-to-samples conversion
        sampling_rate = port_context_in[PORT_IN][Constants.Keys.SAMPLING_RATE]
        if sampling_rate is None:
            raise ValueError("Sampling rate must be provided in context.")

        # Convert time windows to sample counts
        self._samples_pre = int(round(time_pre * sampling_rate))
        self._samples_post = int(round(time_post * sampling_rate))
        frame_size_out = self._samples_pre + self._samples_post

        # Update output port context with epoch specifications
        cc_key = Constants.Keys.CHANNEL_COUNT
        fsz_key = Constants.Keys.FRAME_SIZE
        timing_key = OPort.Configuration.Keys.TIMING

        # Get channel count and timing from input context
        channel_count = port_context_out[PORT_OUT][cc_key]
        timing = port_context_out[PORT_OUT][timing_key][PORT_IN]

        # Set output context values
        port_context_out[PORT_OUT][cc_key] = channel_count
        port_context_out[PORT_OUT][fsz_key] = frame_size_out
        port_context_out[PORT_OUT][tpre_key] = time_pre
        port_context_out[PORT_OUT][tpost_key] = time_post
        port_context_out[PORT_OUT][timing_key] = timing

        # Initialize internal buffers and state
        self._buf_input = np.zeros(shape=(frame_size_out, channel_count))
        self._buf_output = []  # Legacy buffer, kept for compatibility
        self._frame_size = frame_size_out
        self._target = self.config[self.Configuration.Keys.TARGET]
        self._countdown = []  # List of active trigger countdowns

        # Initialize last trigger to value outside target range
        self._last_trigger = min(self._target) - 1

        return port_context_out

    def step(self, data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        """Process one frame of data and check for trigger events.

        Updates the rolling input buffer with new data, monitors trigger
        changes, and extracts complete epochs when countdown timers expire.
        Multiple triggers can be active simultaneously.

        Args:
            data: Dictionary containing input data arrays. Must include
                both the main data port and trigger port data.

        Returns:
            Dictionary containing extracted epoch data when a trigger
            countdown completes, None otherwise. Epoch has shape
            (samples_pre + samples_post, channel_count).
        """
        # Update rolling buffer with new data sample
        # Efficiently shift buffer: move all rows up by one position
        self._buf_input[:-1] = self._buf_input[1:]
        self._buf_input[-1] = data[PORT_IN][-1]  # Add newest sample at end

        # Check for trigger state changes
        trigger = data[self.PORT_TRIGGER]
        if trigger != self._last_trigger:
            # New trigger detected - check if it's a target value
            if trigger in self._target:
                # Start new countdown for this trigger event
                self._countdown.append(self._samples_post)
            self._last_trigger = trigger

        # Process all active countdowns
        for i in reversed(range(len(self._countdown))):
            self._countdown[i] -= 1  # Decrement countdown

            # Check if countdown has completed
            if self._countdown[i] <= 0:
                # Remove completed countdown and return epoch data
                self._countdown.pop(i)
                return {PORT_OUT: self._buf_input.copy()}

        # No epochs ready - return None (asynchronous behavior)
        return None
