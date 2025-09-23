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
def config_with_service_binding():
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
                            container_port=9999,  # Service-specific port
                            host_ip="127.0.0.1",
                            host_port=9999,
                        ),
                    )
                ),
                binding=Binding(
                    container_ip="127.0.0.1",
                    container_port=8888,  # Interface-level port
                    host_ip="127.0.0.1",
                    host_port=8888,
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="service_binding_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="service_binding_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@pytest.fixture
def config_with_interface_binding_only():
    """Configuration with only interface binding port specified."""
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
                        # No service binding specified
                    )
                ),
                binding=Binding(
                    container_ip="127.0.0.1",
                    container_port=8888,  # Interface-level port
                    host_ip="127.0.0.1",
                    host_port=8888,
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="interface_binding_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="interface_binding_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@pytest.fixture
def config_with_no_bindings():
    """Configuration without any binding ports specified."""
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
                        # No service binding specified
                    )
                ),
                # No interface binding specified
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="no_bindings_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="no_bindings_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@patch("make87.interfaces.rerun.interface.is_port_in_use")
@patch("make87.interfaces.rerun.interface.rr.serve_grpc")
@patch("make87.interfaces.rerun.interface.rr.RecordingStream")
def test_service_binding_takes_priority(
    mock_recording_stream, mock_serve_grpc, mock_is_port_in_use, config_with_service_binding
):
    """Test that service binding port takes priority over interface binding."""
    # Mock that ports are available
    mock_is_port_in_use.return_value = False

    # Mock rerun components
    mock_recording_stream.return_value = "mock_recording_stream"
    mock_serve_grpc.return_value = "mock_server"

    interface = RerunInterface(name="rerun_test", make87_config=config_with_service_binding)

    # Get the recording stream - should use service binding port (9999)
    _ = interface.get_server_recording_stream("rerun_server")

    # Verify the port check was called with service binding port
    mock_is_port_in_use.assert_called_with(9999)

    # Verify serve_grpc was called with service binding port
    mock_serve_grpc.assert_called_once()
    call_args = mock_serve_grpc.call_args
    assert call_args[1]["grpc_port"] == 9999


@patch("make87.interfaces.rerun.interface.is_port_in_use")
@patch("make87.interfaces.rerun.interface.rr.serve_grpc")
@patch("make87.interfaces.rerun.interface.rr.RecordingStream")
def test_interface_binding_used_when_no_service_binding(
    mock_recording_stream, mock_serve_grpc, mock_is_port_in_use, config_with_interface_binding_only
):
    """Test that interface binding port is used when service binding is not specified."""
    # Mock that ports are available
    mock_is_port_in_use.return_value = False

    # Mock rerun components
    mock_recording_stream.return_value = "mock_recording_stream"
    mock_serve_grpc.return_value = "mock_server"

    interface = RerunInterface(name="rerun_test", make87_config=config_with_interface_binding_only)

    # Get the recording stream - should use interface binding port (8888)
    _ = interface.get_server_recording_stream("rerun_server")

    # Verify the port check was called with interface binding port
    mock_is_port_in_use.assert_called_with(8888)

    # Verify serve_grpc was called with interface binding port
    mock_serve_grpc.assert_called_once()
    call_args = mock_serve_grpc.call_args
    assert call_args[1]["grpc_port"] == 8888


@patch("make87.interfaces.rerun.interface.is_port_in_use")
@patch("make87.interfaces.rerun.interface.rr.serve_grpc")
@patch("make87.interfaces.rerun.interface.rr.RecordingStream")
def test_default_port_used_when_no_bindings(
    mock_recording_stream, mock_serve_grpc, mock_is_port_in_use, config_with_no_bindings
):
    """Test that default port 9876 is used when no bindings are specified."""
    # Mock that ports are available
    mock_is_port_in_use.return_value = False

    # Mock rerun components
    mock_recording_stream.return_value = "mock_recording_stream"
    mock_serve_grpc.return_value = "mock_server"

    interface = RerunInterface(name="rerun_test", make87_config=config_with_no_bindings)

    # Get the recording stream - should use default port (9876)
    _ = interface.get_server_recording_stream("rerun_server")

    # Verify the port check was called with default port
    mock_is_port_in_use.assert_called_with(9876)

    # Verify serve_grpc was called with default port
    mock_serve_grpc.assert_called_once()
    call_args = mock_serve_grpc.call_args
    assert call_args[1]["grpc_port"] == 9876


@patch("make87.interfaces.rerun.interface.is_port_in_use")
def test_service_binding_port_conflict_error_message(mock_is_port_in_use, config_with_service_binding):
    """Test that port conflict error message identifies service binding correctly."""
    # Mock that port is in use
    mock_is_port_in_use.return_value = True

    interface = RerunInterface(name="rerun_test", make87_config=config_with_service_binding)

    with pytest.raises(RuntimeError) as exc_info:
        _ = interface.get_server_recording_stream("rerun_server")

    error_message = str(exc_info.value)
    assert "service binding port 9999 is already in use" in error_message
    assert "Cannot start Rerun server" in error_message


@patch("make87.interfaces.rerun.interface.is_port_in_use")
def test_interface_binding_port_conflict_error_message(mock_is_port_in_use, config_with_interface_binding_only):
    """Test that port conflict error message identifies interface binding correctly."""
    # Mock that port is in use
    mock_is_port_in_use.return_value = True

    interface = RerunInterface(name="rerun_test", make87_config=config_with_interface_binding_only)

    with pytest.raises(RuntimeError) as exc_info:
        _ = interface.get_server_recording_stream("rerun_server")

    error_message = str(exc_info.value)
    assert "interface binding port 8888 is already in use" in error_message
    assert "Cannot start Rerun server" in error_message


@patch("make87.interfaces.rerun.interface.is_port_in_use")
def test_default_port_conflict_error_message(mock_is_port_in_use, config_with_no_bindings):
    """Test that port conflict error message identifies default port correctly."""
    # Mock that port is in use
    mock_is_port_in_use.return_value = True

    interface = RerunInterface(name="rerun_test", make87_config=config_with_no_bindings)

    with pytest.raises(RuntimeError) as exc_info:
        _ = interface.get_server_recording_stream("rerun_server")

    error_message = str(exc_info.value)
    assert "default port 9876 is already in use" in error_message
    assert "Cannot start Rerun server" in error_message
