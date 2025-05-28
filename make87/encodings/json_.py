import json
from typing import Any, Callable, Optional, TypeVar

from make87.encodings.base import Encoder

T = TypeVar("T")


class JsonEncoder(Encoder[T]):
    def __init__(
        self, *, object_hook: Optional[Callable[[dict], T]] = None, default: Optional[Callable[[T], Any]] = None
    ) -> None:
        """
        object_hook: custom deserialization function for complex objects
        default: custom serialization function for complex objects
        """
        self.object_hook = object_hook
        self.default = default

    def encode(self, obj: T) -> bytes:
        """
        Serialize a Python object to UTF-8 encoded JSON bytes.
        """
        try:
            return json.dumps(obj, default=self.default).encode("utf-8")
        except Exception as e:
            raise ValueError(f"JSON encoding failed: {e}")

    def decode(self, data: bytes) -> T:
        """
        Deserialize UTF-8 encoded JSON bytes to a Python object.
        """
        try:
            return json.loads(data.decode("utf-8"), object_hook=self.object_hook)
        except Exception as e:
            raise ValueError(f"JSON decoding failed: {e}")
