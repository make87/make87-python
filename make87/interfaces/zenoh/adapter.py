from typing import Tuple, Optional, Union, overload

import zenoh
from zenoh.zenoh import ZBytes

from make87.interfaces.base import InterfaceAdapter

# Type aliases for unpack return types
UnpackSampleReturn = Tuple[
    bytes,
    zenoh.KeyExpr,
    zenoh.SampleKind,
    zenoh.Encoding,
    zenoh.Timestamp,
    zenoh.CongestionControl,
    zenoh.Priority,
    bool,
    Optional[ZBytes],
]
UnpackQueryReturn = Tuple[
    Optional[bytes],
    zenoh.KeyExpr,
    zenoh.Selector,
    zenoh.Parameters,
    Optional[zenoh.Encoding],
    Optional[ZBytes],
]
UnpackReplyErrorReturn = Tuple[
    bytes,
    zenoh.Encoding,
]


class ZenohAdapter(InterfaceAdapter[zenoh.ZBytes, Union[zenoh.Sample, zenoh.Query, zenoh.ReplyError]]):
    """
    Adapter for converting between bytes and Zenoh interface-native message objects.
    """

    def pack(self, payload: bytes, **metadata) -> zenoh.ZBytes:
        return zenoh.ZBytes(payload)

    def unpack_sample(self, message: zenoh.Sample) -> UnpackSampleReturn:
        return (
            message.payload.to_bytes(),
            message.key_expr,
            message.kind,
            message.encoding,
            message.timestamp,
            message.congestion_control,
            message.priority,
            message.express,
            message.attachment,
        )

    def unpack_query(self, message: zenoh.Query) -> UnpackQueryReturn:
        return (
            message.payload.to_bytes(),
            message.key_expr,
            message.selector,
            message.parameters,
            message.encoding,
            message.attachment,
        )

    def unpack_reply_error(self, message: zenoh.ReplyError) -> UnpackReplyErrorReturn:
        return (
            message.payload.to_bytes(),
            message.encoding,
        )

    @overload
    def unpack(self, message: zenoh.Sample) -> UnpackSampleReturn: ...

    @overload
    def unpack(self, message: zenoh.Query) -> UnpackQueryReturn: ...

    @overload
    def unpack(self, message: zenoh.ReplyError) -> UnpackReplyErrorReturn: ...

    def unpack(
        self, message: Union[zenoh.Sample, zenoh.Query, zenoh.ReplyError]
    ) -> Union[
        UnpackSampleReturn,
        UnpackQueryReturn,
        UnpackReplyErrorReturn,
    ]:
        if isinstance(message, zenoh.Sample):
            return self.unpack_sample(message)
        elif isinstance(message, zenoh.Query):
            return self.unpack_query(message)
        elif isinstance(message, zenoh.ReplyError):
            return self.unpack_reply_error(message)

        raise TypeError(f"Unsupported message type: {type(message)}. Expected zenoh.Sample or zenoh.Reply.")
