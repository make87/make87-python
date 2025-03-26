import atexit
import os
import sys

from make87_messages.core.header_pb2 import Header

import make87
from make87.topics import get_publisher, TypedPublisher
from make87_messages.text.log_message_pb2 import LogMessage


class _StdErrHandler:
    """Redirects stderr to a topic."""

    def __init__(self, topic):
        self._topic: TypedPublisher = topic
        self._original_stderr = sys.stderr

    def write(self, message):
        if self._topic is not None and message.strip():
            self.publish_log(message)
        self._original_stderr.write(message)

    def flush(self):
        pass

    def publish_log(self, message):
        log_header = Header(entity_path=f"{make87.DEPLOYED_APPLICATION_NAME}/logs")
        log_header.timestamp.GetCurrentTime()

        log_msg = LogMessage(header=log_header)
        log_msg.level = LogMessage.ERROR
        log_msg.message = message
        log_msg.source = "stderr"
        log_msg.file_name = os.path.relpath(__file__, os.getcwd())
        log_msg.line_number = 0
        log_msg.process_id = os.getpid()
        log_msg.thread_id = 0
        self._topic.publish(message=log_msg)

    def restore_stderr(self):
        sys.stderr = self._original_stderr


def initialize():
    """Sets up the stderr handler."""
    try:
        topic = get_publisher(name="STDERR", message_type=LogMessage)
        stderr_handler = _StdErrHandler(topic)
        sys.stderr = stderr_handler
        atexit.register(stderr_handler.restore_stderr)
    except Exception as e:
        print(f"No stderr topic setup. Will not publish stderr. Error: {e}")


def cleanup():
    """Cleans up the stderr handler."""
    if isinstance(sys.stderr, _StdErrHandler):
        sys.stderr.flush()
        sys.stderr.restore_stderr()
