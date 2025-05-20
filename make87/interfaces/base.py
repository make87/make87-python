from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Tuple, Literal, Union, overload

from make87.config import get_config
from make87.models.application_env_config import (
    TopicPubConfig,
    TopicSubConfig,
    EndpointReqConfig,
    EndpointPrvConfig,
)

SendT = TypeVar("SendT")  # Protocol "send" type (e.g., zenoh.ZBytes)
RecvT = TypeVar("RecvT")  # Protocol "receive" type (e.g., zenoh.Sample)


class Interface(ABC):
    """
    Abstract base class for messaging interfaces.
    Handles publisher/subscriber setup.
    """

    def __init__(self):
        self._config = get_config()

    @overload
    def get_interface_config_by_name(self, name: str, iface_type: Literal["PUB"]) -> TopicPubConfig: ...

    @overload
    def get_interface_config_by_name(self, name: str, iface_type: Literal["SUB"]) -> TopicSubConfig: ...

    @overload
    def get_interface_config_by_name(self, name: str, iface_type: Literal["REQ"]) -> EndpointReqConfig: ...

    @overload
    def get_interface_config_by_name(self, name: str, iface_type: Literal["PRV"]) -> EndpointPrvConfig: ...

    def get_interface_config_by_name(
        self, name: str, iface_type: Literal["PUB", "SUB", "REQ", "PRV"]
    ) -> Union[TopicPubConfig, TopicSubConfig, EndpointReqConfig, EndpointPrvConfig]:
        """
        Takes a user-level interface name and looks up the corresponding API-level config object.
        """
        if iface_type == "PUB":
            return next(
                cfg.root
                for cfg in self._config.topics
                if isinstance(cfg.root, TopicPubConfig) and cfg.root.topic_name == name
            )
        elif iface_type == "SUB":
            return next(
                cfg.root
                for cfg in self._config.topics
                if isinstance(cfg.root, TopicSubConfig) and cfg.root.topic_name == name
            )
        elif iface_type == "REQ":
            return next(
                cfg.root
                for cfg in self._config.endpoints
                if isinstance(cfg.root, EndpointReqConfig) and cfg.root.endpoint_name == name
            )
        elif iface_type == "PRV":
            return next(
                cfg.root
                for cfg in self._config.endpoints
                if isinstance(cfg.root, EndpointPrvConfig) and cfg.root.endpoint_name == name
            )
        else:
            raise NotImplementedError(f"Interface type {iface_type} is not supported.")

    @abstractmethod
    def get_publisher(self, name: str) -> Any:
        """
        Return an interface-native publisher for the given topic.
        """
        pass

    @abstractmethod
    def get_subscriber(self, name: str) -> Any:
        """
        Set up a subscription for the given topic.
        The callback receives user-level decoded messages of type T.
        """
        pass

    @abstractmethod
    def get_requester(self, name: str) -> Any:
        """
        Set up a request handler for the given topic.
        The callback receives user-level decoded messages of type T.
        """
        pass

    @abstractmethod
    def get_provider(self, name: str) -> Any:
        """
        Set up a provider for the given topic.
        The callback receives user-level decoded messages of type T.
        """
        pass


class InterfaceAdapter(ABC, Generic[SendT, RecvT]):
    """
    Base class for interface adapters.

    Methods:
        pack(payload: bytes) -> SendT:
            Packs bytes into a interface-native message object (ready to send).

        unpack(message: RecvT) -> bytes:
            Unpacks the payload bytes from a interface-native message object (ready to decode).
    """

    @abstractmethod
    def pack(self, payload: bytes, **metadata) -> SendT:
        """
        Packs bytes and optional interface metadata into a message object.

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
        Unpacks the interface-native message.
        Returns:
            Tuple: (payload_bytes, ...metadata)
                - payload_bytes (bytes): Always at index 0
                - ...metadata: Any additional interface-specific data
        """
        raise NotImplementedError()
