from typing import TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar("T")  # The Python object type to encode/decode (e.g. dict, custom class)


class Encoder(ABC, Generic[T]):
    """Serializes (encode) and deserializes (decode) user objects to/from bytes."""

    @abstractmethod
    def encode(self, obj: T) -> bytes:
        """Serialize an object to bytes."""
        pass

    @abstractmethod
    def decode(self, data: bytes) -> T:
        """Deserialize bytes to an object."""
        pass
