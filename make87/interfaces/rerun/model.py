"""Rerun interface model definitions.

This module defines configuration models for Rerun-based interfaces,
including client and server configuration for gRPC connections and
chunk batcher settings.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ChunkBatcherConfig(BaseModel):
    """Configuration for Rerun chunk batcher.

    Controls how data is batched before sending to the Rerun server
    for optimal performance and network efficiency.

    Attributes:
        flush_tick: Seconds between automatic flushes (default: 0.2)
        flush_num_bytes: Flush when buffer reaches this size in bytes (default: 1MiB)
        flush_num_rows: Flush when buffer reaches this number of rows (default: u64::MAX)
    """

    flush_tick: float = Field(default=0.2, description="Time interval in seconds between automatic flushes")
    flush_num_bytes: int = Field(default=1048576, description="Flush when buffer reaches this size in bytes")
    flush_num_rows: int = Field(
        default=18446744073709551615, description="Flush when buffer reaches this number of rows"
    )


class RerunGRpcClientConfig(BaseModel):
    """Configuration for Rerun gRPC client connections.

    Configures how the client connects to and communicates with
    a Rerun server via gRPC protocol.

    Attributes:
        batcher_config: Configuration for the chunk batcher
    """

    batcher_config: ChunkBatcherConfig = Field(default_factory=ChunkBatcherConfig)


class PlaybackBehavior(str, Enum):
    """Playback behavior for Rerun server.

    Defines how the server prioritizes data playback when clients connect.

    Attributes:
        OLDEST_FIRST: Start playing back all the old data first,
                     and only after start sending anything that happened since
        NEWEST_FIRST: Prioritize the newest arriving messages,
                     replaying the history later, starting with the newest
    """

    OLDEST_FIRST = "OldestFirst"
    NEWEST_FIRST = "NewestFirst"


class RerunGRpcServerConfig(BaseModel):
    """Configuration for Rerun gRPC server hosting.

    Configures how the server hosts Rerun data and manages
    memory limits and playback behavior for the recording stream.

    Attributes:
        memory_limit: Maximum memory usage in bytes (default: None for no limit)
        playback_behavior: How to prioritize data playback (default: OLDEST_FIRST)
    """

    memory_limit: Optional[int] = Field(default=None, description="Maximum memory usage in bytes")
    playback_behavior: PlaybackBehavior = Field(
        default=PlaybackBehavior.OLDEST_FIRST, description="Data playback prioritization"
    )
