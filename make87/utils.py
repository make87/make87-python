import json
import os
import random
import sys
from typing import List, Generic, TypeVar, Type, Optional, Any
from typing import Union, Literal, Annotated

from google.protobuf.message import Message
from google.protobuf import timestamp_pb2
from pydantic import BaseModel, Field

T = TypeVar("T", bound=Message)

# Define int32 and uint32 limits
INT32_MIN = -2147483648
INT32_MAX = 2147483647
UINT32_MIN = 0
UINT32_MAX = 4294967295


class TopicBaseModel(BaseModel):
    topic_name: str
    topic_key: str
    message_type: str


class PUB(TopicBaseModel):
    topic_type: Literal["PUB"]


class SUB(TopicBaseModel):
    topic_type: Literal["SUB"]


class EndpointBaseModel(BaseModel):
    endpoint_name: str
    endpoint_key: str
    requester_message_type: str
    provider_message_type: str


class REQ(EndpointBaseModel):
    endpoint_type: Literal["REQ"]


class PRV(EndpointBaseModel):
    endpoint_type: Literal["PRV"]


Topic = Annotated[Union[PUB, SUB], Field(discriminator="topic_type")]
Endpoint = Annotated[Union[REQ, PRV], Field(discriminator="endpoint_type")]


class Topics(BaseModel):
    topics: List[Topic]


class Endpoints(BaseModel):
    endpoints: List[Endpoint]


IS_IN_RELEASE_MODE = os.environ.get("RELEASE_MODE", "false").lower() == "true"
DEPLOYED_APPLICATION_ID = os.environ.get("DEPLOYED_APPLICATION_ID", "unknown_application_id")
DEPLOYED_APPLICATION_NAME = os.environ.get("DEPLOYED_APPLICATION_NAME", "unknown_application_name")
DEPLOYED_SYSTEM_ID = os.environ.get("DEPLOYED_SYSTEM_ID", "unknown_system_id")
APPLICATION_ID = os.environ.get("APPLICATION_ID", "unknown_application_id")
APPLICATION_NAME = os.environ.get("APPLICATION_NAME", "unknown_application_name")


def parse_topics() -> Topics:
    try:
        topic_data_env = os.environ["TOPICS"]
        return Topics.model_validate_json(topic_data_env)
    except KeyError:
        if IS_IN_RELEASE_MODE:
            raise EnvironmentError("`TOPICS` environment variable is required in release mode.")
        else:
            return Topics(topics=[])
    except json.JSONDecodeError as e:
        raise ValueError("`TOPICS` environment variable is not valid JSON.") from e


def parse_endpoints() -> Endpoints:
    try:
        endpoints_data_env = os.environ["ENDPOINTS"]
        return Endpoints.model_validate_json(endpoints_data_env)
    except KeyError:
        if IS_IN_RELEASE_MODE:
            raise EnvironmentError("`ENDPOINTS` environment variable is required in release mode.")
        else:
            return Endpoints(endpoints=[])
    except json.JSONDecodeError as e:
        raise ValueError("`ENDPOINTS` environment variable is not valid JSON.") from e


class Metadata:
    def __init__(self, topic_name: str, message_type_decoded: str, bytes_transmitted: int):
        self.topic_name: str = topic_name
        self.message_type_decoded: str = message_type_decoded
        self.bytes_transmitted: int = bytes_transmitted

    def __repr__(self):
        return f"Metadata(topic_name={self.topic_name}, message_type_decoded={self.message_type_decoded}, bytes_transmitted={self.bytes_transmitted})"

    def __str__(self):
        return f"Metadata(topic_name={self.topic_name}, message_type_decoded={self.message_type_decoded}, bytes_transmitted={self.bytes_transmitted})"


class MessageWithMetadata(Generic[T]):
    """A message with metadata."""

    def __init__(self, message: T, metadata: Metadata):
        self.message: T = message
        self.metadata: Metadata = metadata


def create_header(
        header_cls: Type[T],
        entity_path: Optional[str] = None,
        reference_id: Optional[int] = None,
        timestamp: Optional[Any] = None
) -> T:
    """Creates a default Header with explicitly defined fields."""
    header = header_cls()  # Instantiate the proto class

    # Set timestamp (default: current UTC time)
    if hasattr(header, "timestamp"):
        if timestamp is None:
            header.timestamp.GetCurrentTime()
        else:
            header.timestamp.CopyFrom(timestamp)

    # Set entity_path (default: empty string)
    if hasattr(header, "entity_path"):
        header.entity_path = entity_path if entity_path is not None else "/"

    # Set reference_id (default: random int32 range value)
    if hasattr(header, "reference_id"):
        header.reference_id = reference_id if reference_id is not None else random.randint(UINT32_MIN, UINT32_MAX)

    return header


def header_from_message(
        header_cls: Type[T],
        message: Message,
        append_entity_path: Optional[str] = None,
        reference_id: Optional[int] = None,
        timestamp: Optional[Any] = None,
        set_current_time: bool = False
) -> T:
    """Clones a Header from an existing message and modifies specific fields."""
    # check if has header field, else raise
    if not hasattr(message, "header"):
        raise AttributeError("Message does not have a 'header' field.")

    new_header = header_cls()  # Create a new instance of the same header type
    new_header.CopyFrom(message.header)  # Clone all fields

    # Append to entity_path if provided
    if hasattr(new_header, "entity_path") and append_entity_path:
        new_header.entity_path = f"{new_header.entity_path}/{append_entity_path}".replace("//", "/")

    # Override reference_id if provided, otherwise keep the old one or generate a new one
    if hasattr(new_header, "reference_id") and reference_id is not None:
        new_header.reference_id = reference_id

    # Override timestamp if provided, otherwise keep the old one or set to current time
    if hasattr(new_header, "timestamp") and timestamp:
        new_header.timestamp.CopyFrom(timestamp)

    elif hasattr(new_header, "timestamp") and set_current_time:
        new_header.timestamp.GetCurrentTime()

    return new_header
