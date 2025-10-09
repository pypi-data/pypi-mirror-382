#!/usr/bin/env python3
"""Sensor configuration utilities.

Queue size guidelines:
- Cameras (30 FPS): queue_size=2 provides ~66ms latency buffer
- LIDAR: queue_size=1 for immediate processing
- IMU (high frequency): queue_size=3-5 for small buffer

Small queue sizes ensure low latency and prevent stale data accumulation.
When processing can't keep up, oldest frames are dropped automatically.
"""


def get_head_sensor_configs() -> tuple[list[dict], list[dict]]:
    """Get head sensor configurations for cameras and IMU.

    Returns:
        Tuple of (camera_configs, imu_configs)
    """
    camera_configs = [
        {
            "name": "head_left_rgb",
            "zenoh_topic": "camera/head/left_rgb",
            "ros2_topic": "/head_camera/left/image",
            "frame_id": "head_camera_left_link",
            "compressed": True,
            "compression_format": "jpeg",
            "queue_size": 2,
        },
        {
            "name": "head_right_rgb",
            "zenoh_topic": "camera/head/right_rgb",
            "ros2_topic": "/head_camera/right/image",
            "frame_id": "head_camera_right_link",
            "compressed": True,
            "compression_format": "jpeg",
            "queue_size": 2,
        },
    ]

    imu_configs = [
        {
            "name": "head_imu",
            "zenoh_topic": "imu/head_camera",
            "ros2_topic": "/head_camera/head_imu",
            "frame_id": "head_imu_link",
            "queue_size": 3,
        }
    ]

    return camera_configs, imu_configs


def get_lidar_sensor_configs() -> list[dict]:
    """Get LIDAR sensor configurations.

    Returns:
        List of LIDAR configuration dictionaries
    """
    lidar_configs = [
        {
            "name": "base_lidar",
            "zenoh_topic": "lidar/scan",
            "ros2_topic": "/scan_pcd",
            "frame_id": "laser_link",
            "scan_duration": 0.098,
            "queue_size": 2,
        }
    ]

    return lidar_configs


def get_chassis_imu_sensor_configs() -> list[dict]:
    """Get chassis IMU sensor configurations.

    Returns:
        List of chassis IMU configuration dictionaries
    """
    imu_configs = [
        {
            "name": "base_imu",
            "zenoh_topic": "state/chassis_imu",
            "ros2_topic": "/base_imu",
            "frame_id": "imu_link",
            "queue_size": 3,
        }
    ]

    return imu_configs


def get_lidar_imu_sensor_configs() -> tuple[list[dict], list[dict]]:
    """Get lidar and IMU sensor configurations (legacy function).

    DEPRECATED: Use get_lidar_sensor_configs() and get_chassis_imu_sensor_configs() separately.

    Returns:
        Tuple of (lidar_configs, imu_configs)
    """
    return get_lidar_sensor_configs(), get_chassis_imu_sensor_configs()


def get_wrist_camera_configs() -> list[dict]:
    """Get wrist camera configurations for left and right wrist cameras.

    Returns:
        List of wrist camera configuration dictionaries
    """
    wrist_camera_configs = [
        {
            "name": "left_wrist_camera",
            "zenoh_topic": "camera/left_wrist/rgb",
            "ros2_topic": "/left_wrist_camera/image",
            "side": "left",
            "frame_id": "left_wrist_camera_link",
            "compressed": True,
            "compression_format": "jpeg",
            "queue_size": 2,
        },
        {
            "name": "right_wrist_camera",
            "zenoh_topic": "camera/right_wrist/rgb",
            "ros2_topic": "/right_wrist_camera/image",
            "side": "right",
            "frame_id": "right_wrist_camera_link",
            "compressed": True,
            "compression_format": "jpeg",
            "queue_size": 2,
        },
    ]

    return wrist_camera_configs
