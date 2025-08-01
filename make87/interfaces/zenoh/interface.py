"""Zenoh messaging interface implementation.

This module provides the ZenohInterface class which implements the Make87
messaging interface using the Zenoh protocol. It supports publishers,
subscribers, queriers, and queryables with configurable QoS settings.
"""

import json
import logging
from typing import Any, Callable, Optional, Union
import zenoh
import socket
from functools import cached_property
from make87.interfaces.base import InterfaceBase
from make87.interfaces.zenoh.model import (
    ZenohPublisherConfig,
    ZenohSubscriberConfig,
    ZenohQuerierConfig,
    ZenohQueryableConfig,
)

logger = logging.getLogger(__name__)


class ZenohInterface(InterfaceBase):
    """Concrete Zenoh implementation of the Make87 messaging interface.

    This class provides a Zenoh-based implementation of the Make87 messaging
    interface, supporting publish/subscribe and query/response patterns with
    configurable Quality of Service (QoS) settings.

    The interface lazily initializes Zenoh configuration and session for efficiency,
    and automatically configures network endpoints based on the application configuration.

    Attributes:
        zenoh_config: Cached Zenoh configuration object
        session: Cached Zenoh session for communication
    """

    @cached_property
    def zenoh_config(self) -> zenoh.Config:
        """Get or create the Zenoh configuration.

        Lazily creates and configures a Zenoh configuration object with
        appropriate network endpoints based on the interface configuration.

        Returns:
            Configured zenoh.Config instance

        Note:
            The configuration automatically sets up:
            - Listen endpoints on port 7447 if available
            - Connect endpoints based on configured peers
        """
        cfg = zenoh.Config()

        if not is_port_in_use(7447):
            cfg.insert_json5("listen/endpoints", json.dumps(["tcp/0.0.0.0:7447"]))

        endpoints = {
            f"tcp/{x.vpn_ip}:{x.vpn_port}"
            for x in list(self.interface_config.requesters.values()) + list(self.interface_config.subscribers.values())
        }
        cfg.insert_json5("connect/endpoints", json.dumps(list(endpoints)))
        return cfg

    @cached_property
    def session(self) -> zenoh.Session:
        """Get or create the Zenoh session.

        Lazily creates and caches a Zenoh session using the configured
        Zenoh configuration.

        Returns:
            Active zenoh.Session instance for communication
        """
        return zenoh.open(self.zenoh_config)

    def get_publisher(self, name: str) -> zenoh.Publisher:
        """Create a Zenoh publisher for the specified interface name.

        Args:
            name: The name of the publisher interface as defined in configuration

        Returns:
            Configured zenoh.Publisher instance

        Note:
            The publisher is not cached, and it is the user's responsibility
            to manage its lifecycle. The publisher will be configured with
            QoS settings from the interface configuration.

        Example:

            >>> interface = ZenohInterface("my_interface")
            >>> publisher = interface.get_publisher("output_topic")
            >>> publisher.put("Hello, World!")
        """
        iface_config = self.get_interface_type_by_name(name=name, iface_type="PUB")
        qos_config = ZenohPublisherConfig.model_validate(iface_config.model_extra)

        return self.session.declare_publisher(
            key_expr=iface_config.topic_key,
            congestion_control=qos_config.congestion_control.to_zenoh() if qos_config.congestion_control else None,
            priority=qos_config.priority.to_zenoh() if qos_config.priority else None,
            express=qos_config.express,
            reliability=qos_config.reliability.to_zenoh() if qos_config.reliability else None,
        )

    def get_subscriber(
        self,
        name: str,
        handler: Optional[Union[Callable[[zenoh.Sample], Any], zenoh.handlers.Callback]] = None,
    ) -> zenoh.Subscriber:
        """Create a Zenoh subscriber for the specified interface name.

        Args:
            name: The name of the subscriber interface as defined in configuration
            handler: Optional message handler. Can be a Python function accepting
                a zenoh.Sample, or a Zenoh callback handler. If None, a channel
                handler will be created from configuration.

        Returns:
            Configured zenoh.Subscriber instance

        Note:
            If a custom handler is provided, any handler configuration values
            will be ignored. The subscriber will use the configured topic key
            and channel settings.

        Example:

            >>> interface = ZenohInterface("my_interface")
            >>> def handle_message(sample):
            ...     print(f"Received: {sample.value}")
            >>> subscriber = interface.get_subscriber("input_topic", handle_message)
        """
        iface_config = self.get_interface_type_by_name(name=name, iface_type="SUB")
        qos_config = ZenohSubscriberConfig.model_validate(iface_config.model_extra)

        if handler is None:
            handler = qos_config.handler.to_zenoh() if qos_config.handler is not None else None
        else:
            logging.warning(
                "Application code defines a custom handler for the subscriber. Any handler config values for will be ignored."
            )

        return self.session.declare_subscriber(
            key_expr=iface_config.topic_key,
            handler=handler,
        )

    def get_querier(
        self,
        name: str,
    ) -> zenoh.Querier:
        """Create a Zenoh querier for the specified interface name.

        Queriers are used for making requests in the query/response pattern.

        Args:
            name: The name of the querier interface as defined in configuration

        Returns:
            Configured zenoh.Querier instance

        Note:
            The querier will be configured with QoS settings from the interface
            configuration including congestion control, priority, and express delivery.

        Example:

            >>> interface = ZenohInterface("my_interface")
            >>> querier = interface.get_querier("api_client")
            >>> replies = querier.get("some/query")
        """
        iface_config = self.get_interface_type_by_name(name=name, iface_type="REQ")
        qos_config = ZenohQuerierConfig.model_validate(iface_config.model_config)

        return self.session.declare_querier(
            key_expr=iface_config.endpoint_key,
            congestion_control=qos_config.congestion_control.to_zenoh() if qos_config.congestion_control else None,
            priority=qos_config.priority.to_zenoh() if qos_config.priority else None,
            express=qos_config.express,
        )

    def get_queryable(
        self,
        name: str,
        handler: Optional[Union[Callable[[zenoh.Query], Any], zenoh.handlers.Callback]] = None,
    ) -> zenoh.Queryable:
        """Create a Zenoh queryable for the specified interface name.

        Queryables are used for handling requests in the query/response pattern.

        Args:
            name: The name of the queryable interface as defined in configuration
            handler: Optional query handler. Can be a Python function accepting
                a zenoh.Query, or a Zenoh callback handler. If None, a channel
                handler will be created from configuration.

        Returns:
            Configured zenoh.Queryable instance

        Note:
            If a custom handler is provided, any handler configuration values
            will be ignored. The handler should process queries and send responses.

        Example:

            >>> interface = ZenohInterface("my_interface")
            >>> def handle_query(query):
            ...     query.reply(zenoh.Sample("response/key", "response data"))
            >>> queryable = interface.get_queryable("api_server", handle_query)
        """
        iface_config = self.get_interface_type_by_name(name=name, iface_type="PRV")
        qos_config = ZenohQueryableConfig.model_validate(iface_config.model_config)

        if handler is None:
            handler = qos_config.handler.to_zenoh() if qos_config.handler is not None else None
        else:
            logging.warning(
                "Application code defines a custom handler for the queryable. Any handler config values for will be ignored."
            )

        return self.session.declare_queryable(
            key_expr=iface_config.endpoint_key,
            handler=handler,
        )


def is_port_in_use(port: int, host: str = "0.0.0.0") -> bool:
    """Check if a network port is currently in use.

    Args:
        port: The port number to check
        host: The host address to check. Defaults to "0.0.0.0" (all interfaces)

    Returns:
        True if the port is in use, False if it's available

    Note:
        This function attempts to bind to the specified port. If the bind
        succeeds, the port is available. If it fails with OSError, the
        port is already in use.

    Example:

        >>> if is_port_in_use(8080):
        ...     print("Port 8080 is busy")
        ... else:
        ...     print("Port 8080 is available")
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return False  # Not in use
        except OSError:
            logger.info(f"Port {port} is already in use on {host}.")
            return True  # Already bound
