#!/usr/bin/env python3
"""Base Zenoh subscriber for ROS2 republishing."""

import queue
import threading
import time
from abc import ABC, abstractmethod
from typing import Any

import zenoh

# Import dexcontrol utilities (same as main library uses)
from dexcontrol.utils.os_utils import resolve_key_name
from loguru import logger
from rclpy.node import Node


class BaseZenohROS2Subscriber(ABC):
    """Base class for Zenoh subscribers that republish data to ROS2.

    This class provides the foundation for creating Zenoh subscribers that
    automatically convert and republish data to ROS2 topics. It handles:
    - Zenoh topic subscription with proper key resolution
    - Thread-safe data handling
    - Error isolation (ROS2 failures don't affect Zenoh)
    - Automatic reconnection and lifecycle management

    Attributes:
        zenoh_topic: The resolved Zenoh topic name
        ros2_topic: The ROS2 topic name for publishing
        active: Whether the subscriber is receiving data
        frame_id: ROS2 frame ID for messages
    """

    def __init__(
        self,
        zenoh_topic: str,
        ros2_topic: str,
        zenoh_session: zenoh.Session,
        ros2_node: Node,
        frame_id: str = "",
        enable_fps_tracking: bool = False,
        fps_log_interval: int = 100,
        max_workers: int = 2,  # Deprecated: kept for backward compatibility
        queue_size: int = 2,
    ) -> None:
        """Initialize the base Zenoh-ROS2 subscriber.

        Args:
            zenoh_topic: Raw Zenoh topic name (will be resolved using dexcontrol utils)
            ros2_topic: ROS2 topic name for publishing
            zenoh_session: Active Zenoh session
            ros2_node: ROS2 node for publishing
            frame_id: Frame ID for ROS2 messages
            enable_fps_tracking: Whether to track and log FPS metrics
            fps_log_interval: Number of messages between FPS calculations
            max_workers: (Deprecated) Kept for backward compatibility, use queue_size instead
            queue_size: Maximum queue size for buffering samples (small = low latency)
        """
        self.zenoh_topic = resolve_key_name(zenoh_topic)  # Use dexcontrol resolution
        self.ros2_topic = ros2_topic
        self.frame_id = frame_id
        self.zenoh_session = zenoh_session
        self.ros2_node = ros2_node

        # State tracking
        self._active = False
        self._data_lock = threading.RLock()
        self._last_data_time: float | None = None
        self._subscriber: zenoh.Subscriber | None = None
        self._ros2_publisher: Any | None = None

        # FPS tracking
        self._enable_fps_tracking = enable_fps_tracking
        self._fps_log_interval = fps_log_interval
        self._frame_count = 0
        self._fps = 0.0
        self._last_fps_time = time.time()

        # Congestion tracking
        self._dropped_frame_count = 0
        self._processed_frame_count = 0
        self._last_congestion_warning_time = 0.0

        # Queue-based processing (single consumer thread for ordering)
        self._sample_queue = queue.Queue(maxsize=queue_size)
        self._queue_size = queue_size
        self._shutdown_requested = False

        # Single consumer thread for sequential processing (preserves ordering)
        self._consumer_thread = threading.Thread(
            target=self._consume_samples,
            daemon=True,
            name=f"consumer_{self.zenoh_topic.replace('/', '_')}",
        )
        self._consumer_thread.start()

        # Initialize subscriber and publisher
        self._initialize()

        logger.info(
            f"Initialized Zenoh-ROS2 bridge: {self.zenoh_topic} → {self.ros2_topic} "
            f"(queue_size={queue_size})"
        )

    def _initialize(self) -> None:
        """Initialize Zenoh subscriber and ROS2 publisher."""
        try:
            # Create ROS2 publisher (implemented by subclasses)
            self._ros2_publisher = self._create_ros2_publisher()

            # Create Zenoh subscriber
            self._subscriber = self.zenoh_session.declare_subscriber(
                self.zenoh_topic, self._zenoh_data_handler
            )

            logger.info(f"Created bridge: {self.zenoh_topic} → {self.ros2_topic}")

        except Exception as e:
            logger.error(f"Failed to initialize subscriber for {self.zenoh_topic}: {e}")
            self.shutdown()

    @abstractmethod
    def _create_ros2_publisher(self):
        """Create the appropriate ROS2 publisher for this subscriber type.

        Must be implemented by subclasses to create the correct publisher
        type (e.g., Image, Imu, PointCloud2, etc.).

        Returns:
            ROS2 publisher instance
        """
        pass

    @abstractmethod
    def _convert_and_publish(self, sample: zenoh.Sample) -> None:
        """Convert Zenoh data to ROS2 message and publish.

        Must be implemented by subclasses to handle the specific data
        conversion for their message type.

        Args:
            sample: Zenoh sample containing the data to convert
        """
        pass

    def _zenoh_data_handler(self, sample: zenoh.Sample) -> None:
        """Handle incoming Zenoh data - fast handler that enqueues to consumer thread.

        This minimal handler:
        1. Updates freshness tracking (fast)
        2. Enqueues sample for processing (releases GIL quickly)
        3. Drops oldest frame if queue is full (maintains low latency)

        Args:
            sample: Zenoh sample containing sensor data
        """
        # Update data freshness (minimal GIL time)
        with self._data_lock:
            self._last_data_time = time.monotonic()
            self._active = True

        # Enqueue sample for processing (non-blocking)
        if not self._shutdown_requested:
            try:
                # Non-blocking put - fails immediately if queue is full
                self._sample_queue.put_nowait(sample)
            except queue.Full:
                # Queue full = processing can't keep up with incoming rate
                # Drop OLDEST frame and add newest (keep most recent data)
                try:
                    self._sample_queue.get_nowait()  # Remove oldest
                    self._sample_queue.put_nowait(sample)  # Add newest

                    # Track dropped frames
                    self._dropped_frame_count += 1

                    # Throttled warning (every 5 seconds max)
                    current_time = time.time()
                    if current_time - self._last_congestion_warning_time >= 5.0:
                        logger.warning(
                            f"{self.zenoh_topic}: Queue congestion detected - "
                            f"dropped {self._dropped_frame_count} frames total. "
                            f"Processing can't keep up with incoming rate."
                        )
                        self._last_congestion_warning_time = current_time
                except Exception as e:
                    # Race condition or other error - just drop this frame
                    logger.debug(f"Failed to drop oldest frame: {e}")

    def _consume_samples(self) -> None:
        """Consumer thread that processes samples sequentially from queue.

        This method runs in a dedicated thread and:
        1. Pulls samples from queue (blocking wait)
        2. Processes them one at a time (preserves ordering)
        3. Handles errors without breaking the pipeline
        4. Updates metrics

        Single-threaded processing ensures temporal ordering is maintained.
        """
        logger.debug(f"Consumer thread started for {self.zenoh_topic}")

        while not self._shutdown_requested:
            try:
                # Wait for next sample with timeout (allows checking shutdown flag)
                sample = self._sample_queue.get(timeout=0.1)

                try:
                    # Convert and publish to ROS2 (heavy processing)
                    self._convert_and_publish(sample)
                    self._processed_frame_count += 1
                    self._update_fps_metrics()
                except Exception as e:
                    # Error isolation: processing failures don't break pipeline
                    logger.error(f"Failed to process {self.zenoh_topic}: {e}")
                finally:
                    # Mark task as done
                    self._sample_queue.task_done()

            except queue.Empty:
                # No samples available, continue loop to check shutdown flag
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error in consumer thread for {self.zenoh_topic}: {e}"
                )

        logger.debug(f"Consumer thread stopped for {self.zenoh_topic}")

    def _update_fps_metrics(self) -> None:
        """Update FPS tracking metrics."""
        self._frame_count += 1
        current_time = time.time()

        # Always update FPS for real-time monitoring
        elapsed = current_time - self._last_fps_time
        if elapsed >= 1.0:  # Update FPS every second minimum
            self._fps = self._frame_count / elapsed
            self._frame_count = 0
            self._last_fps_time = current_time

    def is_active(self) -> bool:
        """Check if the subscriber is actively receiving data.

        Returns:
            True if data has been received recently, False otherwise
        """
        with self._data_lock:
            return self._active

    def is_data_fresh(self, max_age_seconds: float = 1.0) -> bool:
        """Check if the most recent data is fresh.

        Args:
            max_age_seconds: Maximum age for data to be considered fresh

        Returns:
            True if data is fresh, False otherwise
        """
        with self._data_lock:
            if self._last_data_time is None:
                return False

            current_time = time.monotonic()
            age = current_time - self._last_data_time
            return age <= max_age_seconds

    def get_time_since_last_data(self) -> float | None:
        """Get time elapsed since last data was received.

        Returns:
            Time in seconds since last data, or None if no data received
        """
        with self._data_lock:
            if self._last_data_time is None:
                return None

            current_time = time.monotonic()
            return current_time - self._last_data_time

    def wait_for_active(self, timeout: float = 5.0) -> bool:
        """Wait for the subscriber to start receiving data.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if subscriber becomes active within timeout, False otherwise
        """
        start_time = time.monotonic()
        check_interval = min(0.05, timeout / 10)

        while True:
            if self.is_active():
                logger.info(f"Bridge {self.zenoh_topic}→{self.ros2_topic} is active")
                return True

            elapsed = time.monotonic() - start_time
            if elapsed >= timeout:
                logger.warning(
                    f"Bridge {self.zenoh_topic}→{self.ros2_topic} not active after {timeout}s"
                )
                return False

            sleep_time = min(check_interval, timeout - elapsed)
            time.sleep(sleep_time)

    def shutdown(self) -> None:
        """Shutdown the subscriber and release resources."""
        logger.info(f"Shutting down bridge: {self.zenoh_topic} → {self.ros2_topic}")

        # Mark as inactive and request shutdown
        with self._data_lock:
            self._active = False
        self._shutdown_requested = True

        # Shutdown Zenoh subscriber first (stop new data)
        if self._subscriber:
            try:
                self._subscriber.undeclare()
                logger.debug(f"Undeclared Zenoh subscriber for {self.zenoh_topic}")
            except Exception as e:
                error_msg = str(e).lower()
                if not ("undeclared" in error_msg or "closed" in error_msg):
                    logger.warning(f"Error undeclaring Zenoh subscriber: {e}")

        # Wait for consumer thread to finish processing queue
        if hasattr(self, "_consumer_thread") and self._consumer_thread.is_alive():
            try:
                logger.debug(
                    f"Waiting for consumer thread to finish for {self.zenoh_topic}"
                )
                self._consumer_thread.join(timeout=2.0)
                if self._consumer_thread.is_alive():
                    logger.warning(
                        f"Consumer thread did not finish in time for {self.zenoh_topic}"
                    )
                else:
                    logger.debug(f"Consumer thread finished for {self.zenoh_topic}")
            except Exception as e:
                logger.warning(f"Error waiting for consumer thread: {e}")

        # Log final statistics
        if self._processed_frame_count > 0 or self._dropped_frame_count > 0:
            drop_rate = (
                self._dropped_frame_count
                / (self._processed_frame_count + self._dropped_frame_count)
                * 100
            )
            logger.info(
                f"Bridge {self.zenoh_topic} stats: "
                f"processed={self._processed_frame_count}, "
                f"dropped={self._dropped_frame_count}, "
                f"drop_rate={drop_rate:.2f}%"
            )

        # ROS2 publishers are managed by the node, no explicit cleanup needed
        logger.info(f"Bridge shutdown complete: {self.zenoh_topic} → {self.ros2_topic}")

    @property
    def fps(self) -> float:
        """Get current FPS measurement.

        Returns:
            Current frames per second
        """
        return self._fps

    @property
    def message_count(self) -> int:
        """Get total number of messages processed.

        Returns:
            Total message count
        """
        return self._frame_count

    def get_health_metrics(self) -> dict[str, Any]:
        """Get subscriber health and performance metrics.

        Returns:
            Dictionary with health metrics including:
            - fps: Current frames per second
            - processed_frames: Total frames successfully processed
            - dropped_frames: Total frames dropped due to congestion
            - drop_rate: Percentage of frames dropped (0-100)
            - queue_size: Current number of samples in queue
            - queue_capacity: Maximum queue size
            - active: Whether subscriber is receiving data
        """
        total_frames = self._processed_frame_count + self._dropped_frame_count
        drop_rate = (
            (self._dropped_frame_count / total_frames * 100)
            if total_frames > 0
            else 0.0
        )

        return {
            "fps": self.fps,
            "processed_frames": self._processed_frame_count,
            "dropped_frames": self._dropped_frame_count,
            "drop_rate": drop_rate,
            "queue_size": self._sample_queue.qsize(),
            "queue_capacity": self._queue_size,
            "active": self.is_active(),
            "zenoh_topic": self.zenoh_topic,
            "ros2_topic": self.ros2_topic,
        }
