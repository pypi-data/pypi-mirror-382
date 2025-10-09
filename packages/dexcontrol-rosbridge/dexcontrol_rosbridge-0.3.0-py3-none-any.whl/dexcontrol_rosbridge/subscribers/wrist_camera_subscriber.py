#!/usr/bin/env python3
"""Wrist camera-specific Zenoh subscriber for ROS2 republishing.

This subscriber handles ZEDx One wrist camera data for manipulation tasks.
"""

from typing import Any

import zenoh
from loguru import logger
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image

from ..converters.compressed_camera_converter import CompressedCameraConverter
from ..converters.wrist_camera_converter import WristCameraConverter
from .base_subscriber import BaseZenohROS2Subscriber


class WristCameraZenohSubscriber(BaseZenohROS2Subscriber):
    """Zenoh subscriber for wrist camera data that republishes to ROS2 Image topics.

    This subscriber handles wrist camera RGB data from Zenoh topics and
    converts them to ROS2 sensor_msgs/Image messages. It's specialized for
    ZEDx One wrist cameras used in manipulation tasks.

    The wrist cameras provide visual feedback for:
    - Visual servoing during manipulation
    - Object detection and pose estimation
    - Grasp verification and monitoring
    - Tool use observation

    Key features:
    - Only RGB streams (no depth data)
    - Optimized for low-latency visual feedback
    - Support for both left and right wrist cameras
    """

    def __init__(
        self,
        zenoh_topic: str,
        ros2_topic: str,
        zenoh_session: zenoh.Session,
        ros2_node: Node,
        side: str = None,
        frame_id: str = None,
        queue_size: int = 2,
        enable_fps_tracking: bool = False,
        fps_log_interval: int = 100,
        compressed: bool = True,
        compression_format: str = "jpeg",
        max_workers: int = 4,  # Deprecated: kept for backward compatibility
    ) -> None:
        """Initialize the wrist camera subscriber.

        Args:
            zenoh_topic: Raw Zenoh topic name (e.g., "camera/left_wrist/rgb")
            ros2_topic: ROS2 topic name (e.g., "/left_wrist_camera/image")
            zenoh_session: Active Zenoh session
            ros2_node: ROS2 node for publishing
            side: Which wrist ("left" or "right"). Auto-detected from topic if None
            frame_id: ROS2 frame ID. Auto-set based on side if None
            queue_size: Sample queue size for processing
            enable_fps_tracking: Whether to track and log FPS
            fps_log_interval: Number of messages between FPS logs
            compressed: If True, publish CompressedImage, if False publish raw Image
            compression_format: Format for compressed images ("jpeg" recommended)
            max_workers: (Deprecated) Kept for backward compatibility, use queue_size instead
        """
        self.compressed = compressed
        self.compression_format = compression_format

        # Auto-detect side from topic if not provided
        if side is None:
            side = self._detect_wrist_side(zenoh_topic)

        if side not in ["left", "right"]:
            raise ValueError(f"Invalid wrist side: {side}. Must be 'left' or 'right'")

        self.side = side

        # Auto-set frame_id based on side if not provided
        if frame_id is None:
            frame_id = f"{side}_wrist_camera_link"

        # Create appropriate converter
        self.converter = self._create_wrist_converter(side, frame_id)

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
            f"{side.title()} wrist camera subscriber initialized: "
            f"{self.zenoh_topic} → {self.ros2_topic}"
        )

    def _detect_wrist_side(self, zenoh_topic: str) -> str:
        """Auto-detect which wrist camera from topic name.

        Args:
            zenoh_topic: Zenoh topic name

        Returns:
            "left" or "right"
        """
        topic_lower = zenoh_topic.lower()

        if "left" in topic_lower:
            return "left"
        elif "right" in topic_lower:
            return "right"
        else:
            # Default to left if cannot detect
            logger.warning(
                f"Could not detect wrist side from topic '{zenoh_topic}', "
                f"defaulting to left. Please specify side explicitly."
            )
            return "left"

    def _create_wrist_converter(self, side: str, frame_id: str):
        """Create appropriate converter for wrist camera.

        Args:
            side: Which wrist camera ("left" or "right")
            frame_id: ROS2 frame ID

        Returns:
            Configured wrist camera converter
        """
        if self.compressed:
            # Use compressed converter for efficiency
            # Wrist cameras are always RGB, never depth
            return CompressedCameraConverter(
                stream_type="rgb", format=self.compression_format, frame_id=frame_id
            )
        else:
            # Use specialized wrist camera converter for raw images
            return WristCameraConverter(side=side, encoding="rgb8", frame_id=frame_id)

    def _create_ros2_publisher(self) -> Any:
        """Create ROS2 publisher with sensor data QoS profile.

        Returns:
            ROS2 Image or CompressedImage publisher
        """
        # Use sensor data QoS profile for real-time performance
        qos = qos_profile_sensor_data

        # Choose message type based on compression setting
        if self.compressed:
            message_type = CompressedImage
            # Add compressed suffix if not already present
            topic_suffix = (
                "/compressed" if not self.ros2_topic.endswith("/compressed") else ""
            )
            topic = self.ros2_topic + topic_suffix
            logger.info(
                f"Creating compressed {self.side} wrist camera publisher "
                f"({self.compression_format}) with sensor data QoS"
            )
        else:
            message_type = Image
            topic = self.ros2_topic
            logger.info(
                f"Creating raw {self.side} wrist camera publisher with sensor data QoS"
            )

        return self.ros2_node.create_publisher(message_type, topic, qos)

    def _convert_and_publish(self, sample: zenoh.Sample) -> None:
        """Convert Zenoh wrist camera data to ROS2 Image and publish.

        Args:
            sample: Zenoh sample containing wrist camera RGB data
        """
        try:
            # Convert using the configured converter
            ros_image = self.converter.convert(sample)

            # Validate the converted data
            if not self._validate_ros_message(ros_image):
                logger.warning(f"Invalid ROS message from {self.side} wrist camera")
                return

            # Publish to ROS2
            if self._ros2_publisher is not None:
                self._ros2_publisher.publish(ros_image)
            else:
                logger.warning(
                    f"{self.side.title()} wrist camera publisher not initialized"
                )

        except Exception as e:
            # Re-raise to let base class handle error logging
            raise RuntimeError(
                f"{self.side.title()} wrist camera conversion failed: {e}"
            ) from e

    def _validate_ros_message(self, ros_image) -> bool:
        """Validate ROS2 Image/CompressedImage message before publishing.

        Args:
            ros_image: ROS2 message to validate

        Returns:
            True if message is valid, False otherwise
        """
        if ros_image is None:
            logger.warning(f"{self.side.title()} wrist camera message is None")
            return False

        if len(ros_image.data) == 0:
            logger.warning(f"Empty {self.side} wrist camera data")
            return False

        # Handle both Image and CompressedImage types
        if hasattr(ros_image, "width") and hasattr(ros_image, "height"):
            # Regular Image message
            if ros_image.width == 0 or ros_image.height == 0:
                logger.warning(
                    f"Invalid {self.side} wrist camera dimensions: "
                    f"{ros_image.width}x{ros_image.height}"
                )
                return False

            # Check expected data size for RGB image
            expected_size = ros_image.width * ros_image.height * 3  # RGB = 3 channels
            if len(ros_image.data) != expected_size:
                logger.warning(
                    f"{self.side.title()} wrist camera data size mismatch: "
                    f"expected {expected_size}, got {len(ros_image.data)}"
                )
                return False

        elif hasattr(ros_image, "format"):
            # CompressedImage message
            if not ros_image.format:
                logger.warning(
                    f"{self.side.title()} wrist CompressedImage has no format"
                )
                return False

            # Basic validation for compressed data
            if len(ros_image.data) < 100:  # Minimum reasonable size
                logger.warning(
                    f"{self.side.title()} wrist CompressedImage data too small"
                )
                return False

        return True

    def get_wrist_camera_info(self) -> dict[str, Any]:
        """Get information about the wrist camera stream.

        Returns:
            Dictionary with wrist camera stream information
        """
        info = {
            "side": self.side,
            "zenoh_topic": self.zenoh_topic,
            "ros2_topic": self.ros2_topic,
            "frame_id": self.frame_id,
            "compressed": self.compressed,
            "active": self.is_active(),
            "fps": self.fps,
        }

        if self.compressed:
            info["compression_format"] = self.compression_format
        else:
            info["encoding"] = (
                self.converter.encoding
                if hasattr(self.converter, "encoding")
                else "rgb8"
            )

        return info

    def __str__(self) -> str:
        """String representation of the subscriber."""
        return f"WristCameraZenohSubscriber({self.side}: {self.zenoh_topic} → {self.ros2_topic})"
