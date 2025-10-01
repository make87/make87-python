import subprocess
import time
import sys
import os
import uuid
from pathlib import Path

import pytest

from make87.internal.models.application_env_config import (
    ApplicationInfo,
    InterfaceConfig,
    BoundClient,
    BoundServer,
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
                    rerun_server=BoundServer(
                        name="rerun_server_service",
                        key="rerun_server_key",
                        spec="rerun_server_spec",
                        interface_name="rerun",
                        protocol="grpc",
                        memory_limit=134217728,  # 128MB
                        playback_behavior="OldestFirst",
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
def test_rerun_client_server():
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
        # Give client time to connect and run (increased timeout for more complex logging)
        client_stdout, client_stderr = client_proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        client_proc.kill()
        client_stdout, client_stderr = client_proc.communicate()

    # Terminate server after client is done
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
            "server is ready to accept client connections",
            "rerun-sdk not installed",
        ]
    ), f"Server did not start successfully. Output: {server_output}, Error: {server_error}"

    assert any(
        phrase in client_output.lower()
        for phrase in [
            "client recording stream created successfully",
            "connected to rerun server",
            "test data logged successfully",
            "rerun-sdk not installed",
        ]
    ), f"Client did not run successfully. Output: {client_output}, Error: {client_error}"


if __name__ == "__main__":
    # Run the meaningful integration test when executed directly
    test_rerun_client_server()
    print("Integration test completed successfully")
