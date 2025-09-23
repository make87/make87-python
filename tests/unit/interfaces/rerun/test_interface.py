import pytest
import uuid

from make87.config import load_config_from_json
from make87.interfaces.rerun.interface import (
    RerunInterface,
    _deterministic_uuid_v4_from_string,
)
from make87.internal.models.application_env_config import (
    InterfaceConfig,
    ApplicationInfo,
    BoundClient,
    BoundServer,
)
from make87.models import ApplicationConfig, MountedPeripherals


@pytest.fixture
def base_application_info():
    return ApplicationInfo(
        deployed_application_id=uuid.uuid4().hex,
        system_id="test-system-id",
        deployed_application_name="test_app",
        is_release_version=True,
        application_id=uuid.uuid4().hex,
        application_name="test_app",
    )


@pytest.fixture
def client_config(base_application_info):
    """Configuration with a Rerun client."""
    application_config_in = ApplicationConfig(
        interfaces=dict(
            rerun_test=InterfaceConfig(
                name="rerun_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients=dict(
                    rerun_client=BoundClient(
                        vpn_ip="127.0.0.1",
                        vpn_port=9876,
                        public_ip=None,
                        public_port=None,
                        same_node=False,
                        name="rerun_client_service",
                        key="rerun_client_key",
                        spec="rerun_client_spec",
                        interface_name="rerun",
                        protocol="grpc",
                        batcher_config=dict(
                            flush_tick=0.1,
                            flush_num_bytes=1048576,
                            flush_num_rows=1000,
                        ),
                    ),
                ),
                servers={},
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=base_application_info,
    )

    config_str = application_config_in.model_dump_json()
    return load_config_from_json(config_str)


@pytest.fixture
def server_config(base_application_info):
    """Configuration with a Rerun server."""
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
                    )
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=base_application_info,
    )

    config_str = application_config_in.model_dump_json()
    return load_config_from_json(config_str)


@pytest.fixture
def empty_config(base_application_info):
    """Configuration with no clients or servers."""
    application_config_in = ApplicationConfig(
        interfaces=dict(
            rerun_test=InterfaceConfig(
                name="rerun_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients={},
                servers={},
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=base_application_info,
    )

    config_str = application_config_in.model_dump_json()
    return load_config_from_json(config_str)


class TestRerunInterface:
    """Test the RerunInterface class."""

    def test_init_with_config(self, client_config):
        """Test interface initialization with provided config."""
        interface = RerunInterface("rerun_test", client_config)

        assert interface.name == "rerun_test"
        assert interface._config == client_config

    def test_init_without_config(self):
        """Test interface initialization without providing config."""
        # This should raise an error since we don't have a proper environment config
        with pytest.raises(Exception):  # Could be various config loading errors
            RerunInterface("rerun_test")

    def test_get_interface_type_by_name_client(self, client_config):
        """Test getting client configuration by name."""
        interface = RerunInterface("rerun_test", client_config)

        client = interface.get_interface_type_by_name("rerun_client", "CLI")
        assert client is not None
        assert client.vpn_ip == "127.0.0.1"
        assert client.vpn_port == 9876

    def test_get_interface_type_by_name_server(self, server_config):
        """Test getting server configuration by name."""
        interface = RerunInterface("rerun_test", server_config)

        server = interface.get_interface_type_by_name("rerun_server", "SRV")
        assert server is not None
        assert server.name == "rerun_server_service"

    def test_get_interface_type_by_name_not_found(self, empty_config):
        """Test error when client/server is not found."""
        interface = RerunInterface("rerun_test", empty_config)

        with pytest.raises(KeyError, match="CLI with name nonexistent not found"):
            interface.get_interface_type_by_name("nonexistent", "CLI")

        with pytest.raises(KeyError, match="SRV with name nonexistent not found"):
            interface.get_interface_type_by_name("nonexistent", "SRV")

    def test_deterministic_uuid_generation(self, client_config):
        """Test that UUID generation is deterministic."""
        uuid1 = _deterministic_uuid_v4_from_string("test-string")
        uuid2 = _deterministic_uuid_v4_from_string("test-string")

        assert uuid1 == uuid2
        assert uuid1.version == 4

    def test_get_client_recording_stream_config_parsing(self, client_config):
        """Test client recording stream configuration parsing."""
        interface = RerunInterface("rerun_test", client_config)

        # Test that we can get the client config and parse it correctly
        client_config = interface.get_interface_type_by_name("rerun_client", "CLI")
        assert client_config.model_extra is not None

        # Test that the interface parses the configuration without errors
        # (We don't actually create the recording stream to avoid rerun dependency)

    def test_get_server_recording_stream_config_parsing(self, server_config):
        """Test server recording stream configuration parsing."""
        interface = RerunInterface("rerun_test", server_config)

        # Test that we can get the server config and parse it correctly
        server_config = interface.get_interface_type_by_name("rerun_server", "SRV")
        assert server_config.model_extra is not None

        # Test that the interface parses the configuration without errors
        # (We don't actually create the recording stream to avoid rerun dependency)

    def test_interface_config_property(self, client_config):
        """Test the interface_config property."""
        interface = RerunInterface("rerun_test", client_config)

        interface_config = interface.interface_config
        assert interface_config is not None
        assert interface_config.name == "rerun_test"
        assert len(interface_config.clients) == 1
        assert "rerun_client" in interface_config.clients
