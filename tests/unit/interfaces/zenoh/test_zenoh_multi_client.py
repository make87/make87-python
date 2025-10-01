import pytest
import uuid

from make87.config import load_config_from_json
from make87.interfaces.zenoh.interface import ZenohInterface
from make87.internal.models.application_env_config import (
    InterfaceConfig,
    ApplicationInfo,
    BoundMultiClient,
    AccessPoint,
)
from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)


@pytest.fixture
def multi_client_config():
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
                multi_clients=dict(
                    MULTI_API_CLIENT=BoundMultiClient(
                        name="MULTI_API_CLIENT",
                        keys=["endpoint_key_1", "endpoint_key_2", "endpoint_key_3"],
                        spec="text",
                        protocol="zenoh",
                        interface_name="zenoh",
                        access_points={
                            "endpoint_key_1": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7447,
                                same_node=True,
                            ),
                            "endpoint_key_2": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7448,
                                same_node=True,
                            ),
                            "endpoint_key_3": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7449,
                                same_node=True,
                            ),
                        },
                        congestion_control="DROP",
                        priority="REAL_TIME",
                        express=True,
                    )
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="multi_client_app_1",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="multi_client_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@pytest.fixture
def zenoh_interface(multi_client_config):
    iface = ZenohInterface(name="zenoh_test", make87_config=multi_client_config)
    return iface


def test_get_multi_client(zenoh_interface):
    """Test that get_multi_client returns a list of queriers."""
    queriers = zenoh_interface.get_multi_client("MULTI_API_CLIENT")

    # Should return a list of queriers
    assert isinstance(queriers, list)

    # Should have 3 queriers (one for each endpoint key)
    assert len(queriers) == 3

    # Each item should be a Zenoh Querier
    for querier in queriers:
        assert hasattr(querier, "undeclare")  # Zenoh queriers have undeclare method


def test_get_multi_client_not_found(zenoh_interface):
    """Test that get_multi_client raises KeyError for non-existent multi-client."""
    with pytest.raises(KeyError):
        zenoh_interface.get_multi_client("NON_EXISTENT")


def test_get_regular_querier_fails_on_multi_config(zenoh_interface):
    """Test that regular get_querier fails when trying to access multi-client config."""
    with pytest.raises(KeyError):
        zenoh_interface.get_querier("MULTI_API_CLIENT")


def test_get_multi_client_fails_on_regular_config(zenoh_interface):
    """Test that get_multi_client fails when trying to access regular querier config."""
    with pytest.raises(KeyError):
        zenoh_interface.get_multi_client("REGULAR_CLIENT")


def test_multi_client_endpoint_keys(zenoh_interface):
    """Test that multi-client uses the correct endpoint keys."""
    # Get the configuration to verify the keys
    iface_config = zenoh_interface.get_interface_type_by_name("MULTI_API_CLIENT", "MCLI")

    # Should have 3 endpoint keys
    assert len(iface_config.keys) == 3
    assert "endpoint_key_1" in iface_config.keys
    assert "endpoint_key_2" in iface_config.keys
    assert "endpoint_key_3" in iface_config.keys

    # Should have matching access points
    assert len(iface_config.access_points) == 3
    assert "endpoint_key_1" in iface_config.access_points
    assert "endpoint_key_2" in iface_config.access_points
    assert "endpoint_key_3" in iface_config.access_points
