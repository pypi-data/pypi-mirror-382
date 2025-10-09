#!/usr/bin/env python3
"""Camera-specific Zenoh subscriber for ROS2 republishing."""

from typing import Any

import zenoh
from loguru import logger
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image

from ..converters.camera_converter import CameraConverter
from ..converters.compressed_camera_converter import CompressedCameraConverter
from .base_subscriber import BaseZenohROS2Subscriber


class CameraZenohSubscriber(BaseZenohROS2Subscriber):
    """Zenoh subscriber for camera data that republishes to ROS2 Image topics.

    This subscriber handles camera data (RGB or depth) from Zenoh topics and
    converts them to ROS2 sensor_msgs/Image messages. It uses dexcomm's
    decoding functions to maintain compatibility with the main dexcontrol library.

    Supported stream types:
    - RGB cameras (left_rgb, right_rgb, etc.)
    - Depth cameras (depth)

    The subscriber automatically detects stream type from the topic name and
    configures appropriate encoding and conversion parameters.
    """

    def __init__(
        self,
        zenoh_topic: str,
        ros2_topic: str,
        zenoh_session: zenoh.Session,
        ros2_node: Node,
        frame_id: str = "camera_link",
        queue_size: int = 2,
        enable_fps_tracking: bool = False,
        fps_log_interval: int = 100,
        compressed: bool = True,
        compression_format: str = "jpeg",
        max_workers: int = 6,  # Deprecated: kept for backward compatibility
    ) -> None:
        """Initialize the camera subscriber.

        Args:
            zenoh_topic: Raw Zenoh topic name (e.g., "camera/head/left_rgb")
            ros2_topic: ROS2 topic name (e.g., "/head_camera/left/image")
            zenoh_session: Active Zenoh session
            ros2_node: ROS2 node for publishing
            frame_id: ROS2 frame ID for the camera
            queue_size: Sample queue size for processing
            enable_fps_tracking: Whether to track and log FPS
            fps_log_interval: Number of messages between FPS logs
            compressed: If True, publish CompressedImage (faster), if False publish raw Image
            compression_format: Format for compressed images ("jpeg" or "png")
            max_workers: (Deprecated) Kept for backward compatibility, use queue_size instead
        """
        self.compressed = compressed
        self.compression_format = compression_format

        # Detect stream type from topic name
        self.stream_type = self._detect_stream_type(zenoh_topic)

        # Create appropriate converter (compressed or raw)
        self.converter = self._create_converter(self.stream_type, frame_id)

        # Initialize base subscriber
        super().__init__(
            zenoh_topic=zenoh_topic,
            ros2_topic=ros2_topic,
            zenoh_session=zenoh_session,
            ros2_node=ros2_node,
            frame_id=frame_id,
            enable_fps_tracking=enable_fps_tracking,
            fps_log_interval=fps_log_interval,
            queue_size=queue_size,
        )

        logger.info(
            f"Camera subscriber initialized: {self.stream_type} "
            f"{self.zenoh_topic} → {self.ros2_topic}"
        )

    def _detect_stream_type(self, zenoh_topic: str) -> str:
        """Detect camera stream type from topic name.

        Args:
            zenoh_topic: Zenoh topic name

        Returns:
            Stream type ("rgb" or "depth")
        """
        topic_lower = zenoh_topic.lower()

        if "depth" in topic_lower:
            return "depth"
        elif any(rgb_type in topic_lower for rgb_type in ["rgb", "left", "right"]):
            return "rgb"
        else:
            # Default to RGB for unknown topics
            logger.warning(
                f"Could not detect stream type from {zenoh_topic}, defaulting to RGB"
            )
            return "rgb"

    def _create_converter(self, stream_type: str, frame_id: str):
        """Create appropriate converter for the stream type.

        Args:
            stream_type: Type of camera stream
            frame_id: ROS2 frame ID

        Returns:
            Configured camera converter (compressed or raw)
        """
        if self.compressed:
            # Force correct compression format based on data type
            if stream_type == "depth":
                # Depth MUST use PNG (lossless) - never allow JPEG (lossy) for depth data
                compression_format = "png"
                if self.compression_format != "png":
                    logger.warning(
                        f"Forcing depth compression from '{self.compression_format}' to 'png' (depth requires lossless compression)"
                    )
            else:
                # RGB uses JPEG for efficient compression
                compression_format = self.compression_format

            # Create compressed converter - it will validate data compatibility at runtime
            return CompressedCameraConverter(stream_type, compression_format, frame_id)
        else:
            # Use raw converter for decompressed image publishing
            if stream_type == "depth":
                return CameraConverter("depth", "32FC1", frame_id)
            else:  # rgb
                return CameraConverter("rgb", "rgb8", frame_id)

    def _create_ros2_publisher(self) -> Any:
        """Create ROS2 publisher with configured QoS profile.

        Returns:
            ROS2 Image or CompressedImage publisher with the specified QoS profile
        """
        # Use sensor data QoS profile
        qos = qos_profile_sensor_data

        # Choose message type based on compression setting
        if self.compressed:
            message_type = CompressedImage
            if self.stream_type == "depth":
                topic_suffix = (
                    "/compressedDepth"
                    if not self.ros2_topic.endswith("/compressedDepth")
                    else ""
                )
                topic = self.ros2_topic + topic_suffix
                logger.info(
                    f"Creating compressed depth publisher ({self.compression_format}) with sensor data QoS"
                )
            else:  # rgb
                topic_suffix = (
                    "/compressed" if not self.ros2_topic.endswith("/compressed") else ""
                )
                topic = self.ros2_topic + topic_suffix
                logger.info(
                    f"Creating compressed camera publisher ({self.compression_format}) with sensor data QoS"
                )
        else:
            message_type = Image
            topic = self.ros2_topic
            logger.info("Creating raw camera publisher with sensor data QoS")

        return self.ros2_node.create_publisher(message_type, topic, qos)

    def _convert_and_publish(self, sample: zenoh.Sample) -> None:
        """Convert Zenoh camera data to ROS2 Image and publish.

        Args:
            sample: Zenoh sample containing camera data
        """
        try:
            # Convert using the configured converter
            ros_image = self.converter.convert(sample)

            # Validate the converted data
            if not self._validate_ros_message(ros_image):
                logger.warning(f"Invalid ROS message generated from {self.zenoh_topic}")
                return

            # Publish to ROS2
            if self._ros2_publisher is not None:
                self._ros2_publisher.publish(ros_image)
            else:
                logger.warning("ROS2 publisher not initialized")

        except Exception as e:
            # Re-raise to let base class handle error logging
            raise RuntimeError(f"Camera conversion failed: {e}") from e

    def _validate_ros_message(self, ros_image) -> bool:
        """Validate ROS2 Image/CompressedImage message before publishing.

        Args:
            ros_image: ROS2 Image or CompressedImage message to validate

        Returns:
            True if message is valid, False otherwise
        """
        if ros_image is None:
            logger.warning("ROS Image message is None")
            return False

        if len(ros_image.data) == 0:
            logger.warning("Empty image data")
            return False

        # Handle both Image and CompressedImage types
        if hasattr(ros_image, "width") and hasattr(ros_image, "height"):
            # Regular Image message
            if ros_image.width == 0 or ros_image.height == 0:
                logger.warning(
                    f"Invalid image dimensions: {ros_image.width}x{ros_image.height}"
                )
                return False

            # Check data size matches expected dimensions for raw images
            if self.stream_type == "rgb":
                expected_size = ros_image.width * ros_image.height * 3  # 3 channels
            else:  # depth
                expected_size = (
                    ros_image.width * ros_image.height * 4
                )  # 4 bytes per float32

            if len(ros_image.data) != expected_size:
                logger.warning(
                    f"Image data size mismatch: expected {expected_size}, got {len(ros_image.data)}"
                )
                return False

        elif hasattr(ros_image, "format"):
            # CompressedImage message
            if not ros_image.format:
                logger.warning("CompressedImage has no format specified")
                return False

            # Basic validation for compressed data
            if len(ros_image.data) < 10:
                logger.warning("CompressedImage data too small")
                return False

        return True

    def get_stream_info(self) -> dict[str, Any]:
        """Get information about the camera stream.

        Returns:
            Dictionary with stream information
        """
        return {
            "stream_type": self.stream_type,
            "zenoh_topic": self.zenoh_topic,
            "ros2_topic": self.ros2_topic,
            "frame_id": self.frame_id,
            "encoding": self.converter.encoding
            if hasattr(self.converter, "encoding")
            else None,
            "format": self.converter.format
            if hasattr(self.converter, "format")
            else "raw",
            "active": self.is_active(),
            "fps": self.fps,
        }

    def __str__(self) -> str:
        """String representation of the subscriber."""
        return f"CameraZenohSubscriber({self.stream_type}: {self.zenoh_topic} → {self.ros2_topic})"
