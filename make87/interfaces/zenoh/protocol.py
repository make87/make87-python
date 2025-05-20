import json
import logging
from typing import Any, Callable, Optional, Union
import zenoh
from functools import cached_property
from make87.interfaces.base import Interface
from make87.interfaces.zenoh.model import ZenohPublisherConfig


class ZenohInterface(Interface):
    """
    Concrete Protocol implementation for Zenoh messaging.
    Lazily initializes config and session for efficiency.
    """

    @cached_property
    def zenoh_config(self) -> zenoh.Config:
        """Lazily parse and cache the Zenoh config."""
        raise NotImplementedError
        # something like below but with actual config value from env
        return zenoh.Config.from_json5(json.dumps(self._make87_config))

    @cached_property
    def session(self) -> zenoh.Session:
        """Lazily create and cache the Zenoh session."""
        return zenoh.open(self.zenoh_config)

    def _get_encoding(self, name: str) -> zenoh.Encoding:
        raise NotImplementedError

    def _get_congestion_control(self, name: str) -> zenoh.CongestionControl:
        raise NotImplementedError

    def _get_priority(self, name: str) -> zenoh.Priority:
        raise NotImplementedError

    def _get_express(self, name: str) -> bool:
        raise NotImplementedError

    def _get_reliability(self, name: str) -> zenoh.Reliability:
        raise NotImplementedError

    def _get_timeout(self, name: str) -> float:
        raise NotImplementedError

    def get_publisher(self, name: str) -> zenoh.Publisher:
        """Declare and return a Zenoh publisher for the given name. The publisher is
        not cached, and it is user responsibility to manage its lifecycle."""
        iface_config = self.get_interface_config_by_name(name=name, iface_type="PUB")
        iface_zenoh_config = ZenohPublisherConfig.model_validate(iface_config.model_config)

        return self.session.declare_publisher(
            key_expr=iface_config.topic_key,
            congestion_control=iface_zenoh_config.congestion_control.to_zenoh(),
            priority=iface_zenoh_config.priority.to_zenoh(),
            express=iface_zenoh_config.express,
            reliability=iface_zenoh_config.reliability.to_zenoh(),
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
        if handler is None:
            handler = zenoh.RingChannel(...)  # TODO: use config values provided from outside!
        else:
            logging.warning(
                "Application code defines a custom handler for the provider. Any handler config values for will be ignored."
            )

        return self.session.declare_subscriber(
            key_expr=self.resolve_name(name, iface_type="SUB"),
            handler=handler,
        )

    def get_requester(
        self,
        name: str,
    ) -> zenoh.Querier:
        """
        Declare and return a Zenoh querier for the given name.
        """
        return self.session.declare_querier(
            key_expr=self.resolve_name(name, iface_type="REQ"),
            timeout=self._get_timeout(name),
            congestion_control=self._get_congestion_control(name),
            priority=self._get_priority(name),
            express=self._get_express(name),
        )

    def get_provider(
        self,
        name: str,
        handler: Optional[Union[Callable[[zenoh.Query], Any], zenoh.handlers.Callback]] = None,
    ) -> zenoh.Queryable:
        """
        Declare and return a Zenoh queryable for the given name.
        """
        if handler is None:
            handler = zenoh.RingChannel(...)  # TODO: use config values provided from outside!
        else:
            logging.warning(
                "Application code defines a custom handler for the provider. Any handler config values for will be ignored."
            )

        return self.session.declare_queryable(
            key_expr=self.resolve_name(name, iface_type="PRV"),
            handler=handler,
        )
