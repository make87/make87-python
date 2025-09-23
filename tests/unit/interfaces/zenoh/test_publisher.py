import pytest
import uuid

from make87.config import load_config_from_json
from make87.interfaces.zenoh.interface import ZenohInterface
from make87.internal.models.application_env_config import InterfaceConfig, ApplicationInfo, BoundPublisher
from make87.models import ApplicationConfig, MountedPeripherals


@pytest.fixture
def pub_config():
    application_config_in = ApplicationConfig(
        interfaces=dict(
            zenoh_test=InterfaceConfig(
                name="zenoh_test",
                subscribers={},
                publishers=dict(
                    HELLO_WORLD_MESSAGE=BoundPublisher(
                        topic_name="HELLO_WORLD_MESSAGE",
                        topic_key="my_topic_key",
                        protocol="zenoh",
                        message_type="make87_messages.text.text_plain.PlainText",
                        congestion_control="DROP",
                        priority="REAL_TIME",
                        express=True,
                        reliability="BEST_EFFORT",
                    )
                ),
                requesters={},
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

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@pytest.fixture
def zenoh_interface(pub_config):
    iface = ZenohInterface(name="zenoh_test", make87_config=pub_config)
    return iface


def test_get_publisher(zenoh_interface):
    assert zenoh_interface.get_publisher("HELLO_WORLD_MESSAGE") is not None


def test_get_subscriber(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_subscriber("HELLO_WORLD_MESSAGE")


def test_get_requester(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_querier("HELLO_WORLD_MESSAGE")


def test_get_provider(zenoh_interface):
    with pytest.raises(KeyError):
        zenoh_interface.get_queryable("HELLO_WORLD_MESSAGE")
