#!/usr/bin/env python3
"""Camera data converter for Zenoh to ROS2."""

import numpy as np
import zenoh
from builtin_interfaces.msg import Time as TimeMsg
from cv_bridge import CvBridge
from loguru import logger
from rclpy.time import Time
from sensor_msgs.msg import Image
from std_msgs.msg import Header

# Import dexcomm deserialization functions
try:
    from dexcomm.serialization import deserialize_depth, deserialize_image

    DEXCOMM_AVAILABLE = True
except ImportError:
    logger.error("dexcomm not available. Camera data cannot be decoded.")
    deserialize_image = None
    deserialize_depth = None
    DEXCOMM_AVAILABLE = False
    raise ImportError("dexcomm package is required for camera data conversion")


class CameraConverter:
    """Converts camera data from Zenoh format to ROS2 Image messages.

    This converter handles the transformation of camera data from dexcomm's
    protobuf format (used in Zenoh topics) to ROS2 sensor_msgs/Image messages.
    It supports both RGB and depth data with proper timestamp extraction.

    Attributes:
        encoding: ROS2 image encoding (rgb8, bgr8, 32FC1, etc.)
        frame_id: ROS2 frame identifier for the camera
        stream_type: Type of camera stream (rgb, depth)
    """

    def __init__(
        self, stream_type: str, encoding: str = "rgb8", frame_id: str = "camera_link"
    ) -> None:
        """Initialize the camera converter.

        Args:
            stream_type: Type of camera stream ("rgb" or "depth")
            encoding: ROS2 image encoding format
            frame_id: ROS2 frame ID for the camera

        Raises:
            ValueError: If dexcomm is not available or stream type is invalid
        """
        if not DEXCOMM_AVAILABLE:
            raise ValueError("dexcomm package is required for camera data conversion")

        if stream_type not in ["rgb", "depth"]:
            raise ValueError(
                f"Invalid stream type: {stream_type}. Must be 'rgb' or 'depth'"
            )

        self.stream_type = stream_type
        self.encoding = encoding
        self.frame_id = frame_id
        self.bridge = CvBridge()

        # Set up appropriate deserializer functions
        if stream_type == "rgb":
            self.deserialize_func = deserialize_image
        else:  # depth
            self.deserialize_func = deserialize_depth

        logger.debug(f"Initialized camera converter: {stream_type} → {encoding}")

    def convert(self, sample: zenoh.Sample) -> Image:
        """Convert Zenoh camera sample to ROS2 Image message.

        Args:
            sample: Zenoh sample containing encoded camera data

        Returns:
            ROS2 Image message

        Raises:
            RuntimeError: If data decoding fails
        """
        try:
            # Extract raw data
            raw_data = sample.payload.to_bytes()

            # Deserialize image data using dexcomm
            result = self.deserialize_func(raw_data)

            # Handle return format (dict with 'data' and 'timestamp', or just array)
            if isinstance(result, dict):
                image_data = result["data"]
                timestamp_ns = result.get("timestamp", None)
            else:
                image_data = result
                timestamp_ns = None

            # CRITICAL: Timestamp is mandatory for robotics safety
            if timestamp_ns is None:
                raise ValueError(
                    f"Sensor data missing timestamp! {self.stream_type} data must include "
                    f"valid timestamps for safe robotics operation. "
                    f"Check dexcomm encoding configuration."
                )

            # Convert to ROS2 Image message
            ros_msg = self.bridge.cv2_to_imgmsg(image_data, self.encoding)

            # Set header information
            ros_msg.header = Header()
            ros_msg.header.frame_id = self.frame_id
            ros_msg.header.stamp = self._convert_timestamp(timestamp_ns)

            return ros_msg

        except Exception as e:
            raise RuntimeError(f"Failed to convert {self.stream_type} data: {e}") from e

    def _extract_timestamp(self, raw_data: bytes) -> int | None:
        """Extract timestamp from raw camera data.

        Args:
            raw_data: Raw encoded camera data

        Returns:
            Timestamp in nanoseconds, or None if not available
        """
        try:
            if self.timestamp_func is not None:
                return self.timestamp_func(raw_data)
        except Exception as e:
            logger.debug(
                f"Failed to extract timestamp from {self.stream_type} data: {e}"
            )
        return None

    def _convert_timestamp(self, timestamp_ns: int) -> TimeMsg:
        """Convert timestamp to ROS2 Time message.

        Args:
            timestamp_ns: Timestamp in nanoseconds (REQUIRED)

        Returns:
            ROS2 Time message

        Raises:
            ValueError: If timestamp is invalid (must be valid nanoseconds since epoch)
        """
        try:
            return Time(nanoseconds=int(timestamp_ns)).to_msg()
        except (ValueError, OverflowError) as e:
            raise ValueError(
                f"Invalid timestamp {timestamp_ns}: {e}. "
                "Timestamp must be valid nanoseconds since epoch."
            ) from e

    def get_expected_dimensions(self, image_data: np.ndarray) -> tuple[int, int]:
        """Get expected dimensions for the image data.

        Args:
            image_data: Decoded image data

        Returns:
            Tuple of (height, width)
        """
        return image_data.shape[0], image_data.shape[1]

    def validate_image_data(self, image_data: np.ndarray) -> bool:
        """Validate that image data is in expected format.

        Args:
            image_data: Decoded image data

        Returns:
            True if data is valid, False otherwise
        """
        if image_data is None:
            return False

        if not isinstance(image_data, np.ndarray):
            logger.warning(f"Image data is not numpy array: {type(image_data)}")
            return False

        if len(image_data.shape) < 2:
            logger.warning(f"Image data has invalid shape: {image_data.shape}")
            return False

        # Check dimensions based on stream type
        if self.stream_type == "rgb":
            if len(image_data.shape) != 3 or image_data.shape[2] not in [3, 4]:
                logger.warning(f"RGB image has invalid shape: {image_data.shape}")
                return False
        elif self.stream_type == "depth":
            if len(image_data.shape) != 2:
                logger.warning(f"Depth image has invalid shape: {image_data.shape}")
                return False

        return True

    @property
    def is_available(self) -> bool:
        """Check if converter is available (dexcomm loaded).

        Returns:
            True if converter can be used, False otherwise
        """
        return DEXCOMM_AVAILABLE

    def __str__(self) -> str:
        """String representation of the converter."""
        return f"CameraConverter(type={self.stream_type}, encoding={self.encoding}, frame={self.frame_id})"


def create_rgb_converter(frame_id: str = "camera_rgb_link") -> CameraConverter:
    """Factory function to create RGB camera converter.

    Args:
        frame_id: ROS2 frame ID for RGB camera

    Returns:
        Configured RGB camera converter
    """
    return CameraConverter("rgb", "rgb8", frame_id)


def create_depth_converter(frame_id: str = "camera_depth_link") -> CameraConverter:
    """Factory function to create depth camera converter.

    Args:
        frame_id: ROS2 frame ID for depth camera

    Returns:
        Configured depth camera converter
    """
    return CameraConverter("depth", "32FC1", frame_id)
