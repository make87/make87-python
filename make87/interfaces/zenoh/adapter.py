from typing import Tuple, Optional

import zenoh
from zenoh.zenoh import ZBytes

from make87.protocols.base import ProtocolAdapter


class ZenohAdapter(ProtocolAdapter[zenoh.ZBytes, zenoh.Sample]):
    """
    Adapter for converting between bytes and Zenoh protocol-native message objects.
    """

    def pack(self, payload: bytes, **metadata) -> zenoh.ZBytes:
        return zenoh.ZBytes(payload)

    def unpack(
        self, message: zenoh.Sample
    ) -> Tuple[
        bytes,
        zenoh.KeyExpr,
        zenoh.SampleKind,
        zenoh.Encoding,
        zenoh.Timestamp,
        zenoh.CongestionControl,
        zenoh.Priority,
        bool,
        Optional[ZBytes],
    ]:
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
