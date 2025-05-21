import pytest
import uuid

from make87.interfaces.zenoh.interface import ZenohInterface
from make87.models.application_env_config import (
    ApplicationEnvConfig,
    TopicConfigs,
    TopicSubConfig,
    EndpointConfigs,
    ServiceConfigs,
    URLMapping,
    MountedPeripherals,
)


@pytest.fixture
def sub_config():
    return ApplicationEnvConfig(
        topics=TopicConfigs(
            topics=[
                TopicSubConfig(
                    topic_name="HELLO_WORLD_MESSAGE",
                    topic_key="my_topic_key",
                    topic_type="SUB",
                    message_type="make87_messages.text.text_plain.PlainText",
                )
            ]
        ),
        endpoints=EndpointConfigs(endpoints=[]),
        services=ServiceConfigs(services=[]),
        url_mapping=URLMapping(name_to_url={}),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        deployed_application_id=uuid.uuid4().hex,
        system_id=uuid.uuid4().hex,
        deployed_application_name="sub_app_1",
        is_release_version=True,
        make87_ip="10.10.0.1",
        port_config=[],
        application_id=uuid.uuid4().hex,
        application_name="sub_app",
    )


@pytest.fixture
def zenoh_interface(sub_config):
    iface = ZenohInterface(make87_config=sub_config)
    return iface


def test_get_subscriber(zenoh_interface):
    assert zenoh_interface.get_subscriber("HELLO_WORLD_MESSAGE") is not None


def test_get_publisher(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_publisher("HELLO_WORLD_MESSAGE")


def test_get_requester(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_requester("HELLO_WORLD_MESSAGE")


def test_get_provider(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_provider("HELLO_WORLD_MESSAGE")
