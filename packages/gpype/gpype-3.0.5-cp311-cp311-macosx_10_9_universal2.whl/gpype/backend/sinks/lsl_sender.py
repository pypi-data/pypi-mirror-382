from __future__ import annotations

from typing import Optional

import ioiocore as ioc
import numpy as np
from pylsl import StreamInfo, StreamOutlet, cf_double64

from ...common.constants import Constants
from ..core.i_node import INode


class LSLSender(INode):
    """Lab Streaming Layer (LSL) sender for real-time data streaming.

    Implements an LSL outlet that streams multi-channel data to the Lab
    Streaming Layer network. Automatically configures the LSL stream based
    on input port context including channel count, sampling rate, and frame
    size. Supports both single-sample and chunk-based streaming modes.
    """

    #: Default LSL stream name for g.Pype data streams
    DEFAULT_STREAM_NAME = "gpype_lsl"

    class Configuration(ioc.INode.Configuration):
        """Configuration class for LSLSender parameters."""

        class Keys(ioc.INode.Configuration.Keys):
            """Configuration keys for LSL sender settings."""

            #: Stream name configuration key
            STREAM_NAME = "stream_name"

    def __init__(self, stream_name: Optional[str] = None, **kwargs):
        """Initialize the LSL sender with specified stream name.

        Args:
            stream_name: Name for the LSL stream. If None, uses the default
                stream name. Used for stream identification on the LSL network.
            **kwargs: Additional arguments passed to parent INode class.
        """
        # Use default stream name if none provided
        if stream_name is None:
            stream_name = LSLSender.DEFAULT_STREAM_NAME

        # Initialize parent INode with configuration
        INode.__init__(self, stream_name=stream_name, **kwargs)

        # Initialize LSL components (created during setup)
        self._lsl_info = None  # LSL stream metadata
        self._lsl_outlet = None  # LSL data outlet
        self._frame_size = None  # Samples per processing frame

    def stop(self):
        """Stop the LSL sender and clean up resources.

        Properly releases LSL resources by setting outlet and info objects
        to None, allowing them to be garbage collected.
        """
        # Release LSL resources
        self._lsl_outlet = None
        self._lsl_info = None

        # Call parent stop method
        super().stop()

    def setup(
        self, data: dict[str, np.ndarray], port_context_in: dict[str, dict]
    ) -> dict[str, dict]:
        """Setup the LSL stream based on input port context.

        Creates LSL StreamInfo and StreamOutlet objects using metadata from
        the input port context. Stream is configured with appropriate
        parameters for EEG data transmission.

        Args:
            data: Dictionary of input data arrays from connected ports.
            port_context_in: Context information from input ports with
                channel count, sampling rate, and frame size.

        Returns:
            Dictionary returned from parent setup method.
        """
        # Extract context information from default input port
        context = port_context_in[Constants.Defaults.PORT_IN]
        channel_count = context[Constants.Keys.CHANNEL_COUNT]
        stream_name = self.config[self.Configuration.Keys.STREAM_NAME]
        sampling_rate = context[Constants.Keys.SAMPLING_RATE]
        self._frame_size = context[Constants.Keys.FRAME_SIZE]

        # Create LSL stream info with EEG configuration
        self._lsl_info = StreamInfo(
            name=stream_name,
            channel_count=channel_count,
            type="EEG",  # Standard LSL type for EEG
            nominal_srate=sampling_rate,
            channel_format=cf_double64,  # Double prec
            source_id=stream_name,
        )  # Unique identifier

        # Create LSL outlet for data transmission
        self._lsl_outlet = StreamOutlet(self._lsl_info)

        # Call parent setup method
        return super().setup(data, port_context_in)

    def step(self, data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        """Process and stream data through LSL outlet.

        Sends incoming data to the LSL network using either single-sample
        or chunk-based transmission depending on frame size. Automatically
        converts numpy arrays to lists for LSL compatibility.

        Args:
            data: Dictionary containing input data arrays. Uses the default
                input port to retrieve data for streaming.

        Returns:
            None as this is a sink node with no output data.
        """
        # Get data from default input port
        d = data[Constants.Defaults.PORT_IN]

        # Stream data if LSL outlet is available
        if self._lsl_outlet:
            if self._frame_size == 1:
                # Single-sample streaming for minimal latency
                self._lsl_outlet.push_sample(d[0].tolist())
            else:
                # Chunk streaming for efficiency with larger frames
                self._lsl_outlet.push_chunk(d.tolist())

        # No output data for sink nodes
        return None
