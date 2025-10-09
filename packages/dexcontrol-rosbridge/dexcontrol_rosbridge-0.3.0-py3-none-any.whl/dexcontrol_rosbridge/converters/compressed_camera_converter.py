#!/usr/bin/env python3
"""Compressed camera data converter for Zenoh to ROS2."""

# No typing imports needed for this module currently

import zenoh
from builtin_interfaces.msg import Time as TimeMsg
from loguru import logger
from rclpy.time import Time
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Header

# Import dexcomm deserialization functions
try:
    from dexcomm.serialization import deserialize_depth, deserialize_image
    from dexcomm.serialization.protobuf import image_pb2

    DEXCOMM_AVAILABLE = True
except ImportError:
    logger.error("dexcomm not available. Camera data cannot be processed.")
    deserialize_image = None
    deserialize_depth = None
    image_pb2 = None
    DEXCOMM_AVAILABLE = False
    raise ImportError("dexcomm package is required for camera data conversion")


class CompressedCameraConverter:
    """Converts camera data from Zenoh format to ROS2 CompressedImage messages.

    This converter extracts JPEG data directly without decompression, providing:
    - Zero CPU overhead from image decoding
    - Minimal memory usage
    - Maximum bandwidth efficiency
    - Faster republishing latency

    Attributes:
        stream_type: Type of camera stream (rgb, depth)
        format: Compression format (jpeg, png)
        frame_id: ROS2 frame identifier for the camera
    """

    def __init__(
        self, stream_type: str, format: str = "jpeg", frame_id: str = "camera_link"
    ) -> None:
        """Initialize the compressed camera converter.

        Args:
            stream_type: Type of camera stream ("rgb" or "depth")
            format: Compression format ("jpeg" or "png")
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

        if format not in ["jpeg", "png"]:
            raise ValueError(f"Invalid format: {format}. Must be 'jpeg' or 'png'")

        # CRITICAL: Depth data MUST use PNG (lossless compression)
        # JPEG is lossy and would corrupt distance measurements
        if stream_type == "depth" and format != "png":
            raise ValueError(
                f"Depth streams MUST use PNG compression (lossless). "
                f"JPEG would corrupt depth values. Got: {format}"
            )

        self.stream_type = stream_type
        self.format = format
        self.frame_id = frame_id

        logger.debug(
            f"Initialized compressed camera converter: {stream_type} → {format}"
        )

    def _ensure_dexcomm_available(self):
        """Ensure dexcomm functions are available."""
        if not DEXCOMM_AVAILABLE or image_pb2 is None:
            raise RuntimeError("dexcomm functions not available")

    def convert(self, sample: zenoh.Sample) -> CompressedImage:
        """Convert Zenoh camera sample to ROS2 CompressedImage message.

        This tries to extract compressed data directly for zero-copy performance.
        If that fails, it falls back to decoding and re-encoding the image.

        Args:
            sample: Zenoh sample containing encoded camera data

        Returns:
            ROS2 CompressedImage message with compressed data

        Raises:
            RuntimeError: If data parsing fails
        """
        try:
            # Extract raw data
            raw_data = sample.payload.to_bytes()

            # Try zero-copy path first (best performance)
            try:
                return self._convert_zero_copy(raw_data)
            except (ValueError, RuntimeError) as e:
                logger.warning(
                    f"Zero-copy conversion failed, falling back to decode/encode: {e}"
                )

            # Fallback: decode and re-encode (compatibility)
            return self._convert_fallback(raw_data)

        except Exception as e:
            raise RuntimeError(
                f"Failed to convert {self.stream_type} compressed data: {e}"
            ) from e

    def _convert_zero_copy(self, raw_data: bytes) -> CompressedImage:
        """Zero-copy conversion - extract compressed data directly."""
        # Extract compressed image data (skip header)
        compressed_data, timestamp_ns = self._extract_compressed_data(raw_data)

        # Create ROS2 CompressedImage message
        compressed_msg = CompressedImage()

        # Set header information
        compressed_msg.header = Header()
        compressed_msg.header.frame_id = self.frame_id
        compressed_msg.header.stamp = self._convert_timestamp(timestamp_ns)

        # Set compression format
        compressed_msg.format = self.format

        # Set compressed image data (raw JPEG/PNG bytes)
        compressed_msg.data = compressed_data

        return compressed_msg

    def _convert_fallback(self, raw_data: bytes) -> CompressedImage:
        """Fallback conversion - decode image and re-encode in desired format."""
        import cv2
        import numpy as np

        # Deserialize image using dexcomm
        if self.stream_type == "rgb":
            if deserialize_image is None:
                raise RuntimeError("deserialize_image not available")
            result = deserialize_image(raw_data)
        else:  # depth
            if deserialize_depth is None:
                raise RuntimeError("deserialize_depth not available")
            result = deserialize_depth(raw_data)

        # Handle return format (dict with 'data' and 'timestamp', or just array)
        if isinstance(result, dict):
            image = result["data"]
            timestamp_ns = result.get("timestamp", None)
        else:
            image = result
            timestamp_ns = None

        # CRITICAL: Timestamp is mandatory for robotics safety
        if timestamp_ns is None:
            raise ValueError(
                f"Fallback decoding failed to extract timestamp from {self.stream_type} data. "
                f"Cannot process sensor data without valid timestamps. "
                f"Check dexcomm configuration to ensure timestamps are enabled."
            )

        # Convert to the desired compressed format
        if self.stream_type == "depth":
            # Depth MUST always use PNG (lossless compression)
            if self.format != "png":
                raise RuntimeError(
                    f"Internal error: depth stream with non-PNG format: {self.format}"
                )

            # Convert depth to uint16 (scale by 1000 for millimeters)
            depth_scaled = (image * 1000.0).astype(np.uint16)
            encode_params = [cv2.IMWRITE_PNG_COMPRESSION, 1]
            success, encoded = cv2.imencode(".png", depth_scaled, encode_params)
            if not success:
                raise RuntimeError("Failed to encode depth image as PNG")
            compressed_data = encoded.tobytes()

        elif self.stream_type == "rgb":
            if self.format == "jpeg":
                # Convert RGB to BGR for OpenCV
                if image.ndim == 3 and image.shape[2] == 3:
                    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                else:
                    image_bgr = image

                # Encode as JPEG
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 95]
                success, encoded = cv2.imencode(".jpg", image_bgr, encode_params)
                if not success:
                    raise RuntimeError("Failed to encode RGB image as JPEG")
                compressed_data = encoded.tobytes()

            elif self.format == "png":
                # RGB to PNG
                if image.ndim == 3 and image.shape[2] == 3:
                    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                else:
                    image_bgr = image
                encode_params = [cv2.IMWRITE_PNG_COMPRESSION, 1]
                success, encoded = cv2.imencode(".png", image_bgr, encode_params)
                if not success:
                    raise RuntimeError("Failed to encode RGB image as PNG")
                compressed_data = encoded.tobytes()
            else:
                raise ValueError(f"Unsupported format for RGB: {self.format}")
        else:
            raise ValueError(f"Unknown stream type: {self.stream_type}")

        # Create ROS2 CompressedImage message
        compressed_msg = CompressedImage()
        compressed_msg.header = Header()
        compressed_msg.header.frame_id = self.frame_id
        compressed_msg.header.stamp = self._convert_timestamp(timestamp_ns)
        compressed_msg.format = self.format
        compressed_msg.data = compressed_data

        return compressed_msg

    def _extract_compressed_data(self, raw_data: bytes) -> tuple[bytes, int | None]:
        """Extract compressed image data (JPEG/PNG bytes) from raw data.

        Args:
            raw_data: Raw data with header + compressed image

        Returns:
            A tuple containing the compressed image data and the timestamp in nanoseconds.
        """
        try:
            self._ensure_dexcomm_available()

            # Parse protobuf message
            msg = image_pb2.RGBImage()
            msg.ParseFromString(raw_data)

            # Extract compressed data
            compressed_data = msg.data

            # Extract timestamp if available
            timestamp_ns = msg.timestamp_ns if msg.HasField("timestamp_ns") else None

            # Validate the encoding matches what we expect
            encoding = msg.encoding if msg.HasField("encoding") else "jpeg"
            if encoding != self.format:
                logger.warning(
                    f"Encoding mismatch: expected {self.format}, got {encoding}"
                )

            # Validate magic bytes to ensure it's actually compressed data
            if self.format == "jpeg":
                if len(compressed_data) < 2 or compressed_data[:2] != b"\xff\xd8":
                    raise ValueError(
                        "Compressed data doesn't start with JPEG magic bytes"
                    )
            elif self.format == "png":
                if len(compressed_data) < 4 or compressed_data[:4] != b"\x89PNG":
                    raise ValueError(
                        "Compressed data doesn't start with PNG magic bytes"
                    )

            return compressed_data, timestamp_ns

        except Exception as e:
            raise RuntimeError(
                f"Failed to extract compressed data from protobuf: {e}"
            ) from e

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

    def get_compression_info(self) -> dict:
        """Get information about the compression settings.

        Returns:
            Dictionary with compression information
        """
        return {
            "stream_type": self.stream_type,
            "format": self.format,
            "frame_id": self.frame_id,
            "compressed": True,
            "zero_copy": True,  # No decompression/recompression
        }

    def validate_compressed_data(self, compressed_data: bytes) -> bool:
        """Validate that compressed data has correct format headers.

        Args:
            compressed_data: Raw compressed image bytes

        Returns:
            True if data appears to be valid compressed image
        """
        if len(compressed_data) < 10:
            return False

        # Check for JPEG magic bytes
        if self.format == "jpeg":
            return compressed_data[:2] == b"\xff\xd8"  # JPEG SOI marker

        # Check for PNG magic bytes
        elif self.format == "png":
            return compressed_data[:8] == b"\x89PNG\r\n\x1a\n"  # PNG signature

        return True

    def can_handle_data(self, raw_data: bytes) -> bool:
        """Check if this converter can handle the incoming data format.

        Args:
            raw_data: Raw camera data from Zenoh

        Returns:
            True if data is in compatible compressed format, False otherwise
        """
        try:
            self._ensure_dexcomm_available()

            # Parse protobuf message
            msg = image_pb2.RGBImage()
            msg.ParseFromString(raw_data)

            # Check if encoding matches what we expect
            encoding = msg.encoding if msg.HasField("encoding") else "jpeg"
            if encoding != self.format:
                return False

            # Validate compressed data magic bytes
            compressed_data = msg.data
            if self.format == "jpeg":
                return len(compressed_data) >= 2 and compressed_data[:2] == b"\xff\xd8"
            elif self.format == "png":
                return len(compressed_data) >= 4 and compressed_data[:4] == b"\x89PNG"
            else:
                return False

        except Exception:
            return False

    @property
    def is_available(self) -> bool:
        """Check if converter is available (dexcomm loaded).

        Returns:
            True if converter can be used, False otherwise
        """
        return DEXCOMM_AVAILABLE

    def __str__(self) -> str:
        """String representation of the converter."""
        return f"CompressedCameraConverter(type={self.stream_type}, format={self.format}, frame={self.frame_id})"


def create_compressed_rgb_converter(
    frame_id: str = "camera_rgb_link",
) -> CompressedCameraConverter:
    """Factory function to create compressed RGB camera converter.

    Args:
        frame_id: ROS2 frame ID for RGB camera

    Returns:
        Configured compressed RGB camera converter
    """
    return CompressedCameraConverter("rgb", "jpeg", frame_id)


def create_compressed_depth_converter(
    frame_id: str = "camera_depth_link",
) -> CompressedCameraConverter:
    """Factory function to create compressed depth camera converter.

    Args:
        frame_id: ROS2 frame ID for depth camera

    Returns:
        Configured compressed depth camera converter

    Note:
        Depth streams ALWAYS use PNG compression (lossless) to preserve
        precise distance measurements. JPEG would corrupt depth values.
    """
    # Depth MUST use PNG (lossless) compression
    return CompressedCameraConverter("depth", "png", frame_id)
