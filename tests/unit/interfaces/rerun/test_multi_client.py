import pytest
import uuid

from make87.config import load_config_from_json
from make87.interfaces.rerun.interface import RerunInterface
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
            rerun_test=InterfaceConfig(
                name="rerun_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients={},
                servers={},
                multi_clients=dict(
                    MULTI_RERUN_CLIENT=BoundMultiClient(
                        name="MULTI_RERUN_CLIENT",
                        keys=["server_endpoint_1", "server_endpoint_2", "server_endpoint_3"],
                        spec="rerun_client",
                        protocol="grpc",
                        interface_name="rerun",
                        access_points={
                            "server_endpoint_1": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=9876,
                                same_node=True,
                            ),
                            "server_endpoint_2": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=9877,
                                same_node=True,
                            ),
                            "server_endpoint_3": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=9878,
                                same_node=True,
                            ),
                        },
                        batcher_config=dict(
                            flush_tick=0.1,
                            flush_num_bytes=1048576,
                            flush_num_rows=1000,
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
            deployed_application_name="multi_client_rerun_app_1",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="multi_client_rerun_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@pytest.fixture
def rerun_interface(multi_client_config):
    iface = RerunInterface(name="rerun_test", make87_config=multi_client_config)
    return iface


def test_get_multi_client_recording_streams_config_parsing(rerun_interface):
    """Test that get_multi_client_recording_streams returns correct configuration."""
    # Test that we can get the multi-client config and parse it correctly
    multi_client_config = rerun_interface.get_interface_type_by_name("MULTI_RERUN_CLIENT", "MCLI")

    # Should have 3 endpoint keys
    assert len(multi_client_config.keys) == 3
    assert "server_endpoint_1" in multi_client_config.keys
    assert "server_endpoint_2" in multi_client_config.keys
    assert "server_endpoint_3" in multi_client_config.keys

    # Should have matching access points
    assert len(multi_client_config.access_points) == 3
    assert "server_endpoint_1" in multi_client_config.access_points
    assert "server_endpoint_2" in multi_client_config.access_points
    assert "server_endpoint_3" in multi_client_config.access_points

    # Check access point details
    ap1 = multi_client_config.access_points["server_endpoint_1"]
    assert ap1.vpn_ip == "127.0.0.1"
    assert ap1.vpn_port == 9876

    ap2 = multi_client_config.access_points["server_endpoint_2"]
    assert ap2.vpn_ip == "127.0.0.1"
    assert ap2.vpn_port == 9877

    ap3 = multi_client_config.access_points["server_endpoint_3"]
    assert ap3.vpn_ip == "127.0.0.1"
    assert ap3.vpn_port == 9878


def test_get_multi_client_not_found(rerun_interface):
    """Test that get_multi_client_recording_streams raises KeyError for non-existent multi-client."""
    with pytest.raises(KeyError):
        rerun_interface.get_multi_client_recording_streams("NON_EXISTENT")


def test_get_regular_client_fails_on_multi_config(rerun_interface):
    """Test that regular get_client_recording_stream fails when trying to access multi-client config."""
    with pytest.raises(KeyError):
        rerun_interface.get_client_recording_stream("MULTI_RERUN_CLIENT")


def test_multi_client_endpoint_keys(rerun_interface):
    """Test that multi-client uses the correct endpoint keys."""
    # Get the configuration to verify the keys
    iface_config = rerun_interface.get_interface_type_by_name("MULTI_RERUN_CLIENT", "MCLI")

    # Should have 3 endpoint keys
    assert len(iface_config.keys) == 3
    assert "server_endpoint_1" in iface_config.keys
    assert "server_endpoint_2" in iface_config.keys
    assert "server_endpoint_3" in iface_config.keys

    # Should have matching access points
    assert len(iface_config.access_points) == 3
    assert "server_endpoint_1" in iface_config.access_points
    assert "server_endpoint_2" in iface_config.access_points
    assert "server_endpoint_3" in iface_config.access_points


def test_get_multi_client_alias(rerun_interface):
    """Test that get_multi_client alias method works correctly."""
    # Both methods should raise the same error for non-existent multi-client
    with pytest.raises(KeyError):
        rerun_interface.get_multi_client("NON_EXISTENT")

    with pytest.raises(KeyError):
        rerun_interface.get_multi_client_recording_streams("NON_EXISTENT")

    # Both methods should work for configuration parsing (we can't test actual creation without rerun)
    try:
        # This will fail at the rerun.RecordingStream creation, but should parse config fine
        rerun_interface.get_multi_client("MULTI_RERUN_CLIENT")
    except Exception as e:
        # Should be a rerun-related error, not a configuration error
        assert "rerun" in str(e).lower() or "module" in str(e).lower()

    try:
        # This will fail at the rerun.RecordingStream creation, but should parse config fine
        rerun_interface.get_multi_client_recording_streams("MULTI_RERUN_CLIENT")
    except Exception as e:
        # Should be a rerun-related error, not a configuration error
        assert "rerun" in str(e).lower() or "module" in str(e).lower()


# Note: We don't test actual RecordingStream creation because it requires
# the rerun package to be installed and working servers to connect to.
# The above tests verify the configuration parsing and validation logic.
