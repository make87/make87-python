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


@patch("make87.interfaces.rerun.interface.rr.serve_grpc")
@patch("make87.interfaces.rerun.interface.rr.RecordingStream")
def test_service_binding_takes_priority(mock_recording_stream, mock_serve_grpc, config_with_service_binding):
    """Test that service binding port takes priority over interface binding."""
    # Mock rerun components
    mock_recording_stream.return_value = "mock_recording_stream"
    mock_serve_grpc.return_value = "mock_server"

    interface = RerunInterface(name="rerun_test", make87_config=config_with_service_binding)

    # Get the recording stream - should use service binding port (9999)
    recording = interface.get_server_recording_stream("rerun_server")

    # Verify serve_grpc was called with service binding port
    mock_serve_grpc.assert_called_once()
    call_args = mock_serve_grpc.call_args
    assert call_args[1]["grpc_port"] == 9999
    assert recording == "mock_recording_stream"


@patch("make87.interfaces.rerun.interface.rr.serve_grpc")
@patch("make87.interfaces.rerun.interface.rr.RecordingStream")
def test_interface_binding_used_when_no_service_binding(
    mock_recording_stream, mock_serve_grpc, config_with_interface_binding_only
):
    """Test that interface binding port is used when service binding is not specified."""
    # Mock rerun components
    mock_recording_stream.return_value = "mock_recording_stream"
    mock_serve_grpc.return_value = "mock_server"

    interface = RerunInterface(name="rerun_test", make87_config=config_with_interface_binding_only)

    # Get the recording stream - should use interface binding port (8888)
    recording = interface.get_server_recording_stream("rerun_server")

    # Verify serve_grpc was called with interface binding port
    mock_serve_grpc.assert_called_once()
    call_args = mock_serve_grpc.call_args
    assert call_args[1]["grpc_port"] == 8888
    assert recording == "mock_recording_stream"


@patch("make87.interfaces.rerun.interface.rr.serve_grpc")
@patch("make87.interfaces.rerun.interface.rr.RecordingStream")
def test_default_port_used_when_no_bindings(mock_recording_stream, mock_serve_grpc, config_with_no_bindings):
    """Test that default port 9876 is used when no bindings are specified."""
    # Mock rerun components
    mock_recording_stream.return_value = "mock_recording_stream"
    mock_serve_grpc.return_value = "mock_server"

    interface = RerunInterface(name="rerun_test", make87_config=config_with_no_bindings)

    # Get the recording stream - should use default port (9876)
    recording = interface.get_server_recording_stream("rerun_server")

    # Verify serve_grpc was called with default port
    mock_serve_grpc.assert_called_once()
    call_args = mock_serve_grpc.call_args
    assert call_args[1]["grpc_port"] == 9876
    assert recording == "mock_recording_stream"


def test_port_hierarchy_configuration_parsing(
    config_with_service_binding, config_with_interface_binding_only, config_with_no_bindings
):
    """Test that port hierarchy configurations are parsed correctly."""
    # Service binding case
    interface_service = RerunInterface(name="rerun_test", make87_config=config_with_service_binding)
    server_config_service = interface_service.get_interface_type_by_name("rerun_server", "SRV")
    assert server_config_service.binding is not None
    assert server_config_service.binding.container_port == 9999
    assert interface_service.interface_config.binding is not None
    assert interface_service.interface_config.binding.container_port == 8888

    # Interface binding only case
    interface_interface = RerunInterface(name="rerun_test", make87_config=config_with_interface_binding_only)
    server_config_interface = interface_interface.get_interface_type_by_name("rerun_server", "SRV")
    assert server_config_interface.binding is None
    assert interface_interface.interface_config.binding is not None
    assert interface_interface.interface_config.binding.container_port == 8888

    # No bindings case
    interface_default = RerunInterface(name="rerun_test", make87_config=config_with_no_bindings)
    server_config_default = interface_default.get_interface_type_by_name("rerun_server", "SRV")
    assert server_config_default.binding is None
    assert interface_default.interface_config.binding is None
