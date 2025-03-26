import logging
import os
from datetime import datetime, timezone

from make87_messages.core.header_pb2 import Header

import make87
from make87.handlers import LEVEL_MAPPING
from make87.topics import TypedPublisher, get_publisher
from make87_messages.text.log_message_pb2 import LogMessage


class _LogHandler(logging.Handler):
    """Custom logging handler that publishes logs to a topic."""

    def __init__(self, topic):
        super().__init__()
        self._topic: TypedPublisher = topic

    def emit(self, record):
        if self._topic is None:
            return

        log_header = Header(entity_path=f"{make87.DEPLOYED_APPLICATION_NAME}/logs")
        log_header.timestamp.FromDatetime(datetime.fromtimestamp(record.created, tz=timezone.utc))

        log_msg = LogMessage(header=log_header)
        log_msg.level = LEVEL_MAPPING.get(record.levelname, LogMessage.INFO)
        log_msg.message = record.getMessage()
        log_msg.source = record.name
        log_msg.file_name = os.path.relpath(record.pathname, os.getcwd())
        log_msg.line_number = record.lineno
        log_msg.process_id = record.process
        log_msg.thread_id = record.thread
        self._topic.publish(message=log_msg)


def initialize():
    """Sets up the logging handler. Automatically forwards all logs as messages to the 'LOGS' topic."""
    logger = logging.getLogger()
    try:
        topic = get_publisher(name="LOGS", message_type=LogMessage)
        log_handler = _LogHandler(topic)
        logger.addHandler(log_handler)
    except Exception as e:
        print(f"No log topic setup. Will not publish logs. Error: {e}")


def cleanup():
    """Cleans up the logging handler and restores original logging configuration."""
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        if isinstance(handler, _LogHandler):
            handler.flush()
            handler.close()
            logger.removeHandler(handler)
