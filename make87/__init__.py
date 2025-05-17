import signal
import threading

from make87.endpoints import (
    ProviderNotAvailable,
    ResponseTimeout,
    TypedProvider,
    TypedRequester,
    get_provider,
    get_requester,
    resolve_endpoint_name,
)
from make87.peripherals import (
    resolve_peripheral_name,
)
from make87.storage import (
    generate_public_url,
    get_application_storage_path,
    get_deployed_application_storage_path,
    get_organization_storage_path,
    get_system_storage_path,
)
from make87.utils import (
    APPLICATION_ID,
    APPLICATION_NAME,
    DEPLOYED_APPLICATION_ID,
    DEPLOYED_APPLICATION_NAME,
    DEPLOYED_SYSTEM_ID,
)

__all__ = [
    "ProviderNotAvailable",
    "ResponseTimeout",
    "TypedProvider",
    "TypedRequester",
    "get_provider",
    "get_requester",
    "resolve_endpoint_name",
    "resolve_peripheral_name",
    "get_system_storage_path",
    "get_organization_storage_path",
    "get_application_storage_path",
    "get_deployed_application_storage_path",
    "generate_public_url",
    "APPLICATION_ID",
    "APPLICATION_NAME",
    "DEPLOYED_APPLICATION_NAME",
    "DEPLOYED_APPLICATION_ID",
    "DEPLOYED_SYSTEM_ID",
]


def run_forever():
    stop_event = threading.Event()

    def handle_stop(signum, frame):
        stop_event.set()

    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)  # Optional: Ctrl-C

    stop_event.wait()
    # Perform any cleanup here if needed
