import pytest
import uuid

from make87.config import load_config_from_json
from make87.interfaces.zenoh.interface import ZenohInterface
from make87.internal.models.application_env_config import (
    InterfaceConfig,
    ApplicationInfo,
    BoundMultiSubscriber,
    AccessPoint,
)
from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)


@pytest.fixture
def multi_sub_config():
    application_config_in = ApplicationConfig(
        interfaces=dict(
            zenoh_test=InterfaceConfig(
                name="zenoh_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients={},
                servers={},
                multi_subscribers=dict(
                    MULTI_HELLO_WORLD=BoundMultiSubscriber(
                        topic_name="MULTI_HELLO_WORLD",
                        topic_keys=["topic_key_1", "topic_key_2", "topic_key_3"],
                        message_type="make87_messages.text.text_plain.PlainText",
                        protocol="zenoh",
                        encoding="utf-8",
                        interface_name="zenoh",
                        access_points={
                            "topic_key_1": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7447,
                                same_node=True,
                            ),
                            "topic_key_2": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7448,
                                same_node=True,
                            ),
                            "topic_key_3": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7449,
                                same_node=True,
                            ),
                        },
                        handler=dict(
                            handler_type="FIFO",
                            capacity=10,
                        ),
                    )
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="multi_sub_app_1",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="multi_sub_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@pytest.fixture
def zenoh_interface(multi_sub_config):
    iface = ZenohInterface(name="zenoh_test", make87_config=multi_sub_config)
    return iface


def test_get_multi_subscriber(zenoh_interface):
    """Test that get_multi_subscriber returns a list of subscribers."""
    subscribers = zenoh_interface.get_multi_subscriber("MULTI_HELLO_WORLD")

    # Should return a list of subscribers
    assert isinstance(subscribers, list)

    # Should have 3 subscribers (one for each topic key)
    assert len(subscribers) == 3

    # Each item should be a Zenoh Subscriber
    for subscriber in subscribers:
        assert hasattr(subscriber, "undeclare")  # Zenoh subscribers have undeclare method


def test_get_multi_subscriber_not_found(zenoh_interface):
    """Test that get_multi_subscriber raises KeyError for non-existent multi-subscriber."""
    with pytest.raises(KeyError):
        zenoh_interface.get_multi_subscriber("NON_EXISTENT")


def test_get_multi_subscriber_with_custom_handler(zenoh_interface):
    """Test that get_multi_subscriber works with custom handler."""

    def custom_handler(sample):
        print(f"Received: {sample.value}")

    subscribers = zenoh_interface.get_multi_subscriber("MULTI_HELLO_WORLD", handler=custom_handler)

    # Should still return a list of subscribers
    assert isinstance(subscribers, list)
    assert len(subscribers) == 3


def test_get_regular_subscriber_fails_on_multi_config(zenoh_interface):
    """Test that regular get_subscriber fails when trying to access multi-subscriber config."""
    with pytest.raises(KeyError):
        zenoh_interface.get_subscriber("MULTI_HELLO_WORLD")


def test_get_multi_subscriber_fails_on_regular_config(zenoh_interface):
    """Test that get_multi_subscriber fails when trying to access regular subscriber config."""
    with pytest.raises(KeyError):
        zenoh_interface.get_multi_subscriber("HELLO_WORLD_MESSAGE")
