#!/usr/bin/env python3
"""IMU data converter for Zenoh to ROS2."""

from typing import Any

import zenoh
from builtin_interfaces.msg import Time as TimeMsg
from loguru import logger
from rclpy.time import Time
from sensor_msgs.msg import Imu
from std_msgs.msg import Header

try:
    from dexcomm.serialization import deserialize_imu
except ImportError:
    logger.error(
        "Failed to import dexcomm IMU serialization functions. Please install dexcomm."
    )
    raise ImportError("dexcomm IMU serialization functions not available")


class IMUConverter:
    """Converts IMU data from Zenoh format to ROS2 Imu messages.

    This converter handles the transformation of IMU data from dexcomm's
    protobuf format to ROS2 sensor_msgs/Imu messages.

    Attributes:
        frame_id: ROS2 frame identifier for the IMU
    """

    def __init__(self, frame_id: str = "imu_link") -> None:
        """Initialize the IMU converter.

        Args:
            frame_id: ROS2 frame ID for the IMU
        """
        self.frame_id = frame_id
        logger.debug(f"Initialized IMU converter with frame_id: {frame_id}")

    def convert(self, sample: zenoh.Sample) -> Imu:
        """Convert Zenoh IMU sample to ROS2 Imu message.

        Args:
            sample: Zenoh sample containing IMU data

        Returns:
            ROS2 Imu message

        Raises:
            RuntimeError: If data decoding fails
        """
        try:
            # Deserialize IMU data using dexcomm
            raw_data = sample.payload.to_bytes()
            imu_data = deserialize_imu(raw_data)

            # Create ROS2 Imu message
            imu_msg = Imu()
            imu_msg.header = Header()
            imu_msg.header.frame_id = self.frame_id
            imu_msg.header.stamp = self._extract_timestamp(imu_data)

            # Linear acceleration (dexcomm uses 'acc' key)
            if "acc" in imu_data and imu_data["acc"] is not None:
                acc = imu_data["acc"]
                imu_msg.linear_acceleration.x = float(acc[0])
                imu_msg.linear_acceleration.y = float(acc[1])
                imu_msg.linear_acceleration.z = float(acc[2])

            # Angular velocity (dexcomm uses 'gyro' key)
            if "gyro" in imu_data and imu_data["gyro"] is not None:
                gyro = imu_data["gyro"]
                imu_msg.angular_velocity.x = float(gyro[0])
                imu_msg.angular_velocity.y = float(gyro[1])
                imu_msg.angular_velocity.z = float(gyro[2])

            # Orientation quaternion (dexcomm uses 'quat' key, format is [w, x, y, z])
            if "quat" in imu_data and imu_data["quat"] is not None:
                quat = imu_data["quat"]
                # dexcomm format is [w, x, y, z], ROS expects [x, y, z, w]
                imu_msg.orientation.w = float(quat[0])
                imu_msg.orientation.x = float(quat[1])
                imu_msg.orientation.y = float(quat[2])
                imu_msg.orientation.z = float(quat[3])

            # Set covariance matrices (use -1 to indicate unknown)
            imu_msg.linear_acceleration_covariance = [-1.0] * 9
            imu_msg.angular_velocity_covariance = [-1.0] * 9
            imu_msg.orientation_covariance = [-1.0] * 9

            return imu_msg

        except Exception as e:
            raise RuntimeError(f"Failed to convert IMU data: {e}") from e

    def _extract_timestamp(self, imu_data: dict[str, Any]) -> TimeMsg:
        """Extract timestamp from IMU data.

        Args:
            imu_data: Parsed IMU data dictionary

        Returns:
            ROS2 Time message

        Raises:
            ValueError: If timestamp is missing or invalid (no synthetic timestamps allowed)
        """
        # CRITICAL: Timestamp is mandatory for robotics safety
        if "timestamp" not in imu_data or imu_data["timestamp"] is None:
            raise ValueError(
                "IMU data missing timestamp! IMU data must include "
                "valid timestamps for safe robotics operation. "
                "Check dexcomm IMU encoding configuration."
            )

        timestamp_ns = int(imu_data["timestamp"])
        return Time(nanoseconds=timestamp_ns).to_msg()

    def validate_imu_data(self, imu_data: dict[str, Any]) -> bool:
        """Validate that IMU data is in expected format.

        Args:
            imu_data: Parsed IMU data dictionary

        Returns:
            True if data is valid, False otherwise
        """
        if not isinstance(imu_data, dict):
            logger.warning(f"IMU data is not a dictionary: {type(imu_data)}")
            return False

        # Check for at least one expected field
        expected_fields = ["acc", "ang_vel", "quat"]
        if not any(field in imu_data for field in expected_fields):
            logger.warning(f"IMU data missing expected fields: {list(imu_data.keys())}")
            return False

        # Validate array fields
        for field_name in ["acc", "ang_vel"]:
            if field_name in imu_data and imu_data[field_name] is not None:
                field_data = imu_data[field_name]
                if not isinstance(field_data, (list, tuple)) or len(field_data) != 3:
                    logger.warning(f"IMU {field_name} has invalid format: {field_data}")
                    return False

        # Validate quaternion field
        if "quat" in imu_data and imu_data["quat"] is not None:
            quat = imu_data["quat"]
            if not isinstance(quat, (list, tuple)) or len(quat) != 4:
                logger.warning(f"IMU quaternion has invalid format: {quat}")
                return False

        return True

    def __str__(self) -> str:
        """String representation of the converter."""
        return f"IMUConverter(frame_id={self.frame_id})"
