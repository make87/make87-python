"""Zenoh messaging interface model definitions.

This module defines configuration models and enums for Zenoh-based messaging
interfaces, including priority levels, reliability modes, congestion control,
and channel handlers.
"""

from enum import Enum
from typing import Annotated, Literal, Union, Optional

import zenoh
from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Message priority levels for Zenoh communication.

    Defines the priority levels available for Zenoh messages, from real-time
    to background processing. Higher priority messages are processed first.

    Attributes:
        REAL_TIME: Highest priority for time-critical messages
        INTERACTIVE_HIGH: High priority for interactive applications
        INTERACTIVE_LOW: Lower priority for interactive applications
        DATA_HIGH: High priority for data processing
        DATA: Default priority for general data
        DATA_LOW: Lower priority for bulk data
        BACKGROUND: Lowest priority for background tasks
        DEFAULT: Default priority (DATA)
        MIN: Minimum priority (BACKGROUND)
        MAX: Maximum priority (REAL_TIME)
    """

    REAL_TIME = "REAL_TIME"
    INTERACTIVE_HIGH = "INTERACTIVE_HIGH"
    INTERACTIVE_LOW = "INTERACTIVE_LOW"
    DATA_HIGH = "DATA_HIGH"
    DATA = "DATA"
    DATA_LOW = "DATA_LOW"
    BACKGROUND = "BACKGROUND"

    DEFAULT = DATA
    MIN = BACKGROUND
    MAX = REAL_TIME

    def to_zenoh(self):
        """Convert to native Zenoh priority enum.

        Returns:
            Corresponding zenoh.Priority enum value

        Raises:
            ValueError: If the priority value is unknown
        """
        if self == Priority.REAL_TIME:
            return zenoh.Priority.REAL_TIME
        elif self == Priority.INTERACTIVE_HIGH:
            return zenoh.Priority.INTERACTIVE_HIGH
        elif self == Priority.INTERACTIVE_LOW:
            return zenoh.Priority.INTERACTIVE_LOW
        elif self == Priority.DATA_HIGH:
            return zenoh.Priority.DATA_HIGH
        elif self == Priority.DATA:
            return zenoh.Priority.DATA
        elif self == Priority.DATA_LOW:
            return zenoh.Priority.DATA_LOW
        elif self == Priority.BACKGROUND:
            return zenoh.Priority.BACKGROUND
        else:
            raise ValueError(f"Unknown Priority value: {self}")


class Reliability(Enum):
    """Message reliability modes for Zenoh communication.

    Defines the reliability guarantees for message delivery.

    Attributes:
        BEST_EFFORT: No delivery guarantees, lowest overhead
        RELIABLE: Guaranteed delivery with acknowledgments
        DEFAULT: Default reliability mode (RELIABLE)
    """

    BEST_EFFORT = "BEST_EFFORT"
    RELIABLE = "RELIABLE"

    DEFAULT = RELIABLE

    def to_zenoh(self):
        """Convert to native Zenoh reliability enum.

        Returns:
            Corresponding zenoh.Reliability enum value

        Raises:
            ValueError: If the reliability value is unknown
        """
        if self == Reliability.BEST_EFFORT:
            return zenoh.Reliability.BEST_EFFORT
        elif self == Reliability.RELIABLE:
            return zenoh.Reliability.RELIABLE
        elif self == Reliability.DEFAULT:
            return zenoh.Reliability.RELIABLE
        else:
            raise ValueError(f"Unknown Reliability value: {self}")


class CongestionControl(Enum):
    """Congestion control modes for Zenoh communication.

    Defines how to handle network congestion when sending messages.

    Attributes:
        DROP: Drop messages when congested
        BLOCK: Block sender when congested
        DEFAULT: Default congestion control (DROP)
    """

    DROP = "DROP"
    BLOCK = "BLOCK"

    DEFAULT = DROP

    def to_zenoh(self):
        """Convert to native Zenoh congestion control enum.

        Returns:
            Corresponding zenoh.CongestionControl enum value

        Raises:
            ValueError: If the congestion control value is unknown
        """
        if self == CongestionControl.DROP:
            return zenoh.CongestionControl.DROP
        elif self == CongestionControl.BLOCK:
            return zenoh.CongestionControl.BLOCK
        elif self == CongestionControl.DEFAULT:
            return zenoh.CongestionControl.DEFAULT
        else:
            raise ValueError(f"Unknown CongestionControl value: {self}")


class ChannelBase(BaseModel):
    """Base class for Zenoh channel configurations.

    Attributes:
        capacity: Maximum number of messages the channel can buffer
    """

    capacity: int


class FifoChannel(ChannelBase):
    """First-In-First-Out channel configuration.

    Messages are processed in the order they are received. When the channel
    is full, new messages are dropped.

    Attributes:
        handler_type: Always "FIFO" for this channel type
        capacity: Maximum number of messages to buffer
    """

    handler_type: Literal["FIFO"]

    def to_zenoh(self):
        """Convert to native Zenoh FIFO channel handler.

        Returns:
            Configured zenoh.handlers.FifoChannel instance
        """
        return zenoh.handlers.FifoChannel(capacity=self.capacity)


class RingChannel(ChannelBase):
    """Ring buffer channel configuration.

    Messages are stored in a circular buffer. When the channel is full,
    the oldest messages are overwritten by new ones.

    Attributes:
        handler_type: Always "RING" for this channel type
        capacity: Maximum number of messages to buffer
    """

    handler_type: Literal["RING"]

    def to_zenoh(self):
        """Convert to native Zenoh ring channel handler.

        Returns:
            Configured zenoh.handlers.RingChannel instance
        """
        return zenoh.handlers.RingChannel(capacity=self.capacity)


HandlerChannel = Annotated[Union[FifoChannel, RingChannel], Field(discriminator="handler_type")]


class ZenohSubscriberConfig(BaseModel):
    """Configuration for Zenoh subscribers.

    Attributes:
        handler: Optional channel handler for buffering received messages
    """

    handler: Optional[HandlerChannel] = None


class ZenohPublisherConfig(BaseModel):
    """Configuration for Zenoh publishers.

    Attributes:
        congestion_control: How to handle network congestion
        priority: Message priority level
        express: Whether to use express delivery (bypass some routing)
        reliability: Message delivery reliability mode
    """

    congestion_control: Optional[CongestionControl] = None
    priority: Optional[Priority] = None
    express: Optional[bool] = None
    reliability: Optional[Reliability] = None


class ZenohQuerierConfig(BaseModel):
    """Configuration for Zenoh query clients.

    Attributes:
        congestion_control: How to handle network congestion
        priority: Query priority level
        express: Whether to use express delivery (bypass some routing)
    """

    congestion_control: Optional[CongestionControl] = None
    priority: Optional[Priority] = None
    express: Optional[bool] = None


class ZenohQueryableConfig(BaseModel):
    """Configuration for Zenoh queryable servers.

    Attributes:
        handler: Optional channel handler for buffering incoming queries
    """

    handler: Optional[HandlerChannel] = None
