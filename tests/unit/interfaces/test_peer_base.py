import pytest
import uuid

from make87.config import load_config_from_json
from make87.interfaces.base import InterfaceBase
from make87.internal.models.application_env_config import (
    InterfaceConfig,
    ApplicationInfo,
    BoundPeer,
    AccessPoint,
)
from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)


class MockInterface(InterfaceBase):
    """Mock implementation of InterfaceBase for peer testing."""

    pass


@pytest.fixture
def peer_config():
    """Configuration with peer defined."""
    application_config_in = ApplicationConfig(
        interfaces=dict(
            test_interface=InterfaceConfig(
                name="test_interface",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients={},
                servers={},
                peers=dict(
                    test_peer=BoundPeer(
                        name="test_peer",
                        key="peer_key_1",
                        spec="peer_spec",
                        protocol="zenoh",
                        interface_name="zenoh",
                        peer_keys=["peer_endpoint_1", "peer_endpoint_2"],
                        access_points={
                            "peer_endpoint_1": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7447,
                                same_node=True,
                            ),
                            "peer_endpoint_2": AccessPoint(
                                vpn_ip="127.0.0.1",
                                vpn_port=7448,
                                same_node=True,
                            ),
                        },
                    )
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="peer_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="peer_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


@pytest.fixture
def config_without_peers():
    """Configuration without peers defined."""
    application_config_in = ApplicationConfig(
        interfaces=dict(
            test_interface=InterfaceConfig(
                name="test_interface",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients={},
                servers={},
                # No peers specified
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="no_peers_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="no_peers_test_app",
        ),
    )

    application_config_str = application_config_in.model_dump_json()
    return load_config_from_json(application_config_str)


def test_get_peer_interface_type_by_name(peer_config):
    """Test that PEER interface type can be retrieved correctly."""
    interface = MockInterface(name="test_interface", make87_config=peer_config)

    # Get the peer configuration
    peer_config_obj = interface.get_interface_type_by_name("test_peer", "PEER")

    # Verify it's the correct type
    assert isinstance(peer_config_obj, BoundPeer)

    # Verify the configuration details
    assert peer_config_obj.name == "test_peer"
    assert peer_config_obj.key == "peer_key_1"
    assert peer_config_obj.spec == "peer_spec"
    assert peer_config_obj.protocol == "zenoh"
    assert peer_config_obj.interface_name == "zenoh"
    assert peer_config_obj.peer_keys == ["peer_endpoint_1", "peer_endpoint_2"]

    # Verify access points
    assert len(peer_config_obj.access_points) == 2
    assert "peer_endpoint_1" in peer_config_obj.access_points
    assert "peer_endpoint_2" in peer_config_obj.access_points

    # Check first access point
    ap1 = peer_config_obj.access_points["peer_endpoint_1"]
    assert ap1.vpn_ip == "127.0.0.1"
    assert ap1.vpn_port == 7447
    assert ap1.same_node is True

    # Check second access point
    ap2 = peer_config_obj.access_points["peer_endpoint_2"]
    assert ap2.vpn_ip == "127.0.0.1"
    assert ap2.vpn_port == 7448
    assert ap2.same_node is True


def test_get_peer_interface_type_by_name_not_found(peer_config):
    """Test that KeyError is raised when peer name is not found."""
    interface = MockInterface(name="test_interface", make87_config=peer_config)

    with pytest.raises(KeyError) as exc_info:
        interface.get_interface_type_by_name("nonexistent_peer", "PEER")

    assert "PEER with name nonexistent_peer not found in interface test_interface" in str(exc_info.value)


def test_get_peer_interface_with_no_peers_configured(config_without_peers):
    """Test that KeyError is raised when no peers are configured."""
    interface = MockInterface(name="test_interface", make87_config=config_without_peers)

    with pytest.raises(KeyError) as exc_info:
        interface.get_interface_type_by_name("any_peer", "PEER")

    assert "PEER with name any_peer not found in interface test_interface" in str(exc_info.value)


def test_peer_interface_config_structure(peer_config):
    """Test that the peer configuration structure is correctly parsed."""
    interface = MockInterface(name="test_interface", make87_config=peer_config)

    # Verify that peers are available in interface config
    assert interface.interface_config.peers is not None
    assert len(interface.interface_config.peers) == 1
    assert "test_peer" in interface.interface_config.peers

    # Verify the peer configuration matches what we expect
    peer = interface.interface_config.peers["test_peer"]
    assert isinstance(peer, BoundPeer)
    assert len(peer.peer_keys) == 2
    assert len(peer.access_points) == 2


def test_interface_type_coverage(peer_config):
    """Test that PEER type is properly integrated into the type system."""
    interface = MockInterface(name="test_interface", make87_config=peer_config)

    # This should not raise an error - PEER should be a supported type
    # We can test that the method signature accepts PEER as a valid literal
    import inspect

    sig = inspect.signature(interface.get_interface_type_by_name)
    iface_type_param = sig.parameters["iface_type"]

    # The type annotation should include PEER
    assert "PEER" in str(iface_type_param.annotation)


def test_peer_type_annotation(peer_config):
    """Test that PEER type returns BoundPeer type annotation."""
    interface = MockInterface(name="test_interface", make87_config=peer_config)

    # Use type checking to verify the overload works correctly
    # This is mainly for IDE/type checker support
    from typing import get_type_hints

    # The method should have proper type annotations
    hints = get_type_hints(interface.get_interface_type_by_name)
    assert "return" in hints
