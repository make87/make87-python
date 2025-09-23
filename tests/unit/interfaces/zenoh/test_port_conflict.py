import pytest
import uuid
from unittest.mock import patch

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
            deployed_application_name="port_conflict_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="port_conflict_test_app",
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
                # No binding specified - will use default port 7447
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="default_port_conflict_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="default_port_conflict_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@patch("make87.interfaces.zenoh.interface.is_port_in_use")
def test_configured_binding_port_conflict(mock_is_port_in_use, config_with_binding):
    """Test that RuntimeError is raised when configured binding port is in use."""
    # Mock that port 8080 is in use
    mock_is_port_in_use.return_value = True

    interface = ZenohInterface(name="zenoh_test", make87_config=config_with_binding)

    with pytest.raises(RuntimeError) as exc_info:
        # This should trigger the port check and raise an exception
        _ = interface.zenoh_config

    error_message = str(exc_info.value)
    assert "configured binding port 8080 is already in use" in error_message
    assert "Cannot start Zenoh interface" in error_message

    # Verify the mock was called with the correct port
    mock_is_port_in_use.assert_called_with(8080)


@patch("make87.interfaces.zenoh.interface.is_port_in_use")
def test_default_port_conflict(mock_is_port_in_use, config_without_binding):
    """Test that RuntimeError is raised when default port 7447 is in use."""
    # Mock that port 7447 is in use
    mock_is_port_in_use.return_value = True

    interface = ZenohInterface(name="zenoh_test", make87_config=config_without_binding)

    with pytest.raises(RuntimeError) as exc_info:
        # This should trigger the port check and raise an exception
        _ = interface.zenoh_config

    error_message = str(exc_info.value)
    assert "default port 7447 is already in use" in error_message
    assert "Cannot start Zenoh interface" in error_message

    # Verify the mock was called with the correct port
    mock_is_port_in_use.assert_called_with(7447)


@patch("make87.interfaces.zenoh.interface.is_port_in_use")
def test_port_available_success(mock_is_port_in_use, config_with_binding):
    """Test that interface works normally when port is available."""
    # Mock that port is available
    mock_is_port_in_use.return_value = False

    interface = ZenohInterface(name="zenoh_test", make87_config=config_with_binding)

    # This should work without raising an exception
    zenoh_config = interface.zenoh_config
    assert zenoh_config is not None

    # Verify the mock was called with the correct port
    mock_is_port_in_use.assert_called_with(8080)


@patch("make87.interfaces.zenoh.interface.is_port_in_use")
def test_error_message_differentiation(mock_is_port_in_use, config_with_binding, config_without_binding):
    """Test that error messages correctly identify configured vs default ports."""
    mock_is_port_in_use.return_value = True

    # Test configured binding port error
    interface_with_binding = ZenohInterface(name="zenoh_test", make87_config=config_with_binding)
    with pytest.raises(RuntimeError) as exc_info:
        _ = interface_with_binding.zenoh_config

    assert "configured binding port" in str(exc_info.value)

    # Test default port error
    interface_without_binding = ZenohInterface(name="zenoh_test", make87_config=config_without_binding)
    with pytest.raises(RuntimeError) as exc_info:
        _ = interface_without_binding.zenoh_config

    assert "default port" in str(exc_info.value)
