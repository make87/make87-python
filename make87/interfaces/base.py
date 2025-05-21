from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Tuple, Literal, Union, overload, Optional

from make87.config import load_config_from_env
from make87.models.application_env_config import (
    TopicConfigPub,
    TopicConfigSub,
    EndpointConfigReq,
    EndpointConfigPrv,
    ApplicationEnvConfig,
)

SendT = TypeVar("SendT")  # Protocol "send" type (e.g., zenoh.ZBytes)
RecvT = TypeVar("RecvT")  # Protocol "receive" type (e.g., zenoh.Sample)


class InterfaceBase(ABC):
    """
    Abstract base class for messaging interfaces.
    Handles publisher/subscriber setup.
    """

    def __init__(self, make87_config: Optional[ApplicationEnvConfig] = None):
        """
        Initialize the interface with a configuration object.
        If no config is provided, it will attempt to load from the environment.
        """
        if make87_config is None:
            make87_config = load_config_from_env()
        self._config = make87_config

    @overload
    def get_interface_config_by_name(self, name: str, iface_type: Literal["PUB"]) -> TopicConfigPub: ...

    @overload
    def get_interface_config_by_name(self, name: str, iface_type: Literal["SUB"]) -> TopicConfigSub: ...

    @overload
    def get_interface_config_by_name(self, name: str, iface_type: Literal["REQ"]) -> EndpointConfigReq: ...

    @overload
    def get_interface_config_by_name(self, name: str, iface_type: Literal["PRV"]) -> EndpointConfigPrv: ...

    def get_interface_config_by_name(
        self, name: str, iface_type: Literal["PUB", "SUB", "REQ", "PRV"]
    ) -> Union[TopicConfigPub, TopicConfigSub, EndpointConfigReq, EndpointConfigPrv]:
        """
        Takes a user-level interface name and looks up the corresponding API-level config object.
        """
        if iface_type == "PUB":
            try:
                return next(
                    cfg.root
                    for cfg in self._config.topics
                    if isinstance(cfg.root, TopicConfigPub) and cfg.root.topic_name == name
                )
            except StopIteration:
                raise KeyError(f"Publisher with name {name} not found.")
        elif iface_type == "SUB":
            try:
                return next(
                    cfg.root
                    for cfg in self._config.topics
                    if isinstance(cfg.root, TopicConfigSub) and cfg.root.topic_name == name
                )
            except StopIteration:
                raise KeyError(f"Subscriber with name {name} not found.")
        elif iface_type == "REQ":
            try:
                return next(
                    cfg.root
                    for cfg in self._config.endpoints
                    if isinstance(cfg.root, EndpointConfigReq) and cfg.root.endpoint_name == name
                )
            except StopIteration:
                raise KeyError(f"Requester with name {name} not found.")
        elif iface_type == "PRV":
            try:
                return next(
                    cfg.root
                    for cfg in self._config.endpoints
                    if isinstance(cfg.root, EndpointConfigPrv) and cfg.root.endpoint_name == name
                )
            except StopIteration:
                raise KeyError(f"Provider with name {name} not found.")
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
