from make87_messages.text.log_message_pb2 import LogMessage

LEVEL_MAPPING = {
    "DEBUG": LogMessage.DEBUG,
    "INFO": LogMessage.INFO,
    "WARNING": LogMessage.WARNING,
    "ERROR": LogMessage.ERROR,
    "CRITICAL": LogMessage.CRITICAL,
}
