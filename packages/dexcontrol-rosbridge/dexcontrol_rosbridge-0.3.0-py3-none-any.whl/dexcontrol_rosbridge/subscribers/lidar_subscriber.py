#!/usr/bin/env python3
"""LIDAR-specific Zenoh subscriber for ROS2 republishing."""

from typing import Any

import zenoh
from loguru import logger
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2

from ..converters.lidar_converter import LidarConverter
from .base_subscriber import BaseZenohROS2Subscriber


class LidarZenohSubscriber(BaseZenohROS2Subscriber):
    """Zenoh subscriber for LIDAR data that republishes to ROS2 PointCloud2 topics.

    This subscriber handles LIDAR scan data from Zenoh topics and converts them to
    ROS2 sensor_msgs/PointCloud2 messages. It expects binary-encoded LIDAR data with
    fields for ranges, angles, timestamp, and optionally qualities.
    """

    def __init__(
        self,
        zenoh_topic: str,
        ros2_topic: str,
        zenoh_session: zenoh.Session,
        ros2_node: Node,
        frame_id: str = "laser_link",
        scan_duration: float = 0.1,
        queue_size: int = 1,
        enable_fps_tracking: bool = False,
        fps_log_interval: int = 100,
        max_workers: int = 2,  # Deprecated: kept for backward compatibility
    ) -> None:
        """Initialize the LIDAR subscriber.

        Args:
            zenoh_topic: Raw Zenoh topic name (e.g., "lidar/base")
            ros2_topic: ROS2 topic name (e.g., "/scan")
            zenoh_session: Active Zenoh session
            ros2_node: ROS2 node for publishing
            frame_id: ROS2 frame ID for the LIDAR
            scan_duration: Duration of a single sweep in seconds for time offset calculation
            queue_size: Sample queue size for processing
            enable_fps_tracking: Whether to track and log FPS
            fps_log_interval: Number of messages between FPS logs
            max_workers: (Deprecated) Kept for backward compatibility, use queue_size instead
        """
        self.scan_duration = scan_duration

        # Create LIDAR converter
        self.converter = LidarConverter(frame_id, scan_duration)

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
            f"LIDAR subscriber initialized: {self.zenoh_topic} → {self.ros2_topic}"
        )

    def _create_ros2_publisher(self) -> Any:
        """Create ROS2 PointCloud2 publisher with configured QoS profile.

        Returns:
            ROS2 PointCloud2 publisher with the specified QoS profile
        """
        # Use sensor data QoS profile
        qos = qos_profile_sensor_data

        logger.info("Creating LIDAR publisher with sensor data QoS")

        return self.ros2_node.create_publisher(PointCloud2, self.ros2_topic, qos)

    def _convert_and_publish(self, sample: zenoh.Sample) -> None:
        """Convert Zenoh LIDAR data to ROS2 PointCloud2 and publish.

        Args:
            sample: Zenoh sample containing LIDAR scan data
        """
        try:
            # Convert using the LIDAR converter
            ros_pointcloud = self.converter.convert(sample)

            # Validate the converted data
            if not self._validate_ros_message(ros_pointcloud):
                logger.warning(
                    f"Invalid PointCloud2 message generated from {self.zenoh_topic}"
                )
                return

            # Publish to ROS2
            self._ros2_publisher.publish(ros_pointcloud)

        except Exception as e:
            # Re-raise to let base class handle error logging
            raise RuntimeError(f"LIDAR conversion failed: {e}") from e

    def _validate_ros_message(self, ros_pointcloud: PointCloud2) -> bool:
        """Validate ROS2 PointCloud2 message before publishing.

        Args:
            ros_pointcloud: ROS2 PointCloud2 message to validate

        Returns:
            True if message is valid, False otherwise
        """
        if ros_pointcloud is None:
            logger.warning("ROS PointCloud2 message is None")
            return False

        if ros_pointcloud.header.frame_id == "":
            logger.warning("PointCloud2 message missing frame_id")
            return False

        if ros_pointcloud.width == 0 or ros_pointcloud.height == 0:
            logger.debug(
                "PointCloud2 message has no points (may be normal during startup)"
            )
            return True  # Empty point clouds are valid

        if len(ros_pointcloud.data) == 0:
            logger.debug("PointCloud2 message has empty data")
            return True  # Empty data is valid

        # Check that we have reasonable field definitions
        if len(ros_pointcloud.fields) == 0:
            logger.warning("PointCloud2 message has no field definitions")
            return False

        # Validate that required fields are present
        field_names = [field.name for field in ros_pointcloud.fields]
        required_fields = ["x", "y", "z"]
        for field in required_fields:
            if field not in field_names:
                logger.warning(f"PointCloud2 message missing required field: {field}")
                return False

        return True

    def get_stream_info(self) -> dict[str, Any]:
        """Get information about the LIDAR stream.

        Returns:
            Dictionary with stream information
        """
        return {
            "stream_type": "lidar",
            "zenoh_topic": self.zenoh_topic,
            "ros2_topic": self.ros2_topic,
            "frame_id": self.frame_id,
            "scan_duration": self.scan_duration,
            "active": self.is_active(),
            "fps": self.fps,
        }

    def __str__(self) -> str:
        """String representation of the subscriber."""
        return f"LidarZenohSubscriber({self.zenoh_topic} → {self.ros2_topic})"
