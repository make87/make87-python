import pytest
import uuid

from make87.interfaces.zenoh.interface import ZenohInterface
from make87.internal.models.application_env_config import (
    InterfaceConfig,
    BoundRequester,
    ApplicationInfo,
)
from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)


@pytest.fixture
def req_config():
    return ApplicationConfig(
        interfaces=dict(
            zenoh_test=InterfaceConfig(
                name="zenoh_test",
                subscribers={},
                publishers={},
                requesters=dict(
                    HELLO_WORLD_MESSAGE=BoundRequester(
                        endpoint_name="HELLO_WORLD_MESSAGE",
                        endpoint_key="my_endpoint_key",
                        protocol="zenoh",
                        requester_message_type="make87_messages.text.text_plain.PlainText",
                        provider_message_type="make87_messages.text.text_plain.PlainText",
                        vpn_ip="10.10.0.1",
                        vpn_port=12345,
                        same_node=True,
                    ),
                ),
                providers={},
                clients={},
                servers={},
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="sub_app_1",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="sub_app",
        ),
    )


@pytest.fixture
def zenoh_interface(req_config):
    iface = ZenohInterface(name="zenoh_test", make87_config=req_config)
    return iface


def test_get_requester(zenoh_interface):
    assert zenoh_interface.get_requester("HELLO_WORLD_MESSAGE") is not None


def test_get_publisher(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_publisher("HELLO_WORLD_MESSAGE")


def test_get_subscriber(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_subscriber("HELLO_WORLD_MESSAGE")


def test_get_provider(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_provider("HELLO_WORLD_MESSAGE")
