#!/usr/bin/env python3
"""Unified multi-process sensor manager for dexcontrol_rosbridge.

This module provides a unified manager for running multiple sensor processes
(cameras, IMU, LIDAR) with complete isolation using multiprocessing.
"""

import signal
import time
from multiprocessing import Process

from loguru import logger

# Import worker processes
from dexcontrol_rosbridge.worker_processes import (
    camera_worker_process,
    chassis_imu_worker_process,
    head_imu_worker_process,
    lidar_worker_process,
    wrist_camera_worker_process,
)


class MultiProcessSensorManager:
    """Manager for multiple sensor processes using multiprocessing.Process.

    This manager supports cameras, IMU sensors, and LIDAR sensors with complete
    process isolation. Each sensor runs in its own process with its own Zenoh
    session and ROS2 node for maximum fault isolation and performance.
    """

    def __init__(self):
        self.processes: dict[str, Process] = {}
        self.sensor_configs: list[dict] = []
        self.shutdown_requested = False

        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, _frame):
        """Handle shutdown signals."""
        logger.info(
            f"Main process: Received signal {signum}, shutting down all sensor processes..."
        )
        self.shutdown_requested = True

    def add_camera(
        self,
        name: str,
        zenoh_topic: str,
        ros2_topic: str,
        frame_id: str = "camera_link",
        compressed: bool = True,
        compression_format: str = "jpeg",
        queue_size: int = 2,
    ) -> None:
        """Add a camera configuration.

        Args:
            name: Unique name for this camera
            zenoh_topic: Zenoh topic to subscribe to
            ros2_topic: ROS2 topic to publish to
            frame_id: ROS2 frame ID
            compressed: Whether to publish compressed images
            compression_format: Compression format (jpeg/png)
            queue_size: Queue size for processing
        """
        config = {
            "type": "camera",
            "name": name,
            "zenoh_topic": zenoh_topic,
            "ros2_topic": ros2_topic,
            "frame_id": frame_id,
            "compressed": compressed,
            "compression_format": compression_format,
            "queue_size": queue_size,
        }

        self.sensor_configs.append(config)
        logger.info(f"Added camera config: {name} ({zenoh_topic} → {ros2_topic})")

    def add_head_imu(
        self,
        name: str,
        zenoh_topic: str,
        ros2_topic: str,
        frame_id: str = "head_imu_link",
        queue_size: int = 3,
    ) -> None:
        """Add a head IMU configuration.

        Args:
            name: Unique name for this head IMU
            zenoh_topic: Zenoh topic to subscribe to
            ros2_topic: ROS2 topic to publish to
            frame_id: ROS2 frame ID
            queue_size: Queue size for processing
        """
        config = {
            "type": "head_imu",
            "name": name,
            "zenoh_topic": zenoh_topic,
            "ros2_topic": ros2_topic,
            "frame_id": frame_id,
            "queue_size": queue_size,
        }

        self.sensor_configs.append(config)
        logger.info(f"Added head IMU config: {name} ({zenoh_topic} → {ros2_topic})")

    def add_chassis_imu(
        self,
        name: str,
        zenoh_topic: str,
        ros2_topic: str,
        frame_id: str = "imu_link",
        queue_size: int = 3,
    ) -> None:
        """Add a chassis IMU configuration.

        Args:
            name: Unique name for this chassis IMU
            zenoh_topic: Zenoh topic to subscribe to
            ros2_topic: ROS2 topic to publish to
            frame_id: ROS2 frame ID
            queue_size: Queue size for processing
        """
        config = {
            "type": "chassis_imu",
            "name": name,
            "zenoh_topic": zenoh_topic,
            "ros2_topic": ros2_topic,
            "frame_id": frame_id,
            "queue_size": queue_size,
        }

        self.sensor_configs.append(config)
        logger.info(f"Added chassis IMU config: {name} ({zenoh_topic} → {ros2_topic})")

    def add_lidar(
        self,
        name: str,
        zenoh_topic: str,
        ros2_topic: str,
        frame_id: str = "laser_link",
        scan_duration: float = 0.1,
        queue_size: int = 1,
    ) -> None:
        """Add a LIDAR configuration.

        Args:
            name: Unique name for this LIDAR
            zenoh_topic: Zenoh topic to subscribe to
            ros2_topic: ROS2 topic to publish to
            frame_id: ROS2 frame ID
            scan_duration: Duration of a single sweep in seconds for time offset calculation
            queue_size: Queue size for processing
        """
        config = {
            "type": "lidar",
            "name": name,
            "zenoh_topic": zenoh_topic,
            "ros2_topic": ros2_topic,
            "frame_id": frame_id,
            "scan_duration": scan_duration,
            "queue_size": queue_size,
        }

        self.sensor_configs.append(config)
        logger.info(f"Added LIDAR config: {name} ({zenoh_topic} → {ros2_topic})")

    def add_wrist_camera(
        self,
        name: str,
        zenoh_topic: str,
        ros2_topic: str,
        side: str = None,
        frame_id: str = None,
        compressed: bool = True,
        compression_format: str = "jpeg",
        queue_size: int = 2,
    ) -> None:
        """Add a wrist camera configuration.

        Args:
            name: Unique name for this wrist camera
            zenoh_topic: Zenoh topic to subscribe to
            ros2_topic: ROS2 topic to publish to
            side: Which wrist ("left" or "right"). Auto-detected if None
            frame_id: ROS2 frame ID. Auto-set based on side if None
            compressed: Whether to publish compressed images
            compression_format: Compression format (jpeg/png)
            queue_size: Queue size for processing
        """
        config = {
            "type": "wrist_camera",
            "name": name,
            "zenoh_topic": zenoh_topic,
            "ros2_topic": ros2_topic,
            "side": side,
            "frame_id": frame_id,
            "compressed": compressed,
            "compression_format": compression_format,
            "queue_size": queue_size,
        }

        self.sensor_configs.append(config)
        side_str = side if side else "auto-detect"
        logger.info(
            f"Added wrist camera config: {name} ({side_str}) ({zenoh_topic} → {ros2_topic})"
        )

    def add_sensor(self, sensor_type: str, **kwargs) -> None:
        """Generic method to add any sensor type.

        Args:
            sensor_type: Type of sensor ("camera", "imu", "lidar", "wrist_camera")
            **kwargs: Sensor-specific configuration parameters
        """
        if sensor_type == "camera":
            self.add_camera(**kwargs)
        elif sensor_type == "head_imu":
            self.add_head_imu(**kwargs)
        elif sensor_type == "chassis_imu":
            self.add_chassis_imu(**kwargs)
        elif sensor_type == "lidar":
            self.add_lidar(**kwargs)
        elif sensor_type == "wrist_camera":
            self.add_wrist_camera(**kwargs)
        else:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

    def start_all_sensors(self) -> bool:
        """Start all configured sensor processes.

        Returns:
            True if all processes started successfully
        """
        if not self.sensor_configs:
            logger.warning("No sensor configurations added")
            return False

        logger.info(f"Starting {len(self.sensor_configs)} sensor processes...")

        success_count = 0
        for config in self.sensor_configs:
            if self._start_sensor_process(config):
                success_count += 1
            else:
                logger.error(f"Failed to start sensor process: {config['name']}")

        if success_count == len(self.sensor_configs):
            logger.info(f"All {success_count} sensor processes started successfully")
            return True
        else:
            logger.error(
                f"Only {success_count}/{len(self.sensor_configs)} processes started"
            )
            return False

    def _start_sensor_process(self, config: dict) -> bool:
        """Start a single sensor process.

        Args:
            config: Sensor configuration dictionary

        Returns:
            True if process started successfully
        """
        name = config["name"]
        sensor_type = config["type"]

        try:
            # Choose worker function based on sensor type
            if sensor_type == "camera":
                process = Process(
                    target=camera_worker_process,
                    args=(
                        config["zenoh_topic"],
                        config["ros2_topic"],
                        config["frame_id"],
                        config["compressed"],
                        config["compression_format"],
                        config["queue_size"],
                    ),
                    name=f"camera_{name}",  # Process name for monitoring
                )
            elif sensor_type == "head_imu":
                process = Process(
                    target=head_imu_worker_process,
                    args=(
                        config["zenoh_topic"],
                        config["ros2_topic"],
                        config["frame_id"],
                        config["queue_size"],
                    ),
                    name=f"head_imu_{name}",  # Process name for monitoring
                )
            elif sensor_type == "chassis_imu":
                process = Process(
                    target=chassis_imu_worker_process,
                    args=(
                        config["zenoh_topic"],
                        config["ros2_topic"],
                        config["frame_id"],
                        config["queue_size"],
                    ),
                    name=f"chassis_imu_{name}",  # Process name for monitoring
                )
            elif sensor_type == "lidar":
                process = Process(
                    target=lidar_worker_process,
                    args=(
                        config["zenoh_topic"],
                        config["ros2_topic"],
                        config["frame_id"],
                        config["scan_duration"],
                        config["queue_size"],
                    ),
                    name=f"lidar_{name}",  # Process name for monitoring
                )
            elif sensor_type == "wrist_camera":
                process = Process(
                    target=wrist_camera_worker_process,
                    args=(
                        config["zenoh_topic"],
                        config["ros2_topic"],
                        config.get("side"),  # Can be None for auto-detection
                        config.get("frame_id"),  # Can be None for auto-setting
                        config["compressed"],
                        config["compression_format"],
                        config["queue_size"],
                    ),
                    name=f"wrist_camera_{name}",  # Process name for monitoring
                )
            else:
                logger.error(f"Unknown sensor type: {sensor_type}")
                return False

            # Start the process
            process.start()
            self.processes[name] = process

            logger.info(f"Started {sensor_type} process: {name} (PID: {process.pid})")

            # Give process a moment to initialize
            time.sleep(0.3)

            # Check if process is still running
            if process.is_alive():
                return True
            else:
                logger.error(f"{sensor_type.title()} process {name} exited immediately")
                return False

        except Exception as e:
            logger.error(f"Failed to start {sensor_type} process {name}: {e}")
            return False

    def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal or process failure."""
        try:
            while not self.shutdown_requested and self._all_processes_alive():
                time.sleep(1.0)
        except KeyboardInterrupt:
            logger.info("Shutdown requested via keyboard interrupt")
            self.shutdown_requested = True

    def _all_processes_alive(self) -> bool:
        """Check if all processes are still alive."""
        if not self.processes:
            return False

        for name, process in self.processes.items():
            if not process.is_alive():
                logger.warning(
                    f"Sensor process {name} died (exit code: {process.exitcode})"
                )
                return False

        return True

    def shutdown_all(self, timeout: float = 10.0) -> None:
        """Shutdown all sensor processes.

        Args:
            timeout: Maximum time to wait for graceful shutdown
        """
        if not self.processes:
            logger.info("No processes to shutdown")
            return

        logger.info(f"Shutting down {len(self.processes)} sensor processes...")

        # Send SIGTERM to all processes for graceful shutdown
        for name, process in self.processes.items():
            if process.is_alive():
                try:
                    logger.info(f"Sending SIGTERM to {name} (PID: {process.pid})")
                    process.terminate()
                except Exception as e:
                    logger.warning(f"Error terminating process {name}: {e}")

        # Wait for graceful shutdown
        start_time = time.time()
        remaining = list(self.processes.items())

        while remaining and (time.time() - start_time) < timeout:
            for name, process in list(remaining):
                if not process.is_alive():
                    logger.info(f"Process {name} shutdown gracefully")
                    remaining.remove((name, process))

            if remaining:
                time.sleep(0.5)

        # Force kill any remaining processes
        if remaining:
            logger.warning(f"Force killing {len(remaining)} remaining processes...")
            for name, process in remaining:
                if process.is_alive():
                    try:
                        logger.warning(f"Force killing {name} (PID: {process.pid})")
                        process.kill()
                        process.join(timeout=2.0)
                    except Exception as e:
                        logger.error(f"Error force killing process {name}: {e}")

        # Wait for all processes to finish
        for name, process in self.processes.items():
            try:
                process.join(timeout=1.0)
            except Exception as e:
                logger.warning(f"Error joining process {name}: {e}")

        self.processes.clear()
        logger.info("All sensor processes shutdown complete")

    def get_process_info(self) -> dict[str, dict]:
        """Get information about all running processes.

        Returns:
            Dictionary mapping process names to process information
        """
        info = {}
        for name, process in self.processes.items():
            info[name] = {
                "pid": process.pid if process.is_alive() else None,
                "alive": process.is_alive(),
                "exitcode": process.exitcode,
                "name": process.name,
            }
        return info

    def get_sensor_configs(self) -> list[dict]:
        """Get all sensor configurations.

        Returns:
            List of sensor configuration dictionaries
        """
        return self.sensor_configs.copy()

    def get_process_count(self) -> int:
        """Get the number of running processes.

        Returns:
            Number of currently running processes
        """
        return len([p for p in self.processes.values() if p.is_alive()])

    def __len__(self) -> int:
        """Return the number of configured sensors."""
        return len(self.sensor_configs)

    def __str__(self) -> str:
        """String representation of the manager."""
        alive_count = self.get_process_count()
        return f"MultiProcessSensorManager({len(self.sensor_configs)} sensors, {alive_count} alive)"
