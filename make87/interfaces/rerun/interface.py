"""Rerun interface implementation.

This module provides the RerunInterface class which implements the make87
messaging interface using the Rerun protocol. It supports both client connections
to existing Rerun servers and hosting Rerun servers locally.
"""

import hashlib
import logging
import uuid
from typing import List

from make87.interfaces.base import InterfaceBase
from make87.interfaces.rerun.model import RerunGRpcClientConfig, RerunGRpcServerConfig
import rerun as rr

logger = logging.getLogger(__name__)


def _deterministic_uuid_v4_from_string(val: str) -> uuid.UUID:
    """Generate a deterministic UUID v4 from a string value.

    Creates a UUID v4 by hashing the input string with SHA-256 and using
    the first 16 bytes as the UUID, with proper version and variant bits set.
    This ensures the same input string always produces the same UUID.

    Args:
        val: The string value to generate a UUID from

    Returns:
        A deterministic UUID v4 based on the input string

    Note:
        This function creates consistent recording IDs for Rerun sessions
        based on the system ID, ensuring reproducible recordings.
    """
    h = hashlib.sha256(val.encode()).digest()
    b = bytearray(h[:16])
    b[6] = (b[6] & 0x0F) | 0x40  # Version 4
    b[8] = (b[8] & 0x3F) | 0x80  # Variant RFC 4122
    return uuid.UUID(bytes=bytes(b))


class RerunInterface(InterfaceBase):
    """Concrete Rerun implementation of the make87 messaging interface.

    This class provides a Rerun-based implementation of the make87 messaging
    interface, supporting both client connections to existing Rerun servers
    and hosting Rerun servers locally.

    The interface handles automatic configuration of recording streams,
    deterministic recording IDs, and proper gRPC connection setup.
    """

    def get_client_recording_stream(self, name: str):
        """Create a Rerun recording stream connected to a gRPC server.

        Creates and configures a Rerun recording stream that connects to an existing
        Rerun server via gRPC using the specified client configuration.

        Args:
            name: The name of the client service configuration to use

        Returns:
            Configured rerun.RecordingStream instance connected to the server

        Raises:
            ClientServiceNotFoundError: If the client service is not found
            RerunNotInstalledError: If rerun package is not installed
            RerunInterfaceError: If connection or configuration fails

        Example:
            >>> interface = RerunInterface("my_interface")
            >>> recording = interface.get_client_recording_stream("rerun_client")
            >>> recording.log("world/points", rr.Points3D([[0, 0, 0], [1, 1, 1]]))
        """
        client_config = self.get_interface_type_by_name(name=name, iface_type="CLI")

        # Handle nested model_extra structure if present
        extra_config = client_config.model_extra
        if isinstance(extra_config, dict) and "model_extra" in extra_config:
            extra_config = extra_config["model_extra"]
        rerun_config = RerunGRpcClientConfig.model_validate(extra_config)

        # Configure the chunk batcher
        batcher_config = rr.ChunkBatcherConfig()
        batcher_config.flush_tick = rerun_config.batcher_config.flush_tick
        batcher_config.flush_num_bytes = rerun_config.batcher_config.flush_num_bytes
        batcher_config.flush_num_rows = rerun_config.batcher_config.flush_num_rows

        system_id = self._config.application_info.system_id

        # Create recording stream with deterministic ID and batcher config
        recording = rr.RecordingStream(
            application_id=system_id,
            recording_id=_deterministic_uuid_v4_from_string(system_id),
            batcher_config=batcher_config,
        )

        # Connect to gRPC server
        rr.connect_grpc(
            f"rerun+http://{client_config.vpn_ip}:{client_config.vpn_port}/proxy",
            recording=recording,
        )

        return recording

    def get_multi_client_recording_streams(self, name: str) -> List:
        """Create multiple Rerun recording streams connected to gRPC servers.

        Creates and configures multiple Rerun recording streams based on the
        multi-client configuration, with each stream connecting to a different
        server endpoint.

        Args:
            name: The name of the multi-client service configuration to use

        Returns:
            List of configured rerun.RecordingStream instances, one for each endpoint

        Raises:
            KeyError: If the multi-client service is not found
            RerunNotInstalledError: If rerun package is not installed
            RerunInterfaceError: If connection or configuration fails

        Example:
            >>> interface = RerunInterface("my_interface")
            >>> recordings = interface.get_multi_client_recording_streams("multi_rerun_client")
            >>> for i, recording in enumerate(recordings):
            ...     recording.log(f"world/points_{i}", rr.Points3D([[i, i, i]]))
        """
        multi_client_config = self.get_interface_type_by_name(name=name, iface_type="MCLI")

        # Handle nested model_extra structure if present
        extra_config = multi_client_config.model_extra
        if isinstance(extra_config, dict) and "model_extra" in extra_config:
            extra_config = extra_config["model_extra"]
        rerun_config = RerunGRpcClientConfig.model_validate(extra_config)

        # Configure the chunk batcher
        batcher_config = rr.ChunkBatcherConfig()
        batcher_config.flush_tick = rerun_config.batcher_config.flush_tick
        batcher_config.flush_num_bytes = rerun_config.batcher_config.flush_num_bytes
        batcher_config.flush_num_rows = rerun_config.batcher_config.flush_num_rows

        system_id = self._config.application_info.system_id

        recording_streams = []
        for i, key in enumerate(multi_client_config.keys):
            # Get the access point for this key
            access_point = multi_client_config.access_points[key]

            # Create unique recording stream for each endpoint
            recording_id = _deterministic_uuid_v4_from_string(f"{system_id}_{key}_{i}")
            recording = rr.RecordingStream(
                application_id=f"{system_id}_{key}",
                recording_id=recording_id,
                batcher_config=batcher_config,
            )

            # Connect to gRPC server using the access point
            rr.connect_grpc(
                f"rerun+http://{access_point.vpn_ip}:{access_point.vpn_port}/proxy",
                recording=recording,
            )

            recording_streams.append(recording)

        return recording_streams

    def get_multi_client(self, name: str) -> List:
        """Alias for get_multi_client_recording_streams for consistency with other interfaces.

        Args:
            name: The name of the multi-client service configuration to use

        Returns:
            List of configured rerun.RecordingStream instances, one for each endpoint
        """
        return self.get_multi_client_recording_streams(name)

    def get_server_recording_stream(self, name: str):
        """Create a Rerun recording stream that hosts a gRPC server.

        Creates and configures a Rerun recording stream that hosts its own
        gRPC server using the specified server configuration.

        Args:
            name: The name of the server service configuration to use

        Returns:
            Configured rerun.RecordingStream instance hosting a server

        Raises:
            RerunInterfaceError: If server creation or configuration fails

        Example:
            >>> interface = RerunInterface("my_interface")
            >>> recording = interface.get_server_recording_stream("rerun_server")
            >>> recording.log("world/points", rr.Points3D([[0, 0, 0], [1, 1, 1]]))
        """
        server_config = self.get_interface_type_by_name(name=name, iface_type="SRV")

        extra_config = server_config.model_extra
        if isinstance(extra_config, dict) and "model_extra" in extra_config:
            extra_config = extra_config["model_extra"]
        rerun_config = RerunGRpcServerConfig.model_validate(extra_config)

        # Configure memory limit
        if rerun_config.memory_limit is not None:
            # Convert bytes to string format (e.g., "1GB", "512MB")
            if rerun_config.memory_limit >= 1024**3:
                memory_limit = f"{rerun_config.memory_limit // (1024**3)}GB"
            elif rerun_config.memory_limit >= 1024**2:
                memory_limit = f"{rerun_config.memory_limit // (1024**2)}MB"
            else:
                memory_limit = f"{rerun_config.memory_limit}B"
        else:
            memory_limit = "25%"  # Default memory limit

        system_id = self._config.application_info.system_id

        # Create recording stream with deterministic ID
        recording = rr.RecordingStream(
            application_id=system_id,
            recording_id=_deterministic_uuid_v4_from_string(system_id),
        )

        # Configure playback behavior
        newest_first = rerun_config.playback_behavior.value == "NewestFirst"

        # Port resolution hierarchy: service binding -> interface binding -> default port
        grpc_port = 9876

        if server_config.binding is not None:
            grpc_port = server_config.binding.container_port
        elif self.interface_config.binding is not None:
            grpc_port = self.interface_config.binding.container_port

        # Start gRPC server
        _ = rr.serve_grpc(
            grpc_port=grpc_port,
            server_memory_limit=memory_limit,
            newest_first=newest_first,
            recording=recording,
        )

        return recording
