import pytest
import uuid

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
            deployed_application_name="rerun_binding_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="rerun_binding_test_app",
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
                        # No binding specified
                    )
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="rerun_no_binding_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="rerun_no_binding_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


def test_rerun_server_config_parsing_with_binding(server_config_with_binding):
    """Test that rerun server config with binding is parsed correctly."""
    interface = RerunInterface(name="rerun_test", make87_config=server_config_with_binding)

    # Check that the server config has binding
    server_config = interface.get_interface_type_by_name("rerun_server", "SRV")
    assert server_config.binding is not None
    assert server_config.binding.container_port == 9999
    assert server_config.binding.container_ip == "127.0.0.1"
    assert server_config.binding.host_ip == "127.0.0.1"
    assert server_config.binding.host_port == 9999


def test_rerun_server_config_parsing_without_binding(server_config_without_binding):
    """Test that rerun server config without binding is parsed correctly."""
    interface = RerunInterface(name="rerun_test", make87_config=server_config_without_binding)

    # Check that the server config has no binding
    server_config = interface.get_interface_type_by_name("rerun_server", "SRV")
    assert server_config.binding is None


def test_rerun_server_binding_configuration_structure(server_config_with_binding):
    """Test the structure of the binding configuration."""
    interface = RerunInterface(name="rerun_test", make87_config=server_config_with_binding)

    server_config = interface.get_interface_type_by_name("rerun_server", "SRV")
    binding = server_config.binding

    assert binding is not None
    assert hasattr(binding, "container_ip")
    assert hasattr(binding, "container_port")
    assert hasattr(binding, "host_ip")
    assert hasattr(binding, "host_port")

    # Verify port is an integer
    assert isinstance(binding.container_port, int)
    assert binding.container_port > 0


# Note: We don't test actual server creation because it would require
# the rerun package to be installed and would create actual network listeners.
# The above tests verify that the binding configuration is correctly parsed
# and accessible to the interface implementation.
