from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Tuple

SendT = TypeVar("SendT")  # Protocol "send" type (e.g., zenoh.ZBytes)
RecvT = TypeVar("RecvT")  # Protocol "receive" type (e.g., zenoh.Sample)


class Protocol(ABC):
    """
    Abstract base class for messaging protocols.
    Handles publisher/subscriber setup.
    """

    def __init__(self, make87_config: Any):
        self._make87_config = make87_config

    @abstractmethod
    def get_publisher(self, name: str) -> Any:
        """
        Return a protocol-native publisher for the given topic.
        """
        pass

    @abstractmethod
    def get_subscriber(self, name: str) -> Any:
        """
        Set up a subscription for the given topic.
        The callback receives user-level decoded messages of type T.
        """
        pass


class ProtocolAdapter(ABC, Generic[SendT, RecvT]):
    """
    Base class for protocol adapters.

    Methods:
        pack(payload: bytes) -> SendT:
            Packs bytes into a protocol-native message object (ready to send).

        unpack(message: RecvT) -> bytes:
            Unpacks the payload bytes from a protocol-native message object (ready to decode).
    """

    @abstractmethod
    def pack(self, payload: bytes, **metadata) -> SendT:
        """
        Packs bytes and optional protocol metadata into a message object.

        Args:
            payload (bytes): The main payload.
            **metadata: Any additional fields (key, encoding, etc.)

        Returns:
            M: Protocol-native message
        """
        raise NotImplementedError()

    @abstractmethod
    def unpack(self, message: RecvT) -> Tuple[bytes, ...]:
        """
        Unpacks the protocol-native message.
        Returns:
            Tuple: (payload_bytes, ...metadata)
                - payload_bytes (bytes): Always at index 0
                - ...metadata: Any additional protocol-specific data
        """
        raise NotImplementedError()
