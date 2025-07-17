from abc import ABC
from typing import Literal, Optional, Union, overload

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
