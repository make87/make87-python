from time import sleep

from make87.endpoints import (  # noqa
    ProviderNotAvailable,
    TypedProvider,
    TypedRequester,
    get_provider,
    get_requester,
    resolve_endpoint_name,
)
from make87.endpoints import _EndpointManager
from make87.peripherals import _PeripheralManager
from make87.peripherals import resolve_peripheral_name  # noqa
from make87.session import _SessionManager
from make87.topics import (  # noqa
    MultiSubscriber,
    TypedPublisher,
    TypedSubscriber,
    get_publisher,
    get_subscriber,
    resolve_topic_name,
    get_multi_subscriber,
    GroupOn,
)
from make87.topics import _TopicManager
from make87.utils import (
    Metadata,
    MessageWithMetadata,
    create_header,
    header_from_message,
    APPLICATION_ID,
    APPLICATION_NAME,
    DEPLOYED_APPLICATION_NAME,
    DEPLOYED_APPLICATION_ID,
    DEPLOYED_SYSTEM_ID,
)
from make87.storage import (
    get_system_storage_path,
    get_organization_storage_path,
    get_application_storage_path,
    get_deployed_application_storage_path,
    generate_public_url,
)
from make87.application_config import get_config_value

__all__ = [
    "MessageWithMetadata",
    "Metadata",
    "MultiSubscriber",
    "ProviderNotAvailable",
    "TypedProvider",
    "TypedPublisher",
    "TypedRequester",
    "TypedSubscriber",
    "get_provider",
    "get_publisher",
    "get_requester",
    "get_subscriber",
    "get_multi_subscriber",
    "initialize",
    "resolve_endpoint_name",
    "resolve_peripheral_name",
    "resolve_topic_name",
    "get_config_value",
    "get_system_storage_path",
    "get_organization_storage_path",
    "get_application_storage_path",
    "get_deployed_application_storage_path",
    "generate_public_url",
    "GroupOn",
    "create_header",
    "header_from_message",
    "APPLICATION_ID",
    "APPLICATION_NAME",
    "DEPLOYED_APPLICATION_NAME",
    "DEPLOYED_APPLICATION_ID",
    "DEPLOYED_SYSTEM_ID",
]


def initialize():
    """Initializes the Make87 SDK. Must be called before using any other SDK functions."""
    # Initialize the session manager
    _SessionManager.get_instance().initialize()
    _TopicManager.get_instance().initialize()
    _EndpointManager.get_instance().initialize()
    _PeripheralManager.get_instance().initialize()


def loop():
    while True:
        sleep(10)
