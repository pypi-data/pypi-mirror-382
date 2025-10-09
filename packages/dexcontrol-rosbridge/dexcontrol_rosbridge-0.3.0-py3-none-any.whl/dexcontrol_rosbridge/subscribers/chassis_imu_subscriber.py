#!/usr/bin/env python3
"""Chassis IMU-specific Zenoh subscriber for ROS2 republishing."""

from typing import Any

import zenoh
from loguru import logger
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu

from ..converters.chassis_imu_converter import ChassisIMUConverter
from .base_subscriber import BaseZenohROS2Subscriber


class ChassisIMUZenohSubscriber(BaseZenohROS2Subscriber):
    """Zenoh subscriber for Chassis IMU protobuf data that republishes to ROS2 Imu topics.

    This subscriber handles IMU protobuf data from Zenoh topics and converts them to
    ROS2 sensor_msgs/Imu messages. It expects protobuf-formatted IMU data using
    dexcontrol_msg_pb2.IMUState format.
    """

    def __init__(
        self,
        zenoh_topic: str,
        ros2_topic: str,
        zenoh_session: zenoh.Session,
        ros2_node: Node,
        frame_id: str = "imu_link",
        queue_size: int = 3,
        enable_fps_tracking: bool = False,
        fps_log_interval: int = 100,
        max_workers: int = 2,  # Deprecated: kept for backward compatibility
    ) -> None:
        """Initialize the Chassis IMU subscriber.

        Args:
            zenoh_topic: Raw Zenoh topic name (e.g., "state/chassis_imu")
            ros2_topic: ROS2 topic name (e.g., "/base_imu")
            zenoh_session: Active Zenoh session
            ros2_node: ROS2 node for publishing
            frame_id: ROS2 frame ID for the IMU
            queue_size: Sample queue size for processing
            enable_fps_tracking: Whether to track and log FPS
            fps_log_interval: Number of messages between FPS logs
            max_workers: (Deprecated) Kept for backward compatibility, use queue_size instead
        """
        # Create Chassis IMU converter
        self.converter = ChassisIMUConverter(frame_id)

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
            f"Chassis IMU subscriber initialized: {self.zenoh_topic} → {self.ros2_topic}"
        )

    def _create_ros2_publisher(self) -> Any:
        """Create ROS2 Imu publisher with configured QoS profile.

        Returns:
            ROS2 Imu publisher with the specified QoS profile
        """
        # Use sensor data QoS profile
        qos = qos_profile_sensor_data

        logger.info("Creating Chassis IMU publisher with sensor data QoS")

        return self.ros2_node.create_publisher(Imu, self.ros2_topic, qos)

    def _convert_and_publish(self, sample: zenoh.Sample) -> None:
        """Convert Zenoh Chassis IMU protobuf data to ROS2 Imu and publish.

        Args:
            sample: Zenoh sample containing protobuf IMU data
        """
        try:
            # Convert using the Chassis IMU converter
            ros_imu = self.converter.convert(sample)

            # Validate the converted data
            if not self._validate_ros_message(ros_imu):
                logger.warning(
                    f"Invalid Chassis IMU message generated from {self.zenoh_topic}"
                )
                return

            # Publish to ROS2
            self._ros2_publisher.publish(ros_imu)

        except Exception as e:
            # Re-raise to let base class handle error logging
            raise RuntimeError(f"Chassis IMU conversion failed: {e}") from e

    def _validate_ros_message(self, ros_imu: Imu) -> bool:
        """Validate ROS2 Imu message before publishing.

        Args:
            ros_imu: ROS2 Imu message to validate

        Returns:
            True if message is valid, False otherwise
        """
        if ros_imu is None:
            logger.warning("ROS Imu message is None")
            return False

        if ros_imu.header.frame_id == "":
            logger.warning("Chassis IMU message missing frame_id")
            return False

        # Check that at least one data field is non-zero
        has_linear_acc = (
            ros_imu.linear_acceleration.x != 0
            or ros_imu.linear_acceleration.y != 0
            or ros_imu.linear_acceleration.z != 0
        )

        has_angular_vel = (
            ros_imu.angular_velocity.x != 0
            or ros_imu.angular_velocity.y != 0
            or ros_imu.angular_velocity.z != 0
        )

        has_orientation = (
            ros_imu.orientation.w != 0
            or ros_imu.orientation.x != 0
            or ros_imu.orientation.y != 0
            or ros_imu.orientation.z != 0
        )

        if not (has_linear_acc or has_angular_vel or has_orientation):
            logger.debug(
                "Chassis IMU message has all zero values (may be normal during startup)"
            )

        return True

    def get_stream_info(self) -> dict[str, Any]:
        """Get information about the Chassis IMU stream.

        Returns:
            Dictionary with stream information
        """
        return {
            "stream_type": "chassis_imu",
            "zenoh_topic": self.zenoh_topic,
            "ros2_topic": self.ros2_topic,
            "frame_id": self.frame_id,
            "active": self.is_active(),
            "fps": self.fps,
        }

    def __str__(self) -> str:
        """String representation of the subscriber."""
        return f"ChassisIMUZenohSubscriber({self.zenoh_topic} → {self.ros2_topic})"
