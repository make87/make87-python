import subprocess
import time
import sys
import os
import uuid
from pathlib import Path


import itertools
import pytest

from make87.interfaces.zenoh.model import Priority, CongestionControl
from make87.internal.models.application_env_config import (
    InterfaceConfig,
    BoundRequester,
    ApplicationInfo,
    BoundProvider,
)

from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)

# Test inputs
priorities = [Priority.REAL_TIME, Priority.DATA, Priority.BACKGROUND]
congestion_controls = [CongestionControl.DROP, CongestionControl.BLOCK]
express_values = [True, False]
handlers = ["FIFO", "RING"]
capacity = [1, 256]


@pytest.mark.parametrize(
    "priority,congestion_control,express,handler_type,handler_capacity",
    list(itertools.product(priorities, congestion_controls, express_values, handlers, capacity)),
)
def test_req_prv_combination(priority, congestion_control, express, handler_type, handler_capacity):
    base_dir = Path(__file__).parent

    requester_path = base_dir / "querier" / "main.py"
    publisher_path = base_dir / "queryable" / "main.py"

    base_env = os.environ.copy()

    querier_env = base_env.copy()
    queryable_env = base_env.copy()

    req_config = ApplicationConfig(
        interfaces=dict(
            zenoh_test=InterfaceConfig(
                name="zenoh_test",
                subscribers={},
                publishers={},
                requesters=dict(
                    HELLO_WORLD_MESSAGE=BoundRequester(
                        endpoint_name="HELLO_WORLD_MESSAGE",
                        endpoint_key="my_endpoint_key",
                        protocol="zenoh",
                        requester_message_type="make87_messages.text.text_plain.PlainText",
                        provider_message_type="make87_messages.text.text_plain.PlainText",
                        priority=priority.value,
                        congestion_control=congestion_control.value,
                        express=express,
                        vpn_ip="127.0.0.1",
                        vpn_port=7447,
                        same_node=True,
                    ),
                ),
                providers={},
                clients={},
                servers={},
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="sub_app_1",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="sub_app",
        ),
    )

    prv_config = ApplicationConfig(
        interfaces=dict(
            zenoh_test=InterfaceConfig(
                name="zenoh_test",
                subscribers={},
                publishers={},
                requesters={},
                providers=dict(
                    HELLO_WORLD_MESSAGE=BoundProvider(
                        endpoint_name="HELLO_WORLD_MESSAGE",
                        endpoint_key="my_endpoint_key",
                        protocol="zenoh",
                        requester_message_type="make87_messages.text.text_plain.PlainText",
                        provider_message_type="make87_messages.text.text_plain.PlainText",
                    ),
                ),
                clients={},
                servers={},
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="sub_app_1",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="sub_app",
        ),
    )

    querier_env.update(
        {
            "MAKE87_CONFIG": req_config.model_dump_json(),
        }
    )

    queryable_env.update(
        {
            "MAKE87_CONFIG": prv_config.model_dump_json(),
        }
    )

    # Start provider
    queryable_proc = subprocess.Popen(
        [sys.executable, str(publisher_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=queryable_env
    )

    time.sleep(1)  # Let provider boot up and expose

    # Start requester
    querier_proc = subprocess.Popen(
        [sys.executable, str(requester_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=querier_env
    )

    time.sleep(1)  # Let requester boot up and wait for response

    # Kill publisher
    queryable_proc.terminate()
    try:
        queryable_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        queryable_proc.kill()
        queryable_proc.communicate()

    # Kill subscriber
    querier_proc.terminate()
    try:
        req_stdout, req_stderr = querier_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        querier_proc.kill()
        req_stdout, req_stderr = querier_proc.communicate()

    output = req_stdout.decode()
    assert all(w in output.lower() for w in ("olleh", "dlrow"))


def test_defaults_only():
    base_dir = Path(__file__).parent

    requester_path = base_dir / "querier" / "main.py"
    publisher_path = base_dir / "queryable" / "main.py"

    base_env = os.environ.copy()

    querier_env = base_env.copy()
    queryable_env = base_env.copy()

    req_config = ApplicationConfig(
        interfaces=dict(
            zenoh_test=InterfaceConfig(
                name="zenoh_test",
                subscribers={},
                publishers={},
                requesters=dict(
                    HELLO_WORLD_MESSAGE=BoundRequester(
                        endpoint_name="HELLO_WORLD_MESSAGE",
                        endpoint_key="my_endpoint_key",
                        protocol="zenoh",
                        requester_message_type="make87_messages.text.text_plain.PlainText",
                        provider_message_type="make87_messages.text.text_plain.PlainText",
                        vpn_ip="127.0.0.1",
                        vpn_port=7447,
                        same_node=True,
                    ),
                ),
                providers={},
                clients={},
                servers={},
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="sub_app_1",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="sub_app",
        ),
    )

    prv_config = ApplicationConfig(
        interfaces=dict(
            zenoh_test=InterfaceConfig(
                name="zenoh_test",
                subscribers={},
                publishers={},
                requesters={},
                providers=dict(
                    HELLO_WORLD_MESSAGE=BoundProvider(
                        endpoint_name="HELLO_WORLD_MESSAGE",
                        endpoint_key="my_endpoint_key",
                        protocol="zenoh",
                        requester_message_type="make87_messages.text.text_plain.PlainText",
                        provider_message_type="make87_messages.text.text_plain.PlainText",
                    ),
                ),
                clients={},
                servers={},
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="sub_app_1",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="sub_app",
        ),
    )

    querier_env.update(
        {
            "MAKE87_CONFIG": req_config.model_dump_json(),
        }
    )

    queryable_env.update(
        {
            "MAKE87_CONFIG": prv_config.model_dump_json(),
        }
    )

    # Start provider
    queryable_proc = subprocess.Popen(
        [sys.executable, str(publisher_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=queryable_env
    )

    time.sleep(1)  # Let provider boot up and expose

    # Start requester
    querier_proc = subprocess.Popen(
        [sys.executable, str(requester_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=querier_env
    )

    time.sleep(1)  # Let requester boot up and wait for response

    # Kill publisher
    queryable_proc.terminate()
    try:
        queryable_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        queryable_proc.kill()
        queryable_proc.communicate()

    # Kill subscriber
    querier_proc.terminate()
    try:
        req_stdout, req_stderr = querier_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        querier_proc.kill()
        req_stdout, req_stderr = querier_proc.communicate()

    output = req_stdout.decode()
    assert all(w in output.lower() for w in ("olleh", "dlrow"))
