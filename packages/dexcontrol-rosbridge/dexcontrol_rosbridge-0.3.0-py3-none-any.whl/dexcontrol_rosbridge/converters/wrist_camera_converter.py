#!/usr/bin/env python3
"""Wrist camera data converter for Zenoh to ROS2.

This converter handles ZEDx One wrist camera data, which only provides RGB streams.
It's specialized for left and right wrist cameras used for manipulation tasks.
"""

import zenoh
from loguru import logger
from sensor_msgs.msg import Image

from .camera_converter import CameraConverter


class WristCameraConverter(CameraConverter):
    """Converts wrist camera data from Zenoh format to ROS2 Image messages.

    This converter handles the transformation of wrist camera data from dexcomm's
    serialized format (used in Zenoh topics) to ROS2 sensor_msgs/Image messages.
    Wrist cameras only support RGB data streams (no depth).

    The ZEDx One wrist cameras are used for manipulation tasks and provide
    high-quality RGB images for visual servoing and object detection.

    Attributes:
        side: Which wrist camera ("left" or "right")
        encoding: ROS2 image encoding (always rgb8 for wrist cameras)
        frame_id: ROS2 frame identifier for the wrist camera
    """

    def __init__(
        self, side: str = "left", encoding: str = "rgb8", frame_id: str = None
    ) -> None:
        """Initialize the wrist camera converter.

        Args:
            side: Which wrist camera ("left" or "right")
            encoding: ROS2 image encoding format (default: rgb8)
            frame_id: ROS2 frame ID for the camera. If None, automatically
                     set based on side (e.g., left_wrist_camera_link)

        Raises:
            ValueError: If side is not "left" or "right"
        """
        if side not in ["left", "right"]:
            raise ValueError(
                f"Invalid wrist camera side: {side}. Must be 'left' or 'right'"
            )

        self.side = side

        # Automatically set frame_id based on side if not provided
        if frame_id is None:
            frame_id = f"{side}_wrist_camera_link"

        # Initialize parent class with RGB stream type (wrist cameras only have RGB)
        super().__init__(stream_type="rgb", encoding=encoding, frame_id=frame_id)

        logger.debug(
            f"Initialized {side} wrist camera converter: {encoding}, frame={frame_id}"
        )

    def convert(self, sample: zenoh.Sample) -> Image:
        """Convert Zenoh wrist camera sample to ROS2 Image message.

        Args:
            sample: Zenoh sample containing encoded wrist camera RGB data

        Returns:
            ROS2 Image message

        Raises:
            RuntimeError: If data decoding fails
        """
        try:
            # Use parent class conversion logic
            ros_msg = super().convert(sample)

            # Add wrist camera specific metadata if needed
            # For now, the base conversion is sufficient

            return ros_msg

        except Exception as e:
            raise RuntimeError(
                f"Failed to convert {self.side} wrist camera data: {e}"
            ) from e

    def validate_wrist_camera_data(self, image_data) -> bool:
        """Validate that wrist camera data is in expected format.

        Wrist cameras should always provide RGB data with proper dimensions.

        Args:
            image_data: Decoded image data

        Returns:
            True if data is valid for wrist camera, False otherwise
        """
        if not self.validate_image_data(image_data):
            return False

        # Additional wrist camera specific validation
        # ZEDx One typically provides 1920x1080 or 1280x720 images
        height, width = image_data.shape[0], image_data.shape[1]

        # Common resolutions for ZEDx One
        valid_resolutions = [
            (1920, 1080),  # Full HD
            (1280, 720),  # HD
            (640, 480),  # VGA for faster processing
        ]

        if (width, height) not in valid_resolutions:
            logger.warning(
                f"{self.side.title()} wrist camera has unusual resolution: {width}x{height}. "
                f"Expected one of: {valid_resolutions}"
            )
            # Don't fail, just warn - camera might be configured differently

        return True

    @property
    def camera_side(self) -> str:
        """Get which wrist camera this converter is for.

        Returns:
            "left" or "right"
        """
        return self.side

    def __str__(self) -> str:
        """String representation of the converter."""
        return f"WristCameraConverter(side={self.side}, encoding={self.encoding}, frame={self.frame_id})"


def create_left_wrist_converter(frame_id: str = None) -> WristCameraConverter:
    """Factory function to create left wrist camera converter.

    Args:
        frame_id: ROS2 frame ID for left wrist camera.
                 Defaults to "left_wrist_camera_link" if not provided.

    Returns:
        Configured left wrist camera converter
    """
    return WristCameraConverter("left", "rgb8", frame_id)


def create_right_wrist_converter(frame_id: str = None) -> WristCameraConverter:
    """Factory function to create right wrist camera converter.

    Args:
        frame_id: ROS2 frame ID for right wrist camera.
                 Defaults to "right_wrist_camera_link" if not provided.

    Returns:
        Configured right wrist camera converter
    """
    return WristCameraConverter("right", "rgb8", frame_id)
