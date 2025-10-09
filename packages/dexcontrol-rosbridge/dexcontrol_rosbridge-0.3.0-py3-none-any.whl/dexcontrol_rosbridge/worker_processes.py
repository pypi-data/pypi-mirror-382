#!/usr/bin/env python3
"""Worker process functions for dexcontrol_rosbridge."""

import os
import signal

import rclpy
from loguru import logger

from dexcontrol_rosbridge.subscribers.camera_subscriber import CameraZenohSubscriber
from dexcontrol_rosbridge.subscribers.chassis_imu_subscriber import (
    ChassisIMUZenohSubscriber,
)
from dexcontrol_rosbridge.subscribers.head_imu_subscriber import (
    IMUZenohSubscriber as HeadIMUZenohSubscriber,
)
from dexcontrol_rosbridge.subscribers.lidar_subscriber import LidarZenohSubscriber
from dexcontrol_rosbridge.subscribers.wrist_camera_subscriber import (
    WristCameraZenohSubscriber,
)
from dexcontrol_rosbridge.zenoh_utils import init_zenoh_session


def setup_signal_handlers():
    """Setup common signal handlers for worker processes.

    Returns:
        Function to check if shutdown was requested
    """
    shutdown_requested = False

    def signal_handler(signum, frame):
        nonlocal shutdown_requested
        logger.info(
            f"Process {os.getpid()}: Received signal {signum}, shutting down..."
        )
        shutdown_requested = True

    def is_shutdown_requested():
        return shutdown_requested

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    return is_shutdown_requested


def camera_worker_process(
    zenoh_topic: str,
    ros2_topic: str,
    frame_id: str,
    compressed: bool = True,
    compression_format: str = "jpeg",
    queue_size: int = 2,
    enable_fps_tracking: bool = True,
) -> None:
    """Worker function that runs in a separate process for one camera stream.

    Each process creates its own Zenoh session and ROS2 node for complete isolation.

    Args:
        zenoh_topic: Zenoh topic to subscribe to
        ros2_topic: ROS2 topic to publish to
        frame_id: ROS2 frame ID for camera
        compressed: Whether to publish compressed images
        compression_format: Compression format (jpeg/png)
        queue_size: Queue size for processing
        enable_fps_tracking: Whether to track and log FPS
    """
    process_pid = os.getpid()
    zenoh_session = None
    ros2_node = None
    subscriber = None

    is_shutdown_requested = setup_signal_handlers()

    try:
        logger.info(
            f"Process {process_pid}: Starting camera worker for {zenoh_topic} → {ros2_topic}"
        )

        rclpy.init()
        node_name = f"camera_bridge_{zenoh_topic.replace('/', '_').replace('-', '_')}"
        ros2_node = rclpy.create_node(node_name)
        logger.info(f"Process {process_pid}: Created ROS2 node '{node_name}'")

        zenoh_session = init_zenoh_session()
        logger.info(f"Process {process_pid}: Created Zenoh session {id(zenoh_session)}")

        if "depth" in zenoh_topic.lower() and compression_format != "png":
            logger.warning(
                f"Process {process_pid}: Forcing depth stream to PNG (was {compression_format})"
            )
            compression_format = "png"

        subscriber = CameraZenohSubscriber(
            zenoh_topic=zenoh_topic,
            ros2_topic=ros2_topic,
            zenoh_session=zenoh_session,
            ros2_node=ros2_node,
            frame_id=frame_id,
            enable_fps_tracking=enable_fps_tracking,
            fps_log_interval=30,
            compressed=compressed,
            compression_format=compression_format,
            queue_size=queue_size,
        )

        logger.info(f"Process {process_pid}: Camera subscriber initialized")

        logger.info(f"Process {process_pid}: Waiting for camera data...")
        if not subscriber.wait_for_active(timeout=10.0):
            logger.error(
                f"Process {process_pid}: Camera did not become active within 10 seconds"
            )
            return

        logger.info(
            f"Process {process_pid}: Camera is active, starting republishing..."
        )

        while not is_shutdown_requested():
            try:
                rclpy.spin_once(ros2_node, timeout_sec=0.1)
            except Exception as e:
                logger.error(f"Process {process_pid}: Error in ROS2 spin: {e}")
                break

        logger.info(f"Process {process_pid}: Camera worker shutting down normally")

    except KeyboardInterrupt:
        logger.info(f"Process {process_pid}: Camera worker interrupted")
    except Exception as e:
        logger.error(f"Process {process_pid}: Camera worker error: {e}")
        raise
    finally:
        _cleanup_resources(process_pid, subscriber, ros2_node, zenoh_session)


def head_imu_worker_process(
    zenoh_topic: str,
    ros2_topic: str,
    frame_id: str,
    queue_size: int = 3,
    enable_fps_tracking: bool = True,
) -> None:
    """Worker function that runs in a separate process for one head IMU stream.

    Each process creates its own Zenoh session and ROS2 node for complete isolation.

    Args:
        zenoh_topic: Zenoh topic to subscribe to
        ros2_topic: ROS2 topic to publish to
        frame_id: ROS2 frame ID for IMU
        queue_size: Queue size for processing
        enable_fps_tracking: Whether to track and log FPS
    """
    process_pid = os.getpid()
    zenoh_session = None
    ros2_node = None
    subscriber = None

    is_shutdown_requested = setup_signal_handlers()

    try:
        logger.info(
            f"Process {process_pid}: Starting head IMU worker for {zenoh_topic} → {ros2_topic}"
        )

        rclpy.init()
        node_name = f"head_imu_bridge_{zenoh_topic.replace('/', '_').replace('-', '_')}"
        ros2_node = rclpy.create_node(node_name)
        logger.info(f"Process {process_pid}: Created ROS2 node '{node_name}'")

        zenoh_session = init_zenoh_session()
        logger.info(f"Process {process_pid}: Created Zenoh session {id(zenoh_session)}")

        subscriber = HeadIMUZenohSubscriber(
            zenoh_topic=zenoh_topic,
            ros2_topic=ros2_topic,
            zenoh_session=zenoh_session,
            ros2_node=ros2_node,
            frame_id=frame_id,
            enable_fps_tracking=enable_fps_tracking,
            fps_log_interval=30,
            queue_size=queue_size,
        )

        logger.info(f"Process {process_pid}: Head IMU subscriber initialized")

        logger.info(f"Process {process_pid}: Waiting for head IMU data...")
        if not subscriber.wait_for_active(timeout=10.0):
            logger.error(
                f"Process {process_pid}: Head IMU did not become active within 10 seconds"
            )
            return

        logger.info(
            f"Process {process_pid}: Head IMU is active, starting republishing..."
        )

        while not is_shutdown_requested():
            try:
                rclpy.spin_once(ros2_node, timeout_sec=0.1)
            except Exception as e:
                logger.error(f"Process {process_pid}: Error in ROS2 spin: {e}")
                break

        logger.info(f"Process {process_pid}: Head IMU worker shutting down normally")

    except KeyboardInterrupt:
        logger.info(f"Process {process_pid}: Head IMU worker interrupted")
    except Exception as e:
        logger.error(f"Process {process_pid}: Head IMU worker error: {e}")
        raise
    finally:
        _cleanup_resources(process_pid, subscriber, ros2_node, zenoh_session)


def chassis_imu_worker_process(
    zenoh_topic: str,
    ros2_topic: str,
    frame_id: str,
    queue_size: int = 3,
    enable_fps_tracking: bool = True,
) -> None:
    """Worker function that runs in a separate process for one chassis IMU stream.

    This worker handles protobuf-encoded IMU data from the chassis IMU sensor.
    Each process creates its own Zenoh session and ROS2 node for complete isolation.

    Args:
        zenoh_topic: Zenoh topic to subscribe to
        ros2_topic: ROS2 topic to publish to
        frame_id: ROS2 frame ID for IMU
        queue_size: Queue size for processing
        enable_fps_tracking: Whether to track and log FPS
    """
    process_pid = os.getpid()
    zenoh_session = None
    ros2_node = None
    subscriber = None

    is_shutdown_requested = setup_signal_handlers()

    try:
        logger.info(
            f"Process {process_pid}: Starting chassis IMU worker for {zenoh_topic} → {ros2_topic}"
        )

        rclpy.init()
        node_name = (
            f"chassis_imu_bridge_{zenoh_topic.replace('/', '_').replace('-', '_')}"
        )
        ros2_node = rclpy.create_node(node_name)
        logger.info(f"Process {process_pid}: Created ROS2 node '{node_name}'")

        zenoh_session = init_zenoh_session()
        logger.info(f"Process {process_pid}: Created Zenoh session {id(zenoh_session)}")

        subscriber = ChassisIMUZenohSubscriber(
            zenoh_topic=zenoh_topic,
            ros2_topic=ros2_topic,
            zenoh_session=zenoh_session,
            ros2_node=ros2_node,
            frame_id=frame_id,
            enable_fps_tracking=enable_fps_tracking,
            fps_log_interval=30,
            queue_size=queue_size,
        )

        logger.info(f"Process {process_pid}: Chassis IMU subscriber initialized")

        logger.info(f"Process {process_pid}: Waiting for chassis IMU data...")
        if not subscriber.wait_for_active(timeout=10.0):
            logger.error(
                f"Process {process_pid}: Chassis IMU did not become active within 10 seconds"
            )
            return

        logger.info(
            f"Process {process_pid}: Chassis IMU is active, starting republishing..."
        )

        while not is_shutdown_requested():
            try:
                rclpy.spin_once(ros2_node, timeout_sec=0.1)
            except Exception as e:
                logger.error(f"Process {process_pid}: Error in ROS2 spin: {e}")
                break

        logger.info(f"Process {process_pid}: Chassis IMU worker shutting down normally")

    except KeyboardInterrupt:
        logger.info(f"Process {process_pid}: Chassis IMU worker interrupted")
    except Exception as e:
        logger.error(f"Process {process_pid}: Chassis IMU worker error: {e}")
        raise
    finally:
        _cleanup_resources(process_pid, subscriber, ros2_node, zenoh_session)


def lidar_worker_process(
    zenoh_topic: str,
    ros2_topic: str,
    frame_id: str,
    scan_duration: float = 0.1,
    queue_size: int = 1,
    enable_fps_tracking: bool = True,
) -> None:
    """Worker function that runs in a separate process for one LIDAR stream.

    Each process creates its own Zenoh session and ROS2 node for complete isolation.

    Args:
        zenoh_topic: Zenoh topic to subscribe to
        ros2_topic: ROS2 topic to publish to
        frame_id: ROS2 frame ID for LIDAR
        scan_duration: Duration of a single sweep in seconds for time offset calculation
        queue_size: Queue size for processing
        enable_fps_tracking: Whether to track and log FPS
    """
    process_pid = os.getpid()
    zenoh_session = None
    ros2_node = None
    subscriber = None

    is_shutdown_requested = setup_signal_handlers()

    try:
        logger.info(
            f"Process {process_pid}: Starting LIDAR worker for {zenoh_topic} → {ros2_topic}"
        )

        rclpy.init()
        node_name = f"lidar_bridge_{zenoh_topic.replace('/', '_').replace('-', '_')}"
        ros2_node = rclpy.create_node(node_name)
        logger.info(f"Process {process_pid}: Created ROS2 node '{node_name}'")

        zenoh_session = init_zenoh_session()

        subscriber = LidarZenohSubscriber(
            zenoh_topic=zenoh_topic,
            ros2_topic=ros2_topic,
            zenoh_session=zenoh_session,
            ros2_node=ros2_node,
            frame_id=frame_id,
            scan_duration=scan_duration,
            enable_fps_tracking=enable_fps_tracking,
            fps_log_interval=30,
            queue_size=queue_size,
        )

        logger.info(f"Process {process_pid}: LIDAR subscriber initialized")

        logger.info(f"Process {process_pid}: Waiting for LIDAR data...")
        if not subscriber.wait_for_active(timeout=10.0):
            logger.error(
                f"Process {process_pid}: LIDAR did not become active within 10 seconds"
            )
            return

        logger.info(f"Process {process_pid}: LIDAR is active, starting republishing...")

        while not is_shutdown_requested():
            try:
                rclpy.spin_once(ros2_node, timeout_sec=0.1)
            except Exception as e:
                logger.error(f"Process {process_pid}: Error in ROS2 spin: {e}")
                break

        logger.info(f"Process {process_pid}: LIDAR worker shutting down normally")

    except KeyboardInterrupt:
        logger.info(f"Process {process_pid}: LIDAR worker interrupted")
    except Exception as e:
        logger.error(f"Process {process_pid}: LIDAR worker error: {e}")
        raise
    finally:
        _cleanup_resources(process_pid, subscriber, ros2_node, zenoh_session)


def wrist_camera_worker_process(
    zenoh_topic: str,
    ros2_topic: str,
    side: str = None,
    frame_id: str = None,
    compressed: bool = True,
    compression_format: str = "jpeg",
    queue_size: int = 2,
    enable_fps_tracking: bool = True,
) -> None:
    """Worker function that runs in a separate process for one wrist camera stream.

    This worker handles ZEDx One wrist camera data for manipulation tasks.
    Each process creates its own Zenoh session and ROS2 node for complete isolation.

    Args:
        zenoh_topic: Zenoh topic to subscribe to
        ros2_topic: ROS2 topic to publish to
        side: Which wrist camera ("left" or "right"). Auto-detected if None
        frame_id: ROS2 frame ID. Auto-set based on side if None
        compressed: Whether to publish compressed images
        compression_format: Compression format (jpeg/png)
        queue_size: Queue size for processing
        enable_fps_tracking: Whether to track and log FPS
    """
    process_pid = os.getpid()
    zenoh_session = None
    ros2_node = None
    subscriber = None

    is_shutdown_requested = setup_signal_handlers()

    # Auto-detect side from topic if not provided
    if side is None:
        topic_lower = zenoh_topic.lower()
        if "left" in topic_lower:
            side = "left"
        elif "right" in topic_lower:
            side = "right"
        else:
            side = "left"  # Default
            logger.warning(
                f"Process {process_pid}: Could not detect wrist side, defaulting to left"
            )

    try:
        logger.info(
            f"Process {process_pid}: Starting {side} wrist camera worker for {zenoh_topic} → {ros2_topic}"
        )

        rclpy.init()
        node_name = f"{side}_wrist_camera_bridge_{zenoh_topic.replace('/', '_').replace('-', '_')}"
        ros2_node = rclpy.create_node(node_name)
        logger.info(f"Process {process_pid}: Created ROS2 node '{node_name}'")

        zenoh_session = init_zenoh_session()
        logger.info(f"Process {process_pid}: Created Zenoh session {id(zenoh_session)}")

        # Wrist cameras are always RGB, never depth
        if compression_format == "png" and "depth" not in zenoh_topic.lower():
            logger.info(
                f"Process {process_pid}: Using JPEG for {side} wrist RGB camera (more efficient)"
            )
            compression_format = "jpeg"

        subscriber = WristCameraZenohSubscriber(
            zenoh_topic=zenoh_topic,
            ros2_topic=ros2_topic,
            zenoh_session=zenoh_session,
            ros2_node=ros2_node,
            side=side,
            frame_id=frame_id,
            enable_fps_tracking=enable_fps_tracking,
            fps_log_interval=30,
            compressed=compressed,
            compression_format=compression_format,
            queue_size=queue_size,
        )

        logger.info(
            f"Process {process_pid}: {side.title()} wrist camera subscriber initialized"
        )

        logger.info(f"Process {process_pid}: Waiting for {side} wrist camera data...")
        if not subscriber.wait_for_active(timeout=10.0):
            logger.error(
                f"Process {process_pid}: {side.title()} wrist camera did not become active within 10 seconds"
            )
            return

        logger.info(
            f"Process {process_pid}: {side.title()} wrist camera is active, starting republishing..."
        )

        while not is_shutdown_requested():
            try:
                rclpy.spin_once(ros2_node, timeout_sec=0.1)
            except Exception as e:
                logger.error(f"Process {process_pid}: Error in ROS2 spin: {e}")
                break

        logger.info(
            f"Process {process_pid}: {side.title()} wrist camera worker shutting down normally"
        )

    except KeyboardInterrupt:
        logger.info(
            f"Process {process_pid}: {side.title()} wrist camera worker interrupted"
        )
    except Exception as e:
        logger.error(
            f"Process {process_pid}: {side.title()} wrist camera worker error: {e}"
        )
        raise
    finally:
        _cleanup_resources(process_pid, subscriber, ros2_node, zenoh_session)


def _cleanup_resources(process_pid: int, subscriber, ros2_node, zenoh_session):
    """Clean up process resources in proper order.

    Args:
        process_pid: Process ID for logging
        subscriber: Subscriber instance to shutdown
        ros2_node: ROS2 node to destroy
        zenoh_session: Zenoh session to close
    """
    logger.info(f"Process {process_pid}: Cleaning up resources...")

    if subscriber:
        try:
            subscriber.shutdown()
            logger.debug(f"Process {process_pid}: Subscriber shutdown")
        except Exception as e:
            logger.warning(
                f"Process {process_pid}: Error shutting down subscriber: {e}"
            )

    if ros2_node:
        try:
            ros2_node.destroy_node()
            logger.debug(f"Process {process_pid}: ROS2 node destroyed")
        except Exception as e:
            logger.warning(f"Process {process_pid}: Error destroying ROS2 node: {e}")

    try:
        rclpy.shutdown()
        logger.debug(f"Process {process_pid}: ROS2 shutdown")
    except Exception as e:
        logger.warning(f"Process {process_pid}: Error shutting down ROS2: {e}")

    if zenoh_session:
        try:
            zenoh_session.close()
            logger.debug(f"Process {process_pid}: Zenoh session closed")
        except Exception as e:
            logger.warning(f"Process {process_pid}: Error closing Zenoh session: {e}")

    logger.info(f"Process {process_pid}: Cleanup complete")
