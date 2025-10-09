#!/usr/bin/env python3
"""Chassis IMU data converter for Zenoh to ROS2."""

import zenoh
from builtin_interfaces.msg import Time as TimeMsg
from dexcontrol.proto import dexcontrol_msg_pb2
from loguru import logger
from rclpy.time import Time
from sensor_msgs.msg import Imu
from std_msgs.msg import Header


class ChassisIMUConverter:
    """Converts Chassis IMU data from Zenoh protobuf format to ROS2 Imu messages.

    This converter handles the transformation of IMU data from dexcontrol's
    protobuf IMUState format to ROS2 sensor_msgs/Imu messages.

    Attributes:
        frame_id: ROS2 frame identifier for the IMU
    """

    def __init__(self, frame_id: str = "imu_link") -> None:
        """Initialize the Chassis IMU converter.

        Args:
            frame_id: ROS2 frame ID for the IMU
        """
        self.frame_id = frame_id
        logger.debug(f"Initialized Chassis IMU converter with frame_id: {frame_id}")

    def convert(self, sample: zenoh.Sample) -> Imu:
        """Convert Zenoh IMU protobuf sample to ROS2 Imu message.

        Args:
            sample: Zenoh sample containing protobuf IMU data

        Returns:
            ROS2 Imu message

        Raises:
            RuntimeError: If data decoding fails
        """
        try:
            # Decode protobuf data
            raw_data = sample.payload.to_bytes()
            imu_state = dexcontrol_msg_pb2.IMUState()
            imu_state.ParseFromString(raw_data)

            # Create ROS2 Imu message
            imu_msg = Imu()
            imu_msg.header = Header()
            imu_msg.header.frame_id = self.frame_id
            imu_msg.header.stamp = self._extract_timestamp(imu_state)

            # Linear acceleration (acc_x, acc_y, acc_z)
            imu_msg.linear_acceleration.x = float(imu_state.acc_x)
            imu_msg.linear_acceleration.y = float(imu_state.acc_y)
            imu_msg.linear_acceleration.z = float(imu_state.acc_z)

            # Angular velocity (gyro_x, gyro_y, gyro_z)
            imu_msg.angular_velocity.x = float(imu_state.gyro_x)
            imu_msg.angular_velocity.y = float(imu_state.gyro_y)
            imu_msg.angular_velocity.z = float(imu_state.gyro_z)

            # Orientation quaternion (quat_w, quat_x, quat_y, quat_z)
            # Note: protobuf format is w,x,y,z but ROS expects x,y,z,w order in the message fields
            imu_msg.orientation.w = float(imu_state.quat_w)
            imu_msg.orientation.x = float(imu_state.quat_x)
            imu_msg.orientation.y = float(imu_state.quat_y)
            imu_msg.orientation.z = float(imu_state.quat_z)

            # Set covariance matrices (use -1 to indicate unknown)
            imu_msg.linear_acceleration_covariance = [-1.0] * 9
            imu_msg.angular_velocity_covariance = [-1.0] * 9
            imu_msg.orientation_covariance = [-1.0] * 9

            return imu_msg

        except Exception as e:
            raise RuntimeError(f"Failed to convert Chassis IMU data: {e}") from e

    def _extract_timestamp(self, imu_state: dexcontrol_msg_pb2.IMUState) -> TimeMsg:
        """Extract timestamp from IMU protobuf data.

        Args:
            imu_state: Protobuf IMUState message

        Returns:
            ROS2 Time message

        Raises:
            ValueError: If timestamp is missing or invalid
        """
        # Check if timestamp_ns field exists and is valid
        if not hasattr(imu_state, "timestamp_ns") or imu_state.timestamp_ns == 0:
            raise ValueError(
                "Chassis IMU data missing timestamp! IMU data must include "
                "valid timestamps for safe robotics operation."
            )

        timestamp_ns = int(imu_state.timestamp_ns)
        return Time(nanoseconds=timestamp_ns).to_msg()

    def validate_imu_data(self, imu_state: dexcontrol_msg_pb2.IMUState) -> bool:
        """Validate that IMU protobuf data is in expected format.

        Args:
            imu_state: Protobuf IMUState message

        Returns:
            True if data is valid, False otherwise
        """
        # Check that we have the protobuf message type
        if not isinstance(imu_state, dexcontrol_msg_pb2.IMUState):
            logger.warning(f"IMU data is not IMUState protobuf: {type(imu_state)}")
            return False

        # Check for required fields
        required_fields = [
            "acc_x",
            "acc_y",
            "acc_z",
            "gyro_x",
            "gyro_y",
            "gyro_z",
            "quat_w",
            "quat_x",
            "quat_y",
            "quat_z",
        ]

        for field in required_fields:
            if not hasattr(imu_state, field):
                logger.warning(f"IMU protobuf missing field: {field}")
                return False

        return True

    def __str__(self) -> str:
        """String representation of the converter."""
        return f"ChassisIMUConverter(frame_id={self.frame_id})"
