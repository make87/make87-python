"""Base interface classes for Make87 messaging systems.

This module provides the abstract base class for all Make87 messaging interfaces,
including publisher/subscriber, request/response, and client/server patterns.
"""

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
    """Abstract base class for messaging interfaces.

    This class provides a common foundation for all Make87 messaging interfaces,
    handling configuration management and interface type resolution. It supports
    multiple messaging patterns including publish/subscribe, request/response,
    and client/server communication.

    Attributes:
        _name: The name of this interface instance
        _config: The Make87 application configuration
    """

    def __init__(self, name: str, make87_config: Optional[ApplicationConfig] = None):
        """Initialize the interface with a configuration object.

        Args:
            name: The name identifier for this interface instance
            make87_config: Optional ApplicationConfig instance. If not provided,
                configuration will be loaded from the environment.
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
        """Get configuration object for a named interface by type.

        Takes a user-level interface name and looks up the corresponding API-level
        configuration object based on the interface type.

        Args:
            name: The user-defined name of the interface to look up
            iface_type: The type of interface to retrieve. Valid values:
                - "PUB": Publisher topic configuration
                - "SUB": Subscriber configuration
                - "REQ": Requester endpoint configuration
                - "PRV": Provider endpoint configuration
                - "CLI": Client service configuration
                - "SRV": Server service configuration

        Returns:
            The appropriate configuration object for the specified interface type

        Raises:
            KeyError: If the interface name is not found for the specified type
            NotImplementedError: If the interface type is not supported

        Example:

            >>> interface = SomeInterface("my_interface")
            >>> pub_config = interface.get_interface_type_by_name("output", "PUB")
            >>> sub_config = interface.get_interface_type_by_name("input", "SUB")
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
        """Get the name of this interface instance.

        Returns:
            The name identifier for this interface
        """
        return self._name

    @property
    def interface_config(self) -> InterfaceConfig:
        """Get the interface configuration for this instance.

        Returns:
            The InterfaceConfig object containing all interface definitions
            for this named interface

        Raises:
            KeyError: If the interface name is not found in the application config
        """
        return self._config.interfaces.get(self._name)
