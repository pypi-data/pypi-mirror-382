from __future__ import annotations

import os
import queue
import threading
from datetime import datetime
from typing import Optional

import ioiocore as ioc
import numpy as np

from ...common.constants import Constants
from ..core.i_node import INode
from ..core.i_port import IPort


class FileWriter(INode):
    """Threaded file writer for real-time data logging to CSV files.

    Implements a file writer that operates in a separate background thread
    to prevent blocking the main signal processing pipeline. Data is queued
    and written asynchronously to maintain real-time performance. Automatically
    adds timestamps to filenames and includes sample indices with channel
    headers in CSV output.
    """

    class Configuration(ioc.INode.Configuration):
        """Configuration class for FileWriter parameters."""

        class Keys(ioc.INode.Configuration.Keys):
            """Configuration keys for file writer settings."""

            #: File name configuration key
            FILE_NAME = "file_name"

    def __init__(
        self,
        file_name: str,
        **kwargs,
    ):
        """Initialize the file writer with specified filename and ports.

        Args:
            file_name: Base filename for data output. A timestamp will be
                automatically appended. Must have .csv extension.
            **kwargs: Additional arguments passed to parent INode class.

        Raises:
            ValueError: If file format is not supported (.csv required).
        """
        # Initialize parent INode with configuration
        INode.__init__(self, file_name=file_name, **kwargs)

        # Initialize threading components for background file operations
        self._file_queue = queue.Queue()  # Thread-safe data queue
        self._stop_event = threading.Event()  # Shutdown coordination
        self._worker_thread = None  # Background file writer thread
        self._file_handle = None  # CSV file handle
        self._sample_counter = 0  # Global sample index counter

    def start(self):
        """Start the file writer and initialize background thread.

        Creates the output file with timestamp, validates the file format,
        and starts the background worker thread for asynchronous writing.

        Raises:
            ValueError: If the file format is not .csv.
            IOError: If the file cannot be created or opened.
        """
        # Get base filename from configuration
        file_name = self.config[self.Configuration.Keys.FILE_NAME]

        # Split filename and extension for timestamp insertion
        name, ext = os.path.splitext(file_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{name}_{timestamp}{ext}"

        # Validate file format - only CSV is supported
        if not file_name.endswith(".csv"):
            raise ValueError(f"Unsupported file format {file_name}.")

        # Open file handle for writing
        self._file_handle = open(file_name, "w")

        # Initialize and start background worker thread
        self._worker_thread = threading.Thread(
            target=self._file_worker, daemon=True
        )
        self._stop_event.clear()  # Reset stop event
        self._worker_thread.start()

        # Initialize header for CSV output
        self._header = ""

        # Call parent start method
        super().start()

    def stop(self):
        """Stop the file writer and clean up resources.

        Signals the background thread to stop, waits for it to finish
        processing remaining data, and properly closes the file handle.
        Ensures all queued data is written before stopping.
        """
        # Signal background thread to stop
        self._stop_event.set()

        # Wait for worker thread to finish processing remaining data
        if self._worker_thread is not None:
            self._worker_thread.join()

        # Close file handle and clean up
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None

        # Call parent stop method
        super().stop()

    def setup(
        self, data: dict[str, np.ndarray], port_context_in: dict[str, dict]
    ) -> dict[str, dict]:
        """Setup method called before processing begins.

        Validates that the file handle is properly initialized and ready
        for writing operations.

        Args:
            data: Dictionary of input data arrays from connected ports.
            port_context_in: Context information from input ports.

        Returns:
            Empty dictionary as this is a sink node with no outputs.

        Raises:
            RuntimeError: If file handle is not initialized (start() not
                called).
        """
        # Verify file handle is initialized
        if not self._file_handle:
            raise RuntimeError("File handle is not initialized.")

        # No output context for sink nodes
        return {}

    def step(self, data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        """Process incoming data by queuing it for background writing.

        Args:
            data: Dictionary containing input data arrays. Uses the default
                input port to retrieve data for writing.

        Returns:
            Empty dictionary as this is a sink node with no outputs.
        """
        # Get data from default input port
        d = data[Constants.Defaults.PORT_IN]

        # Copy data and queue for background writing (thread-safe)
        self._file_queue.put(d.copy())

        # No output data for sink nodes
        return {}

    def _file_worker(self):
        """Background worker thread for asynchronous file writing.

        Runs in a separate thread to handle file I/O operations without
        blocking the main signal processing pipeline. Continuously processes
        data blocks from the queue until stop is signaled. Generates CSV
        headers on first write and maintains global sample counter.
        """
        # Continue processing until stop signaled AND queue is empty
        while not self._stop_event.is_set() or not self._file_queue.empty():
            if not self._file_queue.empty():
                try:
                    # Get next data block from queue (timeout for response)
                    block = self._file_queue.get(timeout=1)

                    # Ensure file handle is still valid
                    if self._file_handle:
                        # Generate CSV header only for first data block
                        if self._sample_counter == 0:
                            header = "Index, "
                            ch_names = [
                                f"Ch{d + 1:02d}" for d in range(block.shape[1])
                            ]
                            header += ", ".join(ch_names)
                        else:
                            header = ""

                        # Generate sample indices for this block
                        start_idx = self._sample_counter
                        end_idx = self._sample_counter + block.shape[0]
                        indices = np.arange(start_idx, end_idx)
                        self._sample_counter += block.shape[0]

                        # Combine indices with data (indices as first column)
                        full_block = np.column_stack((indices, block))

                        # Write to CSV with high precision formatting
                        np.savetxt(
                            self._file_handle,
                            full_block,
                            fmt="%.17g",  # High precision format
                            delimiter=",",
                            header=header,
                            comments="",
                        )  # No comment prefix

                except queue.Empty:
                    # Timeout occurred, continue loop to check stop condition
                    continue
            else:
                # Queue is empty, brief sleep to prevent busy waiting
                import time

                time.sleep(0.01)
                continue
