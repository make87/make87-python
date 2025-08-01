"""Base encoder classes for data serialization and deserialization.

This module provides the abstract base class for all Make87 data encoders,
defining the interface for converting Python objects to and from bytes.
"""

from typing import TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar("T")  # The Python object type to encode/decode (e.g. dict, custom class)


class Encoder(ABC, Generic[T]):
    """Abstract base class for data serialization and deserialization.

    This class defines the interface for all Make87 encoders, providing
    methods to serialize Python objects to bytes and deserialize bytes
    back to Python objects.

    Type Parameters:
        T: The type of Python objects this encoder handles
    """

    @abstractmethod
    def encode(self, obj: T) -> bytes:
        """Serialize a Python object to bytes.

        Args:
            obj: The Python object to serialize

        Returns:
            The serialized object as bytes

        Raises:
            EncodingError: If the object cannot be serialized
        """
        pass

    @abstractmethod
    def decode(self, data: bytes) -> T:
        """Deserialize bytes to a Python object.

        Args:
            data: The byte data to deserialize

        Returns:
            The deserialized Python object

        Raises:
            DecodingError: If the data cannot be deserialized
        """
        pass
