import os
from typing import TypeVar

from google.protobuf.message import Message

T = TypeVar("T", bound=Message)


IS_IN_RELEASE_MODE = os.environ.get("RELEASE_MODE", "false").lower() == "true"
DEPLOYED_APPLICATION_ID = os.environ.get("DEPLOYED_APPLICATION_ID", "unknown_application_id")
DEPLOYED_APPLICATION_NAME = os.environ.get("DEPLOYED_APPLICATION_NAME", "unknown_application_name")
DEPLOYED_SYSTEM_ID = os.environ.get("DEPLOYED_SYSTEM_ID", "unknown_system_id")
APPLICATION_ID = os.environ.get("APPLICATION_ID", "unknown_application_id")
APPLICATION_NAME = os.environ.get("APPLICATION_NAME", "unknown_application_name")
