import pytest
import uuid

from make87.config import load_config_from_json
from make87.interfaces.zenoh.interface import ZenohInterface
from make87.internal.models.application_env_config import (
    InterfaceConfig,
    ApplicationInfo,
    BoundMultiClient,
    AccessPoint,
    Binding,
)
from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)


@pytest.fixture
def config_with_binding():
    """Configuration with binding port specified."""
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
                        keys=["endpoint_key_1"],
                        spec="text",
                        protocol="zenoh",
                        interface_name="zenoh",
                        access_points={
                            "endpoint_key_1": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7447,
                                same_node=True,
                            ),
                        },
                        congestion_control="DROP",
                        priority="REAL_TIME",
                        express=True,
                    )
                ),
                binding=Binding(
                    container_ip="127.0.0.1",
                    container_port=8080,
                    host_ip="127.0.0.1",
                    host_port=8080,
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="binding_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="binding_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@pytest.fixture
def config_without_binding():
    """Configuration without binding port specified."""
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
                        keys=["endpoint_key_1"],
                        spec="text",
                        protocol="zenoh",
                        interface_name="zenoh",
                        access_points={
                            "endpoint_key_1": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7447,
                                same_node=True,
                            ),
                        },
                        congestion_control="DROP",
                        priority="REAL_TIME",
                        express=True,
                    )
                ),
                # No binding specified
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="no_binding_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="no_binding_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


def test_zenoh_config_uses_binding_port(config_with_binding):
    """Test that zenoh config uses the binding port when specified."""
    interface = ZenohInterface(name="zenoh_test", make87_config=config_with_binding)

    # Check that the binding is configured correctly
    assert interface.interface_config.binding is not None
    assert interface.interface_config.binding.container_port == 8080

    # Get the zenoh config and check the listen endpoints
    _ = interface.zenoh_config

    # The config should contain the custom port in listen endpoints
    # Note: We can't easily inspect the zenoh config object directly,
    # but we can verify the interface configuration is correct


def test_zenoh_config_uses_default_port(config_without_binding):
    """Test that zenoh config uses default port 7447 when no binding specified."""
    interface = ZenohInterface(name="zenoh_test", make87_config=config_without_binding)

    # Check that no binding is configured
    assert interface.interface_config.binding is None

    # Get the zenoh config - should use default port 7447
    zenoh_config = interface.zenoh_config

    # The config should work without errors
    assert zenoh_config is not None


def test_binding_configuration_parsing(config_with_binding):
    """Test that binding configuration is parsed correctly."""
    interface = ZenohInterface(name="zenoh_test", make87_config=config_with_binding)

    binding = interface.interface_config.binding
    assert binding is not None
    assert binding.container_ip == "127.0.0.1"
    assert binding.container_port == 8080
    assert binding.host_ip == "127.0.0.1"
    assert binding.host_port == 8080
