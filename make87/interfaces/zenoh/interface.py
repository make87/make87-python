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
    ZenohRequesterConfig,
    ZenohProviderConfig,
)

logger = logging.getLogger(__name__)

class ZenohInterface(InterfaceBase):
    """
    Concrete Protocol implementation for Zenoh messaging.
    Lazily initializes Zenoh config and session for efficiency.
    """

    @cached_property
    def zenoh_config(self) -> zenoh.Config:
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
        """Lazily create and cache the Zenoh session."""
        return zenoh.open(self.zenoh_config)

    def get_publisher(self, name: str) -> zenoh.Publisher:
        """Declare and return a Zenoh publisher for the given name. The publisher is
        not cached, and it is user responsibility to manage its lifecycle."""
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
        """
        Declare and return a Zenoh subscriber for the given name and handler.
        The handler can be a Python function or a Zenoh callback. If `None` is provided (or omitted),
        a Channel handler will be created from the make87 config values.
        """
        iface_config = self.get_interface_type_by_name(name=name, iface_type="SUB")
        qos_config = ZenohSubscriberConfig.model_validate(iface_config.model_extra)

        if handler is None:
            handler = qos_config.handler.to_zenoh() if qos_config.handler is not None else None
        else:
            logging.warning(
                "Application code defines a custom handler for the provider. Any handler config values for will be ignored."
            )

        return self.session.declare_subscriber(
            key_expr=iface_config.topic_key,
            handler=handler,
        )

    def get_requester(
        self,
        name: str,
    ) -> zenoh.Querier:
        """
        Declare and return a Zenoh querier for the given name.
        """
        iface_config = self.get_interface_type_by_name(name=name, iface_type="REQ")
        qos_config = ZenohRequesterConfig.model_validate(iface_config.model_config)

        return self.session.declare_querier(
            key_expr=iface_config.endpoint_key,
            congestion_control=qos_config.congestion_control.to_zenoh() if qos_config.congestion_control else None,
            priority=qos_config.priority.to_zenoh() if qos_config.priority else None,
            express=qos_config.express,
        )

    def get_provider(
        self,
        name: str,
        handler: Optional[Union[Callable[[zenoh.Query], Any], zenoh.handlers.Callback]] = None,
    ) -> zenoh.Queryable:
        """
        Declare and return a Zenoh queryable for the given name and handler.
        The handler can be a Python function or a Zenoh callback. If `None` is provided (or omitted),
        a Channel handler will be created from the make87 config values.
        """
        iface_config = self.get_interface_type_by_name(name=name, iface_type="PRV")
        qos_config = ZenohProviderConfig.model_validate(iface_config.model_config)

        if handler is None:
            handler = qos_config.handler.to_zenoh() if qos_config.handler is not None else None
        else:
            logging.warning(
                "Application code defines a custom handler for the provider. Any handler config values for will be ignored."
            )

        return self.session.declare_queryable(
            key_expr=iface_config.endpoint_key,
            handler=handler,
        )

    def get_client(self, name: str) -> Any:
        """
        Zenoh does not have a client concept, so this method is not implemented.
        """
        raise NotImplementedError("Zenoh does not support client interfaces.")

    def get_server(self, name: str) -> Any:
        """
        Zenoh does not have a server concept, so this method is not implemented.
        """
        raise NotImplementedError("Zenoh does not support server interfaces.")


def is_port_in_use(port: int, host: str = "0.0.0.0") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return False  # Not in use
        except OSError:
            logger.info(f"Port {port} is already in use on {host}.")
            return True   # Already bound