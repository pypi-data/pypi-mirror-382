#!/usr/bin/env python3
"""Configuration loader for ROS2 plugin."""

from pathlib import Path
from typing import Any

import yaml
from loguru import logger


def load_sensor_config(config_path: str | None = None) -> dict[str, Any]:
    """Load sensor configuration from YAML file.

    Args:
        config_path: Path to configuration file. If None, uses default config.

    Returns:
        Dictionary containing sensor configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    if config_path is None:
        config_path = get_default_config_path()

    config_path = Path(config_path)
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        logger.info("Using default configuration")
        return get_default_config()

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        logger.info(f"Loaded configuration from: {config_path}")
        return config

    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in config file {config_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load config file {config_path}: {e}")
        raise


def get_default_config_path() -> str:
    """Get the default configuration file path.

    Returns:
        Path to default configuration file
    """
    # Look for config file in the same directory as this module
    current_dir = Path(__file__).parent
    config_file = current_dir / "sensor_mapping.yaml"
    return str(config_file)


def get_default_config() -> dict[str, Any]:
    """Get default sensor configuration.

    Returns:
        Dictionary containing default sensor configuration
    """
    return {
        "head_camera": {
            "enable": True,
            "streams": {
                "left_rgb": {
                    "enable": True,
                    "zenoh_topic": "camera/head/left_rgb",
                    "ros2_topic": "/head_camera/left/image_raw",
                    "frame_id": "head_camera_left_link",
                    "queue_size": 10,
                },
                "right_rgb": {
                    "enable": True,
                    "zenoh_topic": "camera/head/right_rgb",
                    "ros2_topic": "/head_camera/right/image_raw",
                    "frame_id": "head_camera_right_link",
                    "queue_size": 10,
                },
                "depth": {
                    "enable": True,
                    "zenoh_topic": "camera/head/depth",
                    "ros2_topic": "/head_camera/depth/image_raw",
                    "frame_id": "head_camera_depth_link",
                    "queue_size": 10,
                },
            },
            "fps_tracking": {"enable": False, "log_interval": 100},
        },
        "head_imu": {
            "enable": False,  # Disabled by default
            "zenoh_topic": "imu/head",
            "ros2_topic": "/head_camera/head_imu",
            "frame_id": "head_imu_link",
            "queue_size": 10,
            "fps_tracking": {"enable": False, "log_interval": 100},
        },
        "base_cameras": {
            "enable": False,  # Disabled by default
            "streams": {
                "front": {
                    "enable": False,
                    "zenoh_topic": "camera/base/front/rgb",
                    "ros2_topic": "/base_camera/front/image_raw",
                    "frame_id": "base_camera_front_link",
                    "queue_size": 10,
                },
                "left": {
                    "enable": False,
                    "zenoh_topic": "camera/base/left/rgb",
                    "ros2_topic": "/base_camera/left/image_raw",
                    "frame_id": "base_camera_left_link",
                    "queue_size": 10,
                },
                "right": {
                    "enable": False,
                    "zenoh_topic": "camera/base/right/rgb",
                    "ros2_topic": "/base_camera/right/image_raw",
                    "frame_id": "base_camera_right_link",
                    "queue_size": 10,
                },
                "back": {
                    "enable": False,
                    "zenoh_topic": "camera/base/back/rgb",
                    "ros2_topic": "/base_camera/back/image_raw",
                    "frame_id": "base_camera_back_link",
                    "queue_size": 10,
                },
            },
            "fps_tracking": {"enable": False, "log_interval": 100},
        },
    }


def save_config(config: dict[str, Any], config_path: str) -> None:
    """Save configuration to YAML file.

    Args:
        config: Configuration dictionary to save
        config_path: Path where to save the configuration

    Raises:
        IOError: If file cannot be written
    """
    try:
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        logger.info(f"Configuration saved to: {config_path}")

    except Exception as e:
        logger.error(f"Failed to save config to {config_path}: {e}")
        raise


def validate_config(config: dict[str, Any]) -> bool:
    """Validate sensor configuration structure.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        # Check top-level structure
        if not isinstance(config, dict):
            logger.error("Config must be a dictionary")
            return False

        # Validate each sensor configuration
        for sensor_name, sensor_config in config.items():
            if not isinstance(sensor_config, dict):
                logger.error(f"Sensor config for {sensor_name} must be a dictionary")
                return False

            # Check common fields
            if "enable" not in sensor_config:
                logger.warning(
                    f"Sensor {sensor_name} missing 'enable' field, assuming False"
                )
                sensor_config["enable"] = False

            # Validate camera configurations
            if sensor_name in ["head_camera", "base_cameras"]:
                if not _validate_camera_config(sensor_name, sensor_config):
                    return False

            # Validate IMU configurations
            elif "imu" in sensor_name:
                if not _validate_imu_config(sensor_name, sensor_config):
                    return False

        logger.info("Configuration validation passed")
        return True

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def _validate_camera_config(sensor_name: str, config: dict[str, Any]) -> bool:
    """Validate camera sensor configuration.

    Args:
        sensor_name: Name of the sensor
        config: Sensor configuration dictionary

    Returns:
        True if valid, False otherwise
    """
    if "streams" not in config:
        logger.error(f"Camera {sensor_name} missing 'streams' configuration")
        return False

    streams = config["streams"]
    if not isinstance(streams, dict):
        logger.error(f"Camera {sensor_name} 'streams' must be a dictionary")
        return False

    for stream_name, stream_config in streams.items():
        required_fields = ["zenoh_topic", "ros2_topic", "frame_id"]
        for field in required_fields:
            if field not in stream_config:
                logger.error(f"Stream {sensor_name}/{stream_name} missing '{field}'")
                return False

    return True


def _validate_imu_config(sensor_name: str, config: dict[str, Any]) -> bool:
    """Validate IMU sensor configuration.

    Args:
        sensor_name: Name of the sensor
        config: Sensor configuration dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["zenoh_topic", "ros2_topic", "frame_id"]
    for field in required_fields:
        if field not in config:
            logger.error(f"IMU {sensor_name} missing '{field}'")
            return False

    return True


def get_enabled_sensors(config: dict[str, Any]) -> dict[str, Any]:
    """Get only enabled sensors from configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Dictionary containing only enabled sensors
    """
    enabled = {}

    for sensor_name, sensor_config in config.items():
        if sensor_config.get("enable", False):
            # For cameras, also filter enabled streams
            if "streams" in sensor_config:
                enabled_streams = {}
                for stream_name, stream_config in sensor_config["streams"].items():
                    if stream_config.get("enable", False):
                        enabled_streams[stream_name] = stream_config

                if enabled_streams:
                    sensor_copy = sensor_config.copy()
                    sensor_copy["streams"] = enabled_streams
                    enabled[sensor_name] = sensor_copy
            else:
                enabled[sensor_name] = sensor_config

    return enabled


def create_example_config() -> None:
    """Create an example configuration file."""
    config_path = get_default_config_path()

    if Path(config_path).exists():
        logger.info(f"Configuration file already exists: {config_path}")
        return

    config = get_default_config()
    save_config(config, config_path)
    logger.info(f"Created example configuration file: {config_path}")


if __name__ == "__main__":
    # Create example config when run directly
    create_example_config()
