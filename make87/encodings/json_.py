"""JSON encoder for serializing Python objects to JSON format.

This module provides a JSON-based encoder that converts Python objects
to UTF-8 encoded JSON bytes and vice versa, with support for custom
serialization and deserialization hooks.
"""

import json
from typing import Any, Callable, Optional, TypeVar

from make87.encodings.base import Encoder

T = TypeVar("T")


class JsonEncoder(Encoder[T]):
    """JSON encoder for Python objects.

    This encoder converts Python objects to UTF-8 encoded JSON bytes
    and deserializes JSON bytes back to Python objects. It supports
    custom serialization and deserialization hooks for complex objects.

    Attributes:
        object_hook: Custom deserialization function for complex objects
        default: Custom serialization function for complex objects
    """

    def __init__(
        self, *, object_hook: Optional[Callable[[dict], T]] = None, default: Optional[Callable[[T], Any]] = None
    ) -> None:
        """Initialize the JSON encoder with optional custom hooks.

        Args:
            object_hook: Custom deserialization function that will be called
                with the result of any object literal decoded (a dict). The
                return value will be used in place of the dict.
            default: Custom serialization function that will be called for
                objects that are not serializable by default. Should return
                a JSON-serializable object or raise TypeError.

        Example:

            >>> # Simple encoder
            >>> encoder = JsonEncoder()
            >>>
            >>> # With custom hooks
            >>> def custom_decoder(d):
            ...     if '__type__' in d:
            ...         return MyClass(**d)
            ...     return d
            >>> def custom_encoder(obj):
            ...     if isinstance(obj, MyClass):
            ...         return {'__type__': 'MyClass', **obj.__dict__}
            ...     raise TypeError
            >>> encoder = JsonEncoder(object_hook=custom_decoder, default=custom_encoder)
        """
        self.object_hook = object_hook
        self.default = default

    def encode(self, obj: T) -> bytes:
        """Serialize a Python object to UTF-8 encoded JSON bytes.

        Args:
            obj: The Python object to serialize

        Returns:
            UTF-8 encoded JSON bytes representation of the object

        Raises:
            ValueError: If JSON encoding fails due to unsupported object types
                or other serialization errors

        Example:

            >>> encoder = JsonEncoder()
            >>> data = {"key": "value", "number": 42}
            >>> encoded = encoder.encode(data)
            >>> print(encoded)
            b'{"key": "value", "number": 42}'
        """
        try:
            return json.dumps(obj, default=self.default).encode("utf-8")
        except Exception as e:
            raise ValueError(f"JSON encoding failed: {e}")

    def decode(self, data: bytes) -> T:
        """Deserialize UTF-8 encoded JSON bytes to a Python object.

        Args:
            data: UTF-8 encoded JSON bytes to deserialize

        Returns:
            The deserialized Python object

        Raises:
            ValueError: If JSON decoding fails due to invalid JSON data
                or encoding issues

        Example:

            >>> encoder = JsonEncoder()
            >>> data = b'{"key": "value", "number": 42}'
            >>> decoded = encoder.decode(data)
            >>> print(decoded)
            {'key': 'value', 'number': 42}
        """
        try:
            return json.loads(data.decode("utf-8"), object_hook=self.object_hook)
        except Exception as e:
            raise ValueError(f"JSON decoding failed: {e}")
