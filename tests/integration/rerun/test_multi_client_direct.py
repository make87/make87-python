"""
Direct test of multi-client functionality for Rerun interface.

This test verifies that the multi-client configuration is parsed correctly
and that multiple recording streams are created as expected.
"""

import uuid

import pytest

from make87.interfaces.rerun import RerunInterface
from make87.internal.models.application_env_config import (
    ApplicationInfo,
    BoundMultiClient,
    AccessPoint,
    InterfaceConfig,
)
from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)
from make87.config import load_config_from_json


@pytest.fixture
def multi_client_app_config():
    """Configuration for multi-client application."""
    config = ApplicationConfig(
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
                                vpn_ip="localhost",
                                vpn_port=9876,
                                same_node=True,
                            ),
                            "server_endpoint_2": AccessPoint(
                                vpn_ip="localhost",
                                vpn_port=9877,
                                same_node=True,
                            ),
                            "server_endpoint_3": AccessPoint(
                                vpn_ip="localhost",
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
            deployed_application_name="multi_client_rerun_test",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="multi_client_rerun_test",
        ),
    )
    return load_config_from_json(config.model_dump_json())


def test_multi_client_creation(multi_client_app_config):
    """Test that multi-client creates the correct configuration."""
    interface = RerunInterface(name="rerun_test", make87_config=multi_client_app_config)

    # Test getting multi-client configuration
    multi_client_config = interface.get_interface_type_by_name("MULTI_RERUN_CLIENT", "MCLI")

    # Should have 3 endpoint keys
    assert len(multi_client_config.keys) == 3, f"Expected 3 keys, got {len(multi_client_config.keys)}"

    # Check keys are correct
    expected_keys = ["server_endpoint_1", "server_endpoint_2", "server_endpoint_3"]
    assert multi_client_config.keys == expected_keys

    # Check access points
    assert len(multi_client_config.access_points) == 3
    for key in expected_keys:
        assert key in multi_client_config.access_points

    # Check access point details
    ap1 = multi_client_config.access_points["server_endpoint_1"]
    assert ap1.vpn_ip == "localhost"
    assert ap1.vpn_port == 9876

    ap2 = multi_client_config.access_points["server_endpoint_2"]
    assert ap2.vpn_ip == "localhost"
    assert ap2.vpn_port == 9877

    ap3 = multi_client_config.access_points["server_endpoint_3"]
    assert ap3.vpn_ip == "localhost"
    assert ap3.vpn_port == 9878

    print("✅ Multi-client configuration verified successfully")


def test_multi_client_config_validation(multi_client_app_config):
    """Test that multi-client configuration is properly structured."""
    interface = RerunInterface(name="rerun_test", make87_config=multi_client_app_config)

    # Verify each access point matches its key
    multi_client_config = interface.get_interface_type_by_name("MULTI_RERUN_CLIENT", "MCLI")

    # Check endpoint keys are different
    endpoint_keys = multi_client_config.keys
    assert len(set(endpoint_keys)) == 3, f"Endpoint keys should be unique: {endpoint_keys}"

    # Check access points have different ports
    ports = [ap.vpn_port for ap in multi_client_config.access_points.values()]
    assert len(set(ports)) == 3, f"Access point ports should be unique: {ports}"

    # Verify multi-client config has the same endpoint keys as access points
    assert set(multi_client_config.keys) == set(
        multi_client_config.access_points.keys()
    ), "Multi-client keys should match access point keys"

    print("✅ Multi-client configuration validation passed")


# Note: We don't test actual recording stream creation because it would
# require connecting to live Rerun servers. The above tests verify that
# the multi-client infrastructure is correctly configured.


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
