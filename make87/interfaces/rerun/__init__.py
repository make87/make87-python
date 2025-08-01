"""Rerun integration utilities for Make87 applications.

This module provides utilities for connecting Make87 applications to Rerun
for data visualization and logging. It handles automatic configuration
and connection setup based on the Make87 application configuration.
"""

import hashlib
import uuid
from typing import Optional

from make87.config import load_config_from_env
from make87.models import ApplicationConfig


def init_and_connect_grpc(interface_name: str, client_name: str, make87_config: Optional[ApplicationConfig] = None):
    """Initialize Rerun and connect via gRPC using Make87 configuration.

    This function initializes a Rerun session and connects to a Rerun server
    via gRPC using configuration from the Make87 application config. It sets
    up the application ID and creates a deterministic recording ID based on
    the system ID.

    Args:
        interface_name: The name of the interface configuration to use
        client_name: The name of the Rerun client configuration
        make87_config: Optional ApplicationConfig instance. If not provided,
            configuration will be loaded from the environment.

    Raises:
        ValueError: If the specified interface or client is not found in configuration
        ImportError: If rerun package is not installed

    Example:

        >>> import make87.interfaces.rerun as rerun_interface
        >>> rerun_interface.init_and_connect_grpc("rerun", "rerun-grpc-client")
        >>> # Now you can use rerun.log() functions
    """
    import rerun as rr

    if make87_config is None:
        make87_config = load_config_from_env()
    if interface_name not in make87_config.interfaces:
        raise ValueError(f"Interface '{interface_name}' not found in the configuration.")
    rerun_interface = make87_config.interfaces.get("rerun")
    system_id = make87_config.application_info.system_id
    rerun_client = rerun_interface.clients.get("rerun-grpc-client", None)
    if rerun_client is None:
        raise ValueError(f"Rerun client '{client_name}' not found in the configuration.")

    rr.init(application_id=system_id, recording_id=_deterministic_uuid_v4_from_string(val=system_id))
    rr.connect_grpc(f"rerun+http://{rerun_client.vpn_ip}:{rerun_client.vpn_port}/proxy")


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
        This function is used internally to create consistent recording IDs
        for Rerun sessions based on the system ID.
    """
    h = hashlib.sha256(val.encode()).digest()
    b = bytearray(h[:16])
    b[6] = (b[6] & 0x0F) | 0x40  # Version 4
    b[8] = (b[8] & 0x3F) | 0x80  # Variant RFC 4122
    return uuid.UUID(bytes=bytes(b))
