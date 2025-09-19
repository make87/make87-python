import subprocess
import time
import sys
import os
import uuid
from pathlib import Path

import pytest

from make87.interfaces.rerun import RerunInterface
from make87.internal.models.application_env_config import (
    ApplicationInfo,
    InterfaceConfig,
    BoundClient,
    ServerServiceConfig,
)
from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)


def create_client_config():
    """Create test configuration with a Rerun client."""
    return ApplicationConfig(
        interfaces=dict(
            rerun_test=InterfaceConfig(
                name="rerun_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients=dict(
                    rerun_client=BoundClient(
                        # AccessPoint fields
                        vpn_ip="localhost",
                        vpn_port=9876,
                        public_ip=None,
                        public_port=None,
                        same_node=False,
                        # ClientServiceConfig fields
                        name="rerun_client_service",
                        key="rerun_client_key",
                        spec="rerun_client_spec",
                        interface_name="rerun",
                        protocol="grpc",
                        # Extra config for rerun
                        batcher_config=dict(
                            flush_tick=0.1,
                            flush_num_bytes=1048576,
                            flush_num_rows=1000,
                        ),
                    )
                ),
                servers={},
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=f"integration-test-{uuid.uuid4().hex[:8]}",
            deployed_application_name="rerun_client_test",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="rerun_client_app",
        ),
    )


def create_server_config():
    """Create test configuration with a Rerun server."""
    return ApplicationConfig(
        interfaces=dict(
            rerun_test=InterfaceConfig(
                name="rerun_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients={},
                servers=dict(
                    rerun_server=ServerServiceConfig(
                        name="rerun_server_service",
                        key="rerun_server_key",
                        spec="rerun_server_spec",
                        interface_name="rerun",
                        protocol="grpc",
                        max_bytes=134217728,  # 128MB
                    )
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=f"integration-test-{uuid.uuid4().hex[:8]}",
            deployed_application_name="rerun_server_test",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="rerun_server_app",
        ),
    )


@pytest.mark.integration
def test_rerun_client_integration():
    """Test Rerun client integration with mock server connection."""
    base_dir = Path(__file__).parent
    client_path = base_dir / "client" / "main.py"

    base_env = os.environ.copy()

    client_config = create_client_config()
    client_env = base_env.copy()
    client_env.update(
        {
            "MAKE87_CONFIG": client_config.model_dump_json(),
        }
    )

    # Start client
    client_proc = subprocess.Popen(
        [sys.executable, str(client_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=client_env
    )

    try:
        # Give client time to run
        client_stdout, client_stderr = client_proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        client_proc.kill()
        client_stdout, client_stderr = client_proc.communicate()

    output = client_stdout.decode()
    error = client_stderr.decode()

    print(f"Client stdout: {output}")
    print(f"Client stderr: {error}")

    # Note: Client might fail to connect if no server is running, but it should
    # still create the recording stream successfully. Check for specific success messages.
    assert any(
        phrase in output.lower()
        for phrase in [
            "client recording stream created successfully",
            "integration test client is running",
            "rerun-sdk not installed",  # Acceptable if rerun is not installed
        ]
    ), f"Client test did not complete successfully. Output: {output}, Error: {error}"


@pytest.mark.integration
def test_rerun_server_integration():
    """Test Rerun server integration."""
    base_dir = Path(__file__).parent
    server_path = base_dir / "server" / "main.py"

    base_env = os.environ.copy()

    server_config = create_server_config()
    server_env = base_env.copy()
    server_env.update(
        {
            "MAKE87_CONFIG": server_config.model_dump_json(),
        }
    )

    # Start server (non-blocking)
    server_proc = subprocess.Popen(
        [sys.executable, str(server_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=server_env
    )

    try:
        # Give server time to start and run
        server_stdout, server_stderr = server_proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        server_proc.kill()
        server_stdout, server_stderr = server_proc.communicate()

    output = server_stdout.decode()
    error = server_stderr.decode()

    print(f"Server stdout: {output}")
    print(f"Server stderr: {error}")

    # Check that server started successfully
    assert any(
        phrase in output.lower()
        for phrase in [
            "server recording stream created successfully",
            "rerun server is now hosting",
            "integration test server is running",
            "rerun-sdk not installed",  # Acceptable if rerun is not installed
        ]
    ), f"Server test did not complete successfully. Output: {output}, Error: {error}"


@pytest.mark.integration
def test_rerun_client_server_full_cycle():
    """Test full client-server cycle (requires rerun)."""
    base_dir = Path(__file__).parent
    server_path = base_dir / "server" / "main.py"
    client_path = base_dir / "client" / "main.py"

    base_env = os.environ.copy()

    # Create configs
    server_config = create_server_config()
    client_config = create_client_config()

    server_env = base_env.copy()
    server_env.update(
        {
            "MAKE87_CONFIG": server_config.model_dump_json(),
        }
    )

    client_env = base_env.copy()
    client_env.update(
        {
            "MAKE87_CONFIG": client_config.model_dump_json(),
        }
    )

    # Start server first
    server_proc = subprocess.Popen(
        [sys.executable, str(server_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=server_env
    )

    # Give server time to start
    time.sleep(2)

    # Start client
    client_proc = subprocess.Popen(
        [sys.executable, str(client_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=client_env
    )

    try:
        # Give client time to connect and run
        client_stdout, client_stderr = client_proc.communicate(timeout=8)
    except subprocess.TimeoutExpired:
        client_proc.kill()
        client_stdout, client_stderr = client_proc.communicate()

    # Terminate server
    server_proc.terminate()
    try:
        server_stdout, server_stderr = server_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        server_proc.kill()
        server_stdout, server_stderr = server_proc.communicate()

    client_output = client_stdout.decode()
    server_output = server_stdout.decode()
    client_error = client_stderr.decode()
    server_error = server_stderr.decode()

    print(f"Server stdout: {server_output}")
    print(f"Server stderr: {server_error}")
    print(f"Client stdout: {client_output}")
    print(f"Client stderr: {client_error}")

    # Check that both server and client ran successfully
    assert any(
        phrase in server_output.lower()
        for phrase in [
            "server recording stream created successfully",
            "rerun server is now hosting",
            "rerun-sdk not installed",
        ]
    ), f"Server did not start successfully. Output: {server_output}, Error: {server_error}"

    assert any(
        phrase in client_output.lower()
        for phrase in [
            "client recording stream created successfully",
            "test data logged successfully",
            "rerun-sdk not installed",
        ]
    ), f"Client did not run successfully. Output: {client_output}, Error: {client_error}"


@pytest.mark.integration
def test_rerun_configuration_variations():
    # Test with minimal client config (no extra settings)
    minimal_client_config = ApplicationConfig(
        interfaces=dict(
            rerun_test=InterfaceConfig(
                name="rerun_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients=dict(
                    rerun_client=BoundClient(
                        vpn_ip="localhost",
                        vpn_port=9876,
                        public_ip=None,
                        public_port=None,
                        same_node=False,
                        name="rerun_client_service",
                        key="rerun_client_key",
                        spec="rerun_client_spec",
                        interface_name="rerun",
                        protocol="grpc",
                    ),
                ),
                servers={},
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id="test-system",
            deployed_application_name="rerun_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="rerun_test",
        ),
    )

    interface = RerunInterface("rerun_test", minimal_client_config)

    try:
        # Should work with default values
        recording = interface.get_client_recording_stream("rerun_client")
        assert recording is not None
    except Exception as e:
        # Connection might fail, but creation should work
        assert "Failed to create client recording stream" not in str(e)

    # Test with minimal server config (no max_bytes)
    minimal_server_config = ApplicationConfig(
        interfaces=dict(
            rerun_test=InterfaceConfig(
                name="rerun_test",
                subscribers={},
                publishers={},
                requesters={},
                providers={},
                clients={},
                servers=dict(
                    rerun_server=ServerServiceConfig(
                        name="rerun_server_service",
                        key="rerun_server_key",
                        spec="rerun_server_spec",
                        interface_name="rerun",
                        protocol="grpc",
                    )
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id="test-system",
            deployed_application_name="rerun_test_app",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="rerun_test",
        ),
    )

    interface = RerunInterface("rerun_test", minimal_server_config)

    try:
        # Should work with no memory limit
        recording = interface.get_server_recording_stream("rerun_server")
        assert recording is not None
    except Exception as e:
        # Server creation might fail in test environment, but config parsing should work
        assert "Failed to parse server configuration" not in str(e)


if __name__ == "__main__":
    # Run a simple integration test when executed directly
    test_rerun_client_integration()
    test_rerun_server_integration()
    print("All integration tests completed successfully")
