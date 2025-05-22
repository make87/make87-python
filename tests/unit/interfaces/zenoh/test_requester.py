import pytest
import uuid

from make87.interfaces.zenoh.interface import ZenohInterface
from make87.models import (
    ApplicationConfig,
    URLMapping,
    MountedPeripherals,
    EndpointConfigReq,
    EndpointConfig,
    EndpointTypeReq,
)


@pytest.fixture
def req_config():
    return ApplicationConfig(
        topics=[],
        endpoints=[
            EndpointConfig(
                root=EndpointConfigReq(
                    endpoint_name="HELLO_WORLD_MESSAGE",
                    endpoint_key="my_endpoint_key",
                    endpoint_type=EndpointTypeReq.REQ,
                    requester_message_type="make87_messages.text.text_plain.PlainText",
                    provider_message_type="make87_messages.text.text_plain.PlainText",
                )
            )
        ],
        services=[],
        url_mapping=URLMapping(name_to_url={}),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        deployed_application_id=uuid.uuid4().hex,
        system_id=uuid.uuid4().hex,
        deployed_application_name="req_app_1",
        is_release_version=True,
        vpn_ip="10.10.0.1",
        port_config=[],
        application_id=uuid.uuid4().hex,
        application_name="req_app",
    )


@pytest.fixture
def zenoh_interface(req_config):
    iface = ZenohInterface(make87_config=req_config)
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
