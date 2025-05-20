import json
import subprocess
import time
import sys
import os
from pathlib import Path


import itertools
import pytest

from make87.interfaces.zenoh.model import Priority, Reliability, CongestionControl

# Test inputs
priorities = [Priority.REAL_TIME, Priority.DATA, Priority.BACKGROUND]
reliabilities = [Reliability.BEST_EFFORT, Reliability.RELIABLE]
congestion_controls = [CongestionControl.DROP, CongestionControl.BLOCK]
express_values = [True, False]
handlers = ["FIFO", "RING"]
capacity = [1, 256]


@pytest.mark.parametrize(
    "priority,reliability,congestion_control,express,handler_type,handler_capacity",
    list(itertools.product(priorities, reliabilities, congestion_controls, express_values, handlers, capacity)),
)
def test_pub_sub_combination(priority, reliability, congestion_control, express, handler_type, handler_capacity):
    base_dir = Path(__file__).parent

    subscriber_path = base_dir / "subscriber" / "main.py"
    publisher_path = base_dir / "publisher" / "main.py"

    base_env = os.environ.copy()

    subscriber_env = base_env.copy()
    publisher_env = base_env.copy()

    subscriber_topic = {
        "topic_name": "HELLO_WORLD_MESSAGE",
        "topic_key": "my_topic_key",
        "topic_type": "SUB",
        "message_type": "make87_messages.text.text_plain.PlainText",
        "handler": {
            "handler_type": handler_type,
            "capacity": handler_capacity,
        },
    }

    publisher_topic = {
        "topic_type": "PUB",
        "topic_name": "HELLO_WORLD_MESSAGE",
        "topic_key": "my_topic_key",
        "message_type": "make87_messages.text.text_plain.PlainText",
        "priority": priority.value,
        "reliability": reliability.value,
        "congestion_control": congestion_control.value,
        "express": express,
    }

    subscriber_env.update(
        {
            "ENDPOINTS": json.dumps({"endpoints": []}),
            "TOPICS": json.dumps({"topics": [subscriber_topic]}),
        }
    )

    publisher_env.update(
        {
            "ENDPOINTS": json.dumps({"endpoints": []}),
            "TOPICS": json.dumps({"topics": [publisher_topic]}),
        }
    )

    # Start subscriber
    subscriber_proc = subprocess.Popen(
        [sys.executable, str(subscriber_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=subscriber_env
    )

    time.sleep(1)  # Let subscriber boot up

    # Start publisher (non-blocking)
    publisher_proc = subprocess.Popen(
        [sys.executable, str(publisher_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=publisher_env
    )

    time.sleep(1)  # Let publisher publish + subscriber receive

    # Kill publisher
    publisher_proc.terminate()
    try:
        publisher_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        publisher_proc.kill()
        publisher_proc.communicate()

    # Kill subscriber
    subscriber_proc.terminate()
    try:
        sub_stdout, sub_stderr = subscriber_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        subscriber_proc.kill()
        sub_stdout, sub_stderr = subscriber_proc.communicate()

    output = sub_stdout.decode()
    assert all(w in output.lower() for w in ("hello", "world"))


def test_defaults_only():
    base_dir = Path(__file__).parent

    subscriber_path = base_dir / "subscriber" / "main.py"
    publisher_path = base_dir / "publisher" / "main.py"

    base_env = os.environ.copy()

    subscriber_env = base_env.copy()
    subscriber_env.update(
        {
            "ENDPOINTS": '{"endpoints": []}',
            "TOPICS": (
                '{"topics": [{"topic_name": "HELLO_WORLD_MESSAGE", "topic_key": "my_topic_key", "topic_type": "SUB", "message_type": "make87_messages.text.text_plain.PlainText"}]}'
            ),
        }
    )

    publisher_env = base_env.copy()
    publisher_env.update(
        {
            "ENDPOINTS": '{"endpoints": []}',
            "TOPICS": (
                '{"topics": [{"topic_type": "PUB", "topic_name": "HELLO_WORLD_MESSAGE", "topic_key": "my_topic_key", "message_type": "make87_messages.text.text_plain.PlainText"}]}'
            ),
        }
    )

    # Start subscriber
    subscriber_proc = subprocess.Popen(
        [sys.executable, str(subscriber_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=subscriber_env
    )

    time.sleep(1)  # Let subscriber boot up

    # Start publisher (non-blocking)
    publisher_proc = subprocess.Popen(
        [sys.executable, str(publisher_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=publisher_env
    )

    time.sleep(1)  # Let publisher publish + subscriber receive

    # Kill publisher
    publisher_proc.terminate()
    try:
        publisher_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        publisher_proc.kill()
        publisher_proc.communicate()

    # Kill subscriber
    subscriber_proc.terminate()
    try:
        sub_stdout, sub_stderr = subscriber_proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        subscriber_proc.kill()
        sub_stdout, sub_stderr = subscriber_proc.communicate()

    output = sub_stdout.decode()
    assert all(w in output.lower() for w in ("hello", "world"))
