import abc
import dataclasses
import datetime
import threading
from collections import deque
from datetime import timedelta
from functools import partial
from typing import Callable, Dict, TypeVar, Generic, List, Tuple, Any, Optional
from typing import Type
from typing import Union

import zenoh
from google.protobuf.message import Message
from zenoh.handlers import RingChannel

from make87.session import get_session
from make87.utils import parse_topics, PUB, SUB, Metadata, MessageWithMetadata, IS_IN_RELEASE_MODE

T = TypeVar("T", bound=Message)
T_M = TypeVar("T_M", bound="MessageWithMetadata")


class Topic:
    """Base class for topics."""

    def __init__(self, name: str):
        self.name = name


class TypedPublisher(Generic[T]):
    """A typed publisher topic that publishes messages of type `T`."""

    def __init__(self, inner: "Publisher", message_type: Type[T]):
        self._inner = inner
        self._message_type = message_type  # Store the actual class for runtime encoding

    def publish(self, message: T) -> None:
        """Publish a message of type `T`."""
        encoded_message = message.SerializeToString()
        self._inner.publisher.put(zenoh.ZBytes(encoded_message))


class Publisher(Topic):
    """A topic used for publishing messages."""

    def __init__(self, name: str, session: zenoh.Session):
        super().__init__(name)
        self._session = session
        self._pub = self._session.declare_publisher(
            f"{name}", encoding=zenoh.Encoding.APPLICATION_PROTOBUF, priority=zenoh.Priority.REAL_TIME, express=True
        )

    @property
    def publisher(self):
        return self._pub


class TypedSubscriber(Generic[T]):
    """A typed subscriber topic that provides messages of type `T`."""

    def __init__(self, inner: "Subscriber", message_type: Type[T]):
        self._inner = inner
        self._message_type = message_type  # Store the actual class for runtime decoding

    def subscribe(self, callback: Callable[[T], None]) -> None:
        """Subscribe to the topic with a callback that expects messages of type `T`."""

        def _decode_message(sample: zenoh.Sample):
            message = self._message_type()
            try:
                message.ParseFromString(sample.payload.to_bytes())
                callback(message)
            except Exception as e:
                raise Exception(f"Failed to decode message on topic '{self._inner.name}': {e}")

        self._inner.subscribe(_decode_message)

    def subscribe_with_metadata(self, callback: Callable[[MessageWithMetadata[T]], None]) -> None:
        """Subscribe to the topic with a callback that expects messages of type `T`."""

        def _decode_message(sample: zenoh.Sample):
            message = self._message_type()
            try:
                message.ParseFromString(sample.payload.to_bytes())
            except Exception as e:
                raise Exception(f"Failed to decode message on topic '{self._inner.name}': {e}")

            callback(
                MessageWithMetadata(
                    message=message,
                    metadata=Metadata(
                        topic_name=str(sample.key_expr),
                        message_type_decoded=type(message).__name__,
                        bytes_transmitted=len(sample.payload),
                    ),
                )
            )

        self._inner.subscribe(_decode_message)

    def receive(self) -> T:
        """Receive a message from the topic."""
        sample = self._inner.subscriber.recv()
        message = self._message_type()
        message.ParseFromString(sample.payload.to_bytes())
        return message

    def receive_with_metadata(self) -> MessageWithMetadata[T]:
        """Receive a message from the topic."""
        sample = self._inner.subscriber.recv()
        message = self._message_type()
        message.ParseFromString(sample.payload.to_bytes())
        return MessageWithMetadata(
            message=message,
            metadata=Metadata(
                topic_name=str(sample.key_expr),
                message_type_decoded=type(message).__name__,
                bytes_transmitted=len(sample.payload),
            ),
        )


class Subscriber:
    """A topic used for subscribing to messages with individual polling threads."""

    def __init__(self, name: str, session: zenoh.Session):
        self.name = name
        self._session = session
        self._threads = []

    def subscribe(self, callback: Callable) -> None:
        """Creates a new subscriber with its own ring buffer and polling thread."""

        def polling_loop():
            """Threaded loop to poll messages in a blocking fashion."""
            # Declare a new subscriber with the ring buffer
            ring_channel = RingChannel(1)
            with self._session.declare_subscriber(self.name, ring_channel) as sub:
                for sample in sub:
                    try:
                        callback(sample)  # Process the message
                    except Exception as e:
                        print(f"Error in callback for topic '{self.name}': {e}")

        # Start a new thread for this subscriber
        thread = threading.Thread(target=polling_loop, daemon=True)
        thread.start()
        self._threads.append(thread)


@dataclasses.dataclass
class BufferMessage:
    message: Message
    metadata: Metadata
    timestamp: datetime.datetime
    reference_id: Optional[int]

    @staticmethod
    def from_message(message_with_metadata: MessageWithMetadata[T]) -> "BufferMessage":
        # check if message has header field
        if message_with_metadata.message.HasField("header"):
            return BufferMessage(
                message=message_with_metadata.message,
                metadata=message_with_metadata.metadata,
                timestamp=message_with_metadata.message.header.timestamp.ToDatetime(),
                reference_id=message_with_metadata.message.header.reference_id
            )


        return BufferMessage(
            message=message_with_metadata.message,
            metadata=message_with_metadata.metadata,
            timestamp=message_with_metadata.message.timestamp.ToDatetime(),
            reference_id=None
        )

class MessageGrouper:

    @abc.abstractmethod
    def message_group_matches(self, messages: List[BufferMessage]) -> bool:
        pass


class ReferenceIdGrouper(MessageGrouper):

    def message_group_matches(self, messages: List[BufferMessage]) -> bool:
        if len(messages) < 2:
            return True
        reference_ids = set(msg.reference_id for msg in messages)
        return len(reference_ids) == 1


class TimestampGrouper(MessageGrouper):
    def __init__(self, delta_time: float):
        self._delta_time: timedelta = timedelta(seconds=delta_time)

    def message_group_matches(self, messages: List[BufferMessage]) -> bool:
        timestamps = [msg.timestamp for msg in messages]
        if max(timestamps) - min(timestamps) <= self._delta_time:
            return True
        return False


class GroupOn:
    TIMESTAMP = TimestampGrouper
    REFERENCE_ID = ReferenceIdGrouper


class MultiSubscriber:
    """Handles synchronized subscription to multiple topics."""

    def __init__(
            self,
            # delta_time: float = 0.1,
            group_on: MessageGrouper
    ):
        self._subscriber_topics: List[TypedSubscriber] = []
        self._buffers: Dict[str, deque] = {}
        # self._delta_time: timedelta = timedelta(seconds=delta_time)
        self._group_on = group_on
        self._lock: threading.Lock = threading.Lock()

    def _buffer_message(self, callback: Callable[[T], None], message_with_metadata: MessageWithMetadata[T]):
        message, metadata = message_with_metadata.message, message_with_metadata.metadata
        with self._lock:
            self._buffers[metadata.topic_name].append(
                BufferMessage.from_message(message_with_metadata)
                # {"message": message, "metadata": metadata, "timestamp": message.timestamp.ToDatetime()}
            )
            self._try_match_messages(callback=callback)

    def _buffer_message_with_metadata(
            self, callback: Callable[[T_M], None], message_with_metadata: MessageWithMetadata[T]
    ):
        message, metadata = message_with_metadata.message, message_with_metadata.metadata
        with self._lock:
            self._buffers[metadata.topic_name].append(
                BufferMessage.from_message(message_with_metadata)
                # {"message": message, "metadata": metadata, "timestamp": message.timestamp.ToDatetime()}
            )
            self._try_match_messages_with_metadata(callback=callback)

    def _try_match_messages_generic(
            self, callback: Callable[[Any], None], message_extractor: Callable[[BufferMessage], Any]
    ):
        while all(self._buffers[topic._inner.name] for topic in self._subscriber_topics):
            msg_group: List[BufferMessage] = [self._buffers[topic._inner.name][0] for topic in self._subscriber_topics]
            if self._group_on.message_group_matches(msg_group):
                messages = tuple(message_extractor(msg) for msg in msg_group)
                callback(messages)
                for topic in self._subscriber_topics:
                    self._buffers[topic._inner.name].popleft()
                return
            else:
                # Remove the oldest message
                oldest_topic_name = min(self._buffers, key=lambda name: self._buffers[name][0].timestamp)
                self._buffers[oldest_topic_name].popleft()

    def _try_match_messages(self, callback: Callable[[T], None]):
        self._try_match_messages_generic(callback, lambda msg: msg.message)

    def _try_match_messages_with_metadata(self, callback: Callable[[T_M], None]):
        self._try_match_messages_generic(
            callback,
            lambda msg: MessageWithMetadata(message=msg.message, metadata=msg.metadata),
        )

    def add_topic(self, topic: TypedSubscriber, max_queue_size: int = 10):
        with self._lock:
            self._subscriber_topics.append(topic)
            self._buffers[topic._inner.name] = deque(maxlen=max_queue_size)

    def subscribe(self, callback: Callable[[Tuple[T, ...]], None]) -> None:
        if not self._subscriber_topics:
            raise ValueError("No topics added to MultiSubscriberTopic. Please call add_topic() first.")
        for topic in self._subscriber_topics:
            topic.subscribe_with_metadata(partial(self._buffer_message, callback))

    def subscribe_with_metadata(self, callback: Callable[[Tuple[T_M, ...]], None]) -> None:
        if not self._subscriber_topics:
            raise ValueError("No topics added to MultiSubscriberTopic. Please call add_topic() first.")
        for topic in self._subscriber_topics:
            topic.subscribe_with_metadata(partial(self._buffer_message_with_metadata, callback))


class _TopicManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._topics: Dict[str, Union[Publisher, Subscriber]] = {}
        self._topic_names: Dict[str, str] = {}
        self._initialized: bool = False

    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure only one instance exists."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def initialize(self):
        """Initialize topics based on the TOPICS environment variable."""
        with self._lock:
            if self._initialized:
                return  # Already initialized

            session = get_session()

            topic_data = parse_topics()

            for topic in topic_data.topics:
                if topic.topic_key in self._topics:
                    continue  # Topic already initialized
                if isinstance(topic, PUB):
                    topic_type = Publisher(
                        name=topic.topic_key,
                        session=session,
                    )
                elif isinstance(topic, SUB):
                    topic_type = Subscriber(
                        name=topic.topic_key,
                        session=session,
                    )
                else:
                    raise ValueError(f"Invalid topic type {topic.topic_type}")
                self._topics[topic.topic_key] = topic_type
                self._topic_names[topic.topic_name] = topic.topic_key

            self._initialized = True

    def _get_untyped_topic(self, name: str) -> Union[Publisher, Subscriber]:
        """Retrieve a topic by name."""
        if not self._initialized:
            raise RuntimeError("TopicManager not initialized. Call initialize() first.")
        if name not in self._topics:
            available_topics = ", ".join(self._topics.keys())
            raise ValueError(f"Topic '{name}' not found. Available topics: {available_topics}")
        return self._topics[name]

    def get_publisher_topic(self, name: str, message_type: Type[T]) -> TypedPublisher[T]:
        """Retrieve a publisher topic by name."""
        name = self.resolve_topic_name(name=name)

        try:
            topic = self._get_untyped_topic(name=name)
        except ValueError as e:
            if IS_IN_RELEASE_MODE:
                raise e
            else:
                return TypedPublisher(inner=Publisher(name=name, session=get_session()), message_type=message_type)

        if not isinstance(topic, Publisher):
            raise ValueError(f"Topic '{name}' is not a publisher topic.")
        return TypedPublisher(inner=topic, message_type=message_type)

    def get_subscriber_topic(self, name: str, message_type: Type[T]) -> TypedSubscriber[T]:
        """Retrieve a topic by name."""
        name = self.resolve_topic_name(name=name)
        try:
            topic = self._get_untyped_topic(name=name)
        except ValueError as e:
            if IS_IN_RELEASE_MODE:
                raise e
            else:
                return TypedSubscriber(inner=Subscriber(name=name, session=get_session()), message_type=message_type)
        if not isinstance(topic, Subscriber):
            raise ValueError(f"Topic '{name}' is not a subscriber topic.")
        return TypedSubscriber(inner=topic, message_type=message_type)

    def resolve_topic_name(self, name: str) -> str:
        """Resolve a topic name to a topic key."""
        if not self._initialized:
            raise RuntimeError("TopicManager not initialized. Call initialize() first.")
        if name not in self._topic_names:
            if IS_IN_RELEASE_MODE:
                raise ValueError(f"Topic name '{name}' not found.")
            else:
                return name
        return self._topic_names[name]


def get_publisher(name: str, message_type: Type[T]) -> TypedPublisher[T]:
    """Retrieve a publisher topic by name.

    Args:
        name: The name of the topic to retrieve used in the `MAKE87.yml` file.
        message_type: The type of message to be published.

    Returns:
        The publisher topic object.

    Raises:
        RuntimeError: If the make87 library has not been initialized correctly. Call `make87.initialize()`.
        ValueError: If the topic is not found.
        ValueError: If the topic is not a publisher topic.

    """
    return _TopicManager.get_instance().get_publisher_topic(name=name, message_type=message_type)


def get_subscriber(name: str, message_type: Type[T]) -> TypedSubscriber[T]:
    """Retrieve a subscriber topic by name.

    Args:
        name: The name of the topic to retrieve used in the `MAKE87.yml` file.
        message_type: The type of message to be subscribed to. Will be used for automatic decoding.

    Returns:
        The subscriber topic object.

    Raises:
        RuntimeError: If the make87 library has not been initialized correctly. Call `make87.initialize()`.
        ValueError: If the topic is not found.
        ValueError: If the topic is not a subscriber topic.
    """
    return _TopicManager.get_instance().get_subscriber_topic(name=name, message_type=message_type)


def get_multi_subscriber(topics: Dict[str, Union[Type[T], Tuple[Type[T], int]]],
                         group_on: Optional[MessageGrouper] = None) -> MultiSubscriber:
    if group_on is None:
        group_on = GroupOn.REFERENCE_ID()

    multi_subscriber = MultiSubscriber(group_on=group_on)
    for name, val in topics.items():
        if isinstance(val, tuple):
            message_type, max_queue_size = val
        else:
            message_type, max_queue_size = val, 10
        multi_subscriber.add_topic(
            topic=get_subscriber(name=name, message_type=message_type),
            max_queue_size=max_queue_size,
        )
    return multi_subscriber


def resolve_topic_name(name: str) -> str:
    """Resolve a topic name to its dynamic topic key.

    Args:
        name: Name of the topic used in the `MAKE87.yml` file.

    Returns:
        The dynamic topic key used to reference the topic.

    Raises:
        RuntimeError: If the make87 library has not been initialized correctly. Call `make87.initialize()`.
        ValueError: If the topic name is not found.
    """
    return _TopicManager.get_instance().resolve_topic_name(name)
