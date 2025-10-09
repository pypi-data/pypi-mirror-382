"""dexcontrol_rosbridge - High-performance sensor data bridge between Zenoh and ROS2.

This package provides a multi-process architecture for republishing sensor data
from Zenoh topics to ROS2 topics with complete fault isolation and high performance.
"""

__version__ = "0.1.0"
__author__ = "Guofei"
__license__ = "MIT"

# Main API exports
from dexcontrol_rosbridge.multiprocess_sensor_manager import MultiProcessSensorManager
from dexcontrol_rosbridge.sensor_configs import (
    get_chassis_imu_sensor_configs,
    get_head_sensor_configs,
    get_lidar_imu_sensor_configs,  # deprecated, kept for backwards compatibility
    get_lidar_sensor_configs,
    get_wrist_camera_configs,
)

__all__ = [
    "MultiProcessSensorManager",
    "get_head_sensor_configs",
    "get_lidar_sensor_configs",
    "get_chassis_imu_sensor_configs",
    "get_wrist_camera_configs",
    "get_lidar_imu_sensor_configs",  # deprecated
]
