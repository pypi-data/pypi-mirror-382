#!/usr/bin/env python3
"""LIDAR data converter for Zenoh to ROS2."""

from typing import Any

import numpy as np
import zenoh
from builtin_interfaces.msg import Time as TimeMsg
from loguru import logger
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header

try:
    from dexcomm.serialization import deserialize_lidar_2d
except ImportError:
    logger.error(
        "Failed to import dexcomm LIDAR serialization functions. Please install dexcomm."
    )
    raise ImportError("dexcomm LIDAR serialization functions not available")


def normalize_angles(angles: np.ndarray) -> np.ndarray:
    """Normalize angles to the range [-pi, pi]."""
    return (angles + np.pi) % (2 * np.pi) - np.pi


class LidarConverter:
    """Converts LIDAR data from Zenoh format to ROS2 PointCloud2 messages.

    This converter handles the transformation of LIDAR scan data from dexcontrol's
    format (encoded binary) to ROS2 sensor_msgs/PointCloud2 messages.

    Attributes:
        frame_id: ROS2 frame identifier for the LIDAR
        scan_duration: Duration of a single sweep in seconds for time offset calculation
    """

    def __init__(
        self, frame_id: str = "laser_link", scan_duration: float = 0.1
    ) -> None:
        """Initialize the LIDAR converter.

        Args:
            frame_id: ROS2 frame ID for the LIDAR
            scan_duration: Default scan duration in seconds (for time offset calculation)
        """
        self.frame_id = frame_id
        self.scan_duration = scan_duration
        logger.debug(
            f"Initialized LIDAR converter with frame_id: {frame_id}, scan_duration: {scan_duration}"
        )

    def convert(self, sample: zenoh.Sample) -> PointCloud2:
        """Convert Zenoh LIDAR sample to ROS2 PointCloud2 message.

        Args:
            sample: Zenoh sample containing LIDAR scan data

        Returns:
            ROS2 PointCloud2 message

        Raises:
            RuntimeError: If data decoding fails
        """
        try:
            # Deserialize the LIDAR scan data using dexcomm
            raw_data = sample.payload.to_bytes()
            scan_data = deserialize_lidar_2d(raw_data)

            # Validate the decoded data
            if not self.validate_scan_data(scan_data):
                raise RuntimeError("Invalid LIDAR scan data format")

            # Create PointCloud2 message
            return self._scan_data_to_point_cloud(scan_data)

        except Exception as e:
            raise RuntimeError(f"Failed to convert LIDAR data: {e}") from e

    def _scan_data_to_point_cloud(self, scan_data: dict[str, Any]) -> PointCloud2:
        """Convert raw LIDAR scan data to ROS2 PointCloud2 message.

        Args:
            scan_data: Decoded scan data dictionary

        Returns:
            ROS2 PointCloud2 message
        """
        # Create header
        header = Header()
        header.frame_id = self.frame_id
        header.stamp = self._extract_timestamp(scan_data)

        # Extract data
        ranges = scan_data["ranges"]
        angles = scan_data["angles"]
        angles = normalize_angles(angles)  # Normalize angles to [-pi, pi]
        point_times = (
            np.arange(len(ranges)) / len(ranges) * self.scan_duration
        )  # Point time offset

        # Filter out invalid ranges
        valid_angle_mask = (angles >= -np.pi * 5 / 9) & (angles <= np.pi * 5 / 9)
        valid_range_mask = (ranges > 0.05) & (ranges < 25.0)
        valid_mask = valid_range_mask & valid_angle_mask

        ranges = ranges[valid_mask]
        angles = angles[valid_mask]
        point_times = point_times[valid_mask]

        # Convert to point cloud (with 90-degree rotation around Z-axis: y->x, x->-y)
        points_3d_intensity = np.zeros((len(ranges), 5), dtype=np.float32)
        points_3d_intensity[:, 0] = ranges * np.cos(angles)  # x = r*cos(θ) (forward)
        points_3d_intensity[:, 1] = ranges * np.sin(angles)  # y = r*sin(θ) (left)
        points_3d_intensity[:, 2] = 0.0  # z = 0 for 2D LIDAR

        # Set intensity (use qualities if available, otherwise default to 1.0)
        if "qualities" in scan_data and scan_data["qualities"] is not None:
            qualities = scan_data["qualities"][valid_mask]
            points_3d_intensity[:, 3] = (
                qualities.astype(np.float32) / 255.0
            )  # Normalize to [0,1]
        else:
            points_3d_intensity[:, 3] = 1.0  # Default intensity

        points_3d_intensity[:, 4] = point_times.astype(np.float32)  # Add time offset

        # Define point cloud fields
        fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(
                name="intensity", offset=12, datatype=PointField.FLOAT32, count=1
            ),
            PointField(name="time", offset=16, datatype=PointField.FLOAT32, count=1),
        ]

        # Create and return PointCloud2 message
        pcd = point_cloud2.create_cloud(header, fields, points_3d_intensity)
        return pcd

    def _extract_timestamp(self, scan_data: dict[str, Any]) -> TimeMsg:
        """Extract timestamp from LIDAR scan data.

        Args:
            scan_data: Parsed LIDAR scan data dictionary

        Returns:
            ROS2 Time message

        Raises:
            ValueError: If timestamp is missing or invalid
        """
        # CRITICAL: Timestamp is mandatory for robotics safety
        if "timestamp" not in scan_data or scan_data["timestamp"] is None:
            raise ValueError(
                "LIDAR data missing timestamp! LIDAR data must include "
                "valid timestamps for safe robotics operation. "
                "Check dexcomm LIDAR encoding configuration."
            )

        timestamp_ns = int(scan_data["timestamp"])
        return Time(nanoseconds=timestamp_ns).to_msg()

    def validate_scan_data(self, scan_data: dict[str, Any]) -> bool:
        """Validate that LIDAR scan data is in expected format.

        Args:
            scan_data: Parsed LIDAR scan data dictionary

        Returns:
            True if data is valid, False otherwise
        """
        if not isinstance(scan_data, dict):
            logger.warning(f"LIDAR data is not a dictionary: {type(scan_data)}")
            return False

        # Check for required fields
        required_fields = ["ranges", "angles", "timestamp"]
        for field in required_fields:
            if field not in scan_data or scan_data[field] is None:
                logger.warning(f"LIDAR data missing required field: {field}")
                return False

        # Validate array fields
        ranges = scan_data["ranges"]
        angles = scan_data["angles"]

        if not isinstance(ranges, np.ndarray) or not isinstance(angles, np.ndarray):
            logger.warning("LIDAR ranges or angles are not numpy arrays")
            return False

        if len(ranges) != len(angles):
            logger.warning(
                f"LIDAR ranges and angles length mismatch: {len(ranges)} vs {len(angles)}"
            )
            return False

        if len(ranges) == 0:
            logger.warning("LIDAR data contains no points")
            return False

        # Validate qualities if present
        if "qualities" in scan_data and scan_data["qualities"] is not None:
            qualities = scan_data["qualities"]
            if not isinstance(qualities, np.ndarray):
                logger.warning("LIDAR qualities is not a numpy array")
                return False
            if len(qualities) != len(ranges):
                logger.warning(
                    f"LIDAR qualities length mismatch: {len(qualities)} vs {len(ranges)}"
                )
                return False

        return True

    def __str__(self) -> str:
        """String representation of the converter."""
        return f"LidarConverter(frame_id={self.frame_id}, scan_duration={self.scan_duration})"
