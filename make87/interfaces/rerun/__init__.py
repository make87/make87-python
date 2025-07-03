import hashlib
import uuid
from typing import Optional

from make87.config import load_config_from_env
from make87.models import ApplicationConfig


def init_and_connect_grpc(interface_name: str, client_name: str, make87_config: Optional[ApplicationConfig] = None):
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
    h = hashlib.sha256(val.encode()).digest()
    b = bytearray(h[:16])
    b[6] = (b[6] & 0x0F) | 0x40  # Version 4
    b[8] = (b[8] & 0x3F) | 0x80  # Variant RFC 4122
    return uuid.UUID(bytes=bytes(b))
