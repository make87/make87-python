from enum import Enum
from typing import Annotated, Literal, Union, Optional

import zenoh
from pydantic import BaseModel, Field


class Priority(str, Enum):
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
    BEST_EFFORT = "BEST_EFFORT"
    RELIABLE = "RELIABLE"

    DEFAULT = RELIABLE

    def to_zenoh(self):
        if self == Reliability.BEST_EFFORT:
            return zenoh.Reliability.BEST_EFFORT
        elif self == Reliability.RELIABLE:
            return zenoh.Reliability.RELIABLE
        elif self == Reliability.DEFAULT:
            return zenoh.Reliability.RELIABLE
        else:
            raise ValueError(f"Unknown Reliability value: {self}")


class CongestionControl(Enum):
    DROP = "DROP"
    BLOCK = "BLOCK"

    DEFAULT = DROP

    def to_zenoh(self):
        if self == CongestionControl.DROP:
            return zenoh.CongestionControl.DROP
        elif self == CongestionControl.BLOCK:
            return zenoh.CongestionControl.BLOCK
        elif self == CongestionControl.DEFAULT:
            return zenoh.CongestionControl.DEFAULT
        else:
            raise ValueError(f"Unknown CongestionControl value: {self}")


class ChannelBase(BaseModel):
    capacity: int


class FifoChannel(ChannelBase):
    handler_type: Literal["FIFO"]

    def to_zenoh(self):
        return zenoh.handlers.FifoChannel(capacity=self.capacity)


class RingChannel(ChannelBase):
    handler_type: Literal["RING"]

    def to_zenoh(self):
        return zenoh.handlers.RingChannel(capacity=self.capacity)


HandlerChannel = Annotated[Union[FifoChannel, RingChannel], Field(discriminator="handler_type")]


class ZenohSubscriberConfig(BaseModel):
    handler: Optional[HandlerChannel] = None


class ZenohPublisherConfig(BaseModel):
    congestion_control: Optional[CongestionControl] = None
    priority: Optional[Priority] = None
    express: Optional[bool] = None
    reliability: Optional[Reliability] = None


class ZenohRequesterConfig(BaseModel):
    congestion_control: Optional[CongestionControl] = None
    priority: Optional[Priority] = None
    express: Optional[bool] = None


class ZenohProviderConfig(BaseModel):
    handler: Optional[HandlerChannel] = None
