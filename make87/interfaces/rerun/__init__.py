"""Rerun integration for make87 applications.

This module provides both a modern interface class and legacy utility functions
for connecting make87 applications to Rerun for data visualization and logging.
It handles automatic configuration and connection setup based on the make87
application configuration.
"""

from make87.interfaces.rerun.interface import (
    RerunInterface,
)
from make87.interfaces.rerun.model import (
    PlaybackBehavior,
    RerunGRpcClientConfig,
    RerunGRpcServerConfig,
    ChunkBatcherConfig,
)

__all__ = [
    "RerunInterface",
    "PlaybackBehavior",
    "RerunGRpcClientConfig",
    "RerunGRpcServerConfig",
    "ChunkBatcherConfig",
]
