import pytest
import uuid

from make87.interfaces.zenoh.interface import ZenohInterface
from make87.models.application_env_config import (
    ApplicationEnvConfig,
    URLMapping,
    MountedPeripherals,
    TopicConfigPub,
    TopicType,
)


@pytest.fixture
def pub_config():
    return ApplicationEnvConfig(
        topics=[
            TopicConfigPub(
                topic_name="HELLO_WORLD_MESSAGE",
                topic_key="my_topic_key",
                topic_type=TopicType.PUB,
                message_type="make87_messages.text.text_plain.PlainText",
            )
        ],
        endpoints=[],
        services=[],
        url_mapping=URLMapping(name_to_url={}),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        deployed_application_id=uuid.uuid4().hex,
        system_id=uuid.uuid4().hex,
        deployed_application_name="pub_app_1",
        is_release_version=True,
        vpn_ip="10.10.0.1",
        port_config=[],
        application_id=uuid.uuid4().hex,
        application_name="pub_app",
    )


@pytest.fixture
def zenoh_interface(pub_config):
    iface = ZenohInterface(make87_config=pub_config)
    return iface


def test_get_publisher(zenoh_interface):
    assert zenoh_interface.get_publisher("HELLO_WORLD_MESSAGE") is not None


def test_get_subscriber(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_subscriber("HELLO_WORLD_MESSAGE")


def test_get_requester(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_requester("HELLO_WORLD_MESSAGE")


def test_get_provider(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_provider("HELLO_WORLD_MESSAGE")
