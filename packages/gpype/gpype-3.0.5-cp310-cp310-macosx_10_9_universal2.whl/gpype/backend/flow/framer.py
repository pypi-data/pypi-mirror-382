from __future__ import annotations

import numpy as np

from ...common.constants import Constants
from ..core.io_node import IONode

#: Default input port identifier
PORT_IN = Constants.Defaults.PORT_IN
#: Default output port identifier
PORT_OUT = Constants.Defaults.PORT_OUT


class Framer(IONode):
    """Frame aggregation node for combining single samples into frames.

    Collects individual samples (frame size = 1) and aggregates them into
    larger frames of a specified size. Maintains an internal buffer that
    accumulates samples until a complete frame is assembled, then outputs
    the entire frame. Useful for converting sample-by-sample streams into
    frame-based processing.
    """

    # Type annotation for the internal buffer
    _buf: np.ndarray

    class Configuration(IONode.Configuration):
        """Configuration class for Framer parameters."""

        class Keys(IONode.Configuration.Keys):
            """Configuration key constants for the Framer."""

            #: Frame size configuration key
            FRAME_SIZE = Constants.Keys.FRAME_SIZE

    def __init__(self, frame_size: int = None, **kwargs):
        """Initialize the Framer node.

        Args:
            frame_size: Size of output frames to generate. Must be a positive
                integer. Defaults to 1 if None.
            **kwargs: Additional configuration parameters passed to IONode.

        Raises:
            ValueError: If frame_size is not an integer or is less than 1.
        """
        # Validate and set default frame size
        if frame_size is None:
            frame_size = 1
        if not isinstance(frame_size, int):
            raise ValueError("frame_size must be integer.")
        if frame_size < 1:
            raise ValueError("frame_size must be greater or equal 1.")

        # Initialize parent IONode with frame configuration
        # Set decimation_factor = frame_size to output every frame_size steps
        super().__init__(
            frame_size=frame_size, decimation_factor=frame_size, **kwargs
        )

        # Initialize internal buffer (will be allocated in setup())
        self._buf = None

    def setup(
        self, data: dict[str, np.ndarray], port_context_in: dict[str, dict]
    ) -> dict[str, dict]:
        """Set up the Framer node and allocate the internal buffer.

        Validates input port configuration and initializes the internal buffer
        based on output frame size and channel count. Input must have
        frame_size = 1 for proper single-sample aggregation.

        Args:
            data: Initial data dictionary for port configuration.
            port_context_in: Input port context with frame size and channel
                count specifications.

        Returns:
            Output port context with updated frame size information.

        Raises:
            ValueError: If input frame size is not 1.
        """
        # Initialize parent setup and get output port context
        port_context_out = super().setup(data, port_context_in)

        # Validate input frame size - must be 1 for single-sample processing
        frame_size_in = port_context_in[PORT_IN][Constants.Keys.FRAME_SIZE]
        if frame_size_in != 1:
            raise ValueError("Input frame size must be 1.")

        # Get configuration for output frame setup
        frame_size_out = self.config[self.Configuration.Keys.FRAME_SIZE]
        channel_count = port_context_out[PORT_OUT][
            Constants.Keys.CHANNEL_COUNT
        ]

        # Update output port context with new frame size
        port_context_out[PORT_OUT][Constants.Keys.FRAME_SIZE] = frame_size_out

        # Allocate internal buffer for frame assembly
        self._buf = np.zeros(shape=(frame_size_out, channel_count))
        self._frame_size = frame_size_out

        return port_context_out

    def step(self, data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        """Process one sample and add it to the internal frame buffer.

        Takes a single sample from input and stores it in the buffer. When a
        complete frame has been assembled (every frame_size samples), outputs
        the complete frame.

        Args:
            data: Input data dictionary containing a single sample with
                PORT_IN key. Sample should have shape (1, channels).

        Returns:
            Output data dictionary with PORT_OUT key containing the complete
            frame when ready, or None if frame is not complete.
        """
        # Calculate buffer position using sample counter
        buf_idx = self.get_counter() % self._frame_size

        # Store the current sample in the buffer at the correct position
        # Take the last sample from input (should be shape (1, channels))
        self._buf[buf_idx, :] = data[PORT_IN][-1:, :]

        # Check if frame is complete (every frame_size samples)
        if self.is_decimation_step():
            # Frame is complete, return the assembled frame
            return {PORT_OUT: self._buf}
        else:
            # Frame not complete yet, return None
            return None
