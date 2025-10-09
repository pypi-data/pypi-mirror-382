#!/usr/bin/env python3
"""Zenoh utilities for pyrosbridge."""

import os

import dexcontrol
import zenoh
from loguru import logger


def init_zenoh_session(zenoh_config_file: str | None = None) -> zenoh.Session:
    """Initialize Zenoh session using same config as dexcontrol.

    Args:
        zenoh_config_file: Optional path to Zenoh config file

    Returns:
        Initialized Zenoh session

    Raises:
        RuntimeError: If Zenoh session initialization fails
    """
    try:
        config_path = zenoh_config_file or get_default_zenoh_config()

        if config_path is not None:
            logger.info(
                f"Process {os.getpid()}: Using Zenoh config from: {config_path}"
            )
            zenoh_session = zenoh.open(zenoh.Config.from_file(str(config_path)))
        else:
            logger.warning(
                f"Process {os.getpid()}: Zenoh config not found, using defaults"
            )
            zenoh_session = zenoh.open(zenoh.Config())

        logger.info(f"Process {os.getpid()}: Zenoh session initialized successfully")
        return zenoh_session

    except Exception as e:
        logger.error(f"Process {os.getpid()}: Failed to initialize Zenoh session: {e}")
        raise RuntimeError(f"Zenoh session initialization failed: {e}") from e


def get_default_zenoh_config() -> str | None:
    """Gets the default zenoh configuration file path.

    Returns:
        Path to default config file if it exists, None otherwise.
    """
    default_path = dexcontrol.COMM_CFG_PATH
    if not default_path.exists():
        logger.warning(f"Zenoh config file not found at {default_path}")
        logger.warning("Please use dextop to set up the zenoh config file")
        return None
    return str(default_path)
