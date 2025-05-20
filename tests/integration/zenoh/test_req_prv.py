import json
import subprocess
import time
import sys
import os
from pathlib import Path


import itertools
import pytest

from make87.interfaces.zenoh.model import Priority, CongestionControl

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
def test_pub_sub_combination(priority, congestion_control, express, handler_type, handler_capacity):
    base_dir = Path(__file__).parent

    requester_path = base_dir / "requester" / "main.py"
    publisher_path = base_dir / "provider" / "main.py"

    base_env = os.environ.copy()

    requester_env = base_env.copy()
    provider_env = base_env.copy()

    requester_endpoint = {
        "endpoint_type": "REQ",
        "endpoint_name": "EXAMPLE_ENDPOINT",
        "endpoint_key": "my_endpoint_key",
        "requester_message_type": "make87_messages.text.text_plain.PlainText",
        "provider_message_type": "make87_messages.text.text_plain.PlainText",
        "priority": priority.value,
        "congestion_control": congestion_control.value,
        "express": express,
    }

    provider_endpoint = {
        "endpoint_name": "EXAMPLE_ENDPOINT",
        "endpoint_key": "my_endpoint_key",
        "endpoint_type": "PRV",
        "requester_message_type": "make87_messages.text.text_plain.PlainText",
        "provider_message_type": "make87_messages.text.text_plain.PlainText",
        "handler": {
            "handler_type": handler_type,
            "capacity": handler_capacity,
        },
    }

    requester_env.update(
        {
            "ENDPOINTS": json.dumps({"endpoints": [requester_endpoint]}),
            "TOPICS": json.dumps({"topics": []}),
        }
    )

    provider_env.update(
        {
            "ENDPOINTS": json.dumps({"endpoints": [provider_endpoint]}),
            "TOPICS": json.dumps({"topics": []}),
        }
    )

    # Start subscriber
    requester_proc = subprocess.Popen(
        [sys.executable, str(requester_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=requester_env
    )

    time.sleep(1)  # Let subscriber boot up

    # Start publisher (non-blocking)
    provider_proc = subprocess.Popen(
        [sys.executable, str(publisher_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=provider_env
    )

    time.sleep(1)  # Let publisher publish + subscriber receive

    # Kill publisher
    provider_proc.terminate()
    try:
        provider_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        provider_proc.kill()
        provider_proc.communicate()

    # Kill subscriber
    requester_proc.terminate()
    try:
        req_stdout, req_stderr = requester_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        requester_proc.kill()
        req_stdout, req_stderr = requester_proc.communicate()

    output = req_stdout.decode()
    assert all(w in output.lower() for w in ("olleh", "dlrow"))


def test_defaults_only():
    base_dir = Path(__file__).parent

    requester_path = base_dir / "requester" / "main.py"
    publisher_path = base_dir / "provider" / "main.py"

    base_env = os.environ.copy()

    requester_end = base_env.copy()
    requester_end.update(
        {
            "ENDPOINTS": (
                '{"endpoints": [{"endpoint_type": "REQ", "endpoint_name": "REQUESTER_ENDPOINT", "endpoint_key": "my_endpoint_key", "requester_message_type": "make87_messages.text.text_plain.PlainText", "provider_message_type": "make87_messages.text.text_plain.PlainText"}]}'
            ),
            "TOPICS": '{"topics": []}',
        }
    )

    provider_env = base_env.copy()
    provider_env.update(
        {
            "ENDPOINTS": (
                '{"endpoints": [{"endpoint_type": "PRV", "endpoint_name": "PROVIDER_ENDPOINT", "endpoint_key": "my_endpoint_key", "requester_message_type": "make87_messages.text.text_plain.PlainText", "provider_message_type": "make87_messages.text.text_plain.PlainText"}]}'
            ),
            "TOPICS": '{"topics": []}',
        }
    )

    # Start subscriber
    requester_proc = subprocess.Popen(
        [sys.executable, str(requester_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=requester_end
    )

    time.sleep(1)  # Let subscriber boot up

    # Start publisher (non-blocking)
    provider_proc = subprocess.Popen(
        [sys.executable, str(publisher_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=provider_env
    )

    time.sleep(1)  # Let publisher publish + subscriber receive

    # Kill publisher
    provider_proc.terminate()
    try:
        provider_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        provider_proc.kill()
        provider_proc.communicate()

    # Kill subscriber
    requester_proc.terminate()
    try:
        req_stdout, req_stderr = requester_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        requester_proc.kill()
        req_stdout, req_stderr = requester_proc.communicate()

    output = req_stdout.decode()
    assert all(w in output.lower() for w in ("olleh", "dlrow"))
