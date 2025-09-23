import pytest
import uuid
from unittest.mock import patch

from make87.config import load_config_from_json
from make87.interfaces.rerun.interface import RerunInterface
from make87.internal.models.application_env_config import (
    InterfaceConfig,
    ApplicationInfo,
    BoundServer,
    Binding,
)
from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)


@pytest.fixture
def server_config_with_binding():
    """Configuration with server binding port specified."""
    application_config_in = ApplicationConfig(
        interfaces=dict(
            rerun_test=InterfaceConfig(
                name="rerun_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients={},
                servers=dict(
                    rerun_server=BoundServer(
                        name="rerun_server_service",
                        key="rerun_server_key",
                        spec="rerun_server_spec",
                        interface_name="rerun",
                        protocol="grpc",
                        memory_limit=1073741824,  # 1GB
                        playback_behavior="NewestFirst",
                        binding=Binding(
                            container_ip="127.0.0.1",
                            container_port=9999,
                            host_ip="127.0.0.1",
                            host_port=9999,
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
            deployed_application_name="rerun_port_conflict_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="rerun_port_conflict_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@pytest.fixture
def server_config_without_binding():
    """Configuration without server binding port specified."""
    application_config_in = ApplicationConfig(
        interfaces=dict(
            rerun_test=InterfaceConfig(
                name="rerun_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients={},
                servers=dict(
                    rerun_server=BoundServer(
                        name="rerun_server_service",
                        key="rerun_server_key",
                        spec="rerun_server_spec",
                        interface_name="rerun",
                        protocol="grpc",
                        memory_limit=1073741824,  # 1GB
                        playback_behavior="NewestFirst",
                        # No binding specified - will use default port 9876
                    )
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="rerun_default_port_conflict_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="rerun_default_port_conflict_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@patch("make87.interfaces.rerun.interface.is_port_in_use")
def test_rerun_configured_binding_port_conflict(mock_is_port_in_use, server_config_with_binding):
    """Test that RuntimeError is raised when configured binding port is in use."""
    # Mock that port 9999 is in use
    mock_is_port_in_use.return_value = True

    interface = RerunInterface(name="rerun_test", make87_config=server_config_with_binding)

    with pytest.raises(RuntimeError) as exc_info:
        # This should trigger the port check and raise an exception
        _ = interface.get_server_recording_stream("rerun_server")

    error_message = str(exc_info.value)
    assert "service binding port 9999 is already in use" in error_message
    assert "Cannot start Rerun server" in error_message

    # Verify the mock was called with the correct port
    mock_is_port_in_use.assert_called_with(9999)


@patch("make87.interfaces.rerun.interface.is_port_in_use")
def test_rerun_default_port_conflict(mock_is_port_in_use, server_config_without_binding):
    """Test that RuntimeError is raised when default port 9876 is in use."""
    # Mock that port 9876 is in use
    mock_is_port_in_use.return_value = True

    interface = RerunInterface(name="rerun_test", make87_config=server_config_without_binding)

    with pytest.raises(RuntimeError) as exc_info:
        # This should trigger the port check and raise an exception
        _ = interface.get_server_recording_stream("rerun_server")

    error_message = str(exc_info.value)
    assert "default port 9876 is already in use" in error_message
    assert "Cannot start Rerun server" in error_message

    # Verify the mock was called with the correct port
    mock_is_port_in_use.assert_called_with(9876)


@patch("make87.interfaces.rerun.interface.is_port_in_use")
@patch("make87.interfaces.rerun.interface.rr.serve_grpc")
@patch("make87.interfaces.rerun.interface.rr.RecordingStream")
def test_rerun_port_available_success(
    mock_recording_stream, mock_serve_grpc, mock_is_port_in_use, server_config_with_binding
):
    """Test that interface works normally when port is available."""
    # Mock that port is available
    mock_is_port_in_use.return_value = False

    # Mock rerun components to avoid actually starting a server
    mock_recording_stream.return_value = "mock_recording_stream"
    mock_serve_grpc.return_value = "mock_server"

    interface = RerunInterface(name="rerun_test", make87_config=server_config_with_binding)

    # This should work without raising an exception
    recording = interface.get_server_recording_stream("rerun_server")
    assert recording == "mock_recording_stream"

    # Verify the mock was called with the correct port
    mock_is_port_in_use.assert_called_with(9999)


@patch("make87.interfaces.rerun.interface.is_port_in_use")
def test_rerun_error_message_differentiation(
    mock_is_port_in_use, server_config_with_binding, server_config_without_binding
):
    """Test that error messages correctly identify configured vs default ports."""
    mock_is_port_in_use.return_value = True

    # Test configured binding port error
    interface_with_binding = RerunInterface(name="rerun_test", make87_config=server_config_with_binding)
    with pytest.raises(RuntimeError) as exc_info:
        _ = interface_with_binding.get_server_recording_stream("rerun_server")

    assert "service binding port" in str(exc_info.value)

    # Test default port error
    interface_without_binding = RerunInterface(name="rerun_test", make87_config=server_config_without_binding)
    with pytest.raises(RuntimeError) as exc_info:
        _ = interface_without_binding.get_server_recording_stream("rerun_server")

    assert "default port" in str(exc_info.value)
