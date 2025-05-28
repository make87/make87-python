from abc import ABC, abstractmethod
from typing import Any, Literal, Optional, Union, overload

from make87.config import load_config_from_env
from make87.internal.models.application_env_config import (
    BoundSubscriber,
    BoundRequester,
    BoundClient,
    ServerServiceConfig,
    InterfaceConfig,
)
from make87.models import (
    ApplicationConfig,
    ProviderEndpointConfig,
    PublisherTopicConfig,
)


class InterfaceBase(ABC):
    """
    Abstract base class for messaging interfaces.
    Handles publisher/subscriber setup.
    """

    def __init__(self, name: str, make87_config: Optional[ApplicationConfig] = None):
        """
        Initialize the interface with a configuration object.
        If no config is provided, it will attempt to load from the environment.
        """
        if make87_config is None:
            make87_config = load_config_from_env()
        self._name = name
        self._config = make87_config

    @overload
    def get_interface_type_by_name(self, name: str, iface_type: Literal["PUB"]) -> PublisherTopicConfig: ...

    @overload
    def get_interface_type_by_name(self, name: str, iface_type: Literal["SUB"]) -> BoundSubscriber: ...

    @overload
    def get_interface_type_by_name(self, name: str, iface_type: Literal["REQ"]) -> BoundRequester: ...

    @overload
    def get_interface_type_by_name(self, name: str, iface_type: Literal["PRV"]) -> ProviderEndpointConfig: ...

    @overload
    def get_interface_type_by_name(self, name: str, iface_type: Literal["CLI"]) -> BoundClient: ...

    @overload
    def get_interface_type_by_name(self, name: str, iface_type: Literal["SRV"]) -> ServerServiceConfig: ...

    def get_interface_type_by_name(
        self, name: str, iface_type: Literal["PUB", "SUB", "REQ", "PRV", "CLI", "SRV"]
    ) -> Union[
        PublisherTopicConfig,
        BoundSubscriber,
        BoundRequester,
        ProviderEndpointConfig,
        BoundClient,
        ServerServiceConfig,
    ]:
        """
        Takes a user-level interface name and looks up the corresponding API-level config object.
        """
        if iface_type == "PUB":
            mapped_interface_types = self.interface_config.publishers
        elif iface_type == "SUB":
            mapped_interface_types = self.interface_config.subscribers
        elif iface_type == "REQ":
            mapped_interface_types = self.interface_config.requesters
        elif iface_type == "PRV":
            mapped_interface_types = self.interface_config.providers
        elif iface_type == "CLI":
            mapped_interface_types = self.interface_config.clients
        elif iface_type == "SRV":
            mapped_interface_types = self.interface_config.servers
        else:
            raise NotImplementedError(f"Interface type {iface_type} is not supported.")

        try:
            return mapped_interface_types[name]
        except KeyError:
            raise KeyError(f"{iface_type} with name {name} not found in interface {self._name}.")

    @property
    def name(self) -> str:
        """
        Return the name of the interface.
        """
        return self._name

    @property
    def interface_config(self) -> InterfaceConfig:
        """
        Return the application configuration for this interface.
        """
        return self._config.interfaces.get(self._name)

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

    @abstractmethod
    def get_client(self, name: str) -> Any:
        """
        Set up a client for the given topic.
        The callback receives user-level decoded messages of type T.
        """
        pass

    @abstractmethod
    def get_server(self, name: str) -> Any:
        """
        Set up a server for the given topic.
        The callback receives user-level decoded messages of type T.
        """
        pass


class GenericInterface(InterfaceBase):
    def get_publisher(self, name: str) -> Any:
        """
        Return a generic publisher for the given topic.
        This is a placeholder implementation and should be overridden in subclasses.
        """
        raise NotImplementedError(
            "GenericInterface does not implement get_publisher. It only provides access to configuration information."
        )

    def get_subscriber(self, name: str) -> Any:
        """
        Return a generic subscriber for the given topic.
        This is a placeholder implementation and should be overridden in subclasses.
        """
        raise NotImplementedError(
            "GenericInterface does not implement get_subscriber. It only provides access to configuration information."
        )

    def get_requester(self, name: str) -> Any:
        """
        Return a generic requester for the given topic.
        This is a placeholder implementation and should be overridden in subclasses.
        """
        raise NotImplementedError(
            "GenericInterface does not implement get_requester. It only provides access to configuration information."
        )

    def get_provider(self, name: str) -> Any:
        """
        Return a generic provider for the given topic.
        This is a placeholder implementation and should be overridden in subclasses.
        """
        raise NotImplementedError(
            "GenericInterface does not implement get_provider. It only provides access to configuration information."
        )

    def get_client(self, name: str) -> Any:
        """
        Return a generic client for the given topic.
        This is a placeholder implementation and should be overridden in subclasses.
        """
        raise NotImplementedError(
            "GenericInterface does not implement get_client. It only provides access to configuration information."
        )

    def get_server(self, name: str) -> Any:
        """
        Return a generic server for the given topic.
        This is a placeholder implementation and should be overridden in subclasses.
        """
        raise NotImplementedError(
            "GenericInterface does not implement get_server. It only provides access to configuration information."
        )
