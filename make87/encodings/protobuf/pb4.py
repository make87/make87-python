"""Protocol Buffers encoder implementation for protobuf version 4.

This module provides the ProtobufEncoder class for serializing and deserializing
Protocol Buffers messages to and from bytes, specifically for protobuf version 4.x.
"""

from typing import Type, TypeVar
from google.protobuf.message import Message

from make87.encodings.base import Encoder

T = TypeVar("T", bound=Message)


class ProtobufEncoder(Encoder[T]):
    """Protocol Buffers encoder for protobuf messages.

    This encoder converts Protocol Buffers message objects to bytes and
    deserializes bytes back to protobuf message objects. It requires a
    specific protobuf message type to be specified during initialization.

    Type Parameters:
        T: The specific protobuf Message class this encoder handles

    Attributes:
        message_type: The protobuf Message class used for encoding/decoding
    """

    def __init__(self, message_type: Type[T]) -> None:
        """Initialize the protobuf encoder with a specific message type.

        Args:
            message_type: The specific protobuf Message class to encode/decode.
                This must be a subclass of google.protobuf.message.Message.

        Example:

            >>> from my_protos import MyMessage
            >>> encoder = ProtobufEncoder(MyMessage)
            >>>
            >>> # Create and encode a message
            >>> message = MyMessage()
            >>> message.field = "value"
            >>> encoded = encoder.encode(message)
        """
        self.message_type = message_type

    def encode(self, obj: T) -> bytes:
        """Serialize a protobuf Message to bytes.

        Args:
            obj: The protobuf message instance to serialize

        Returns:
            The serialized message as bytes

        Raises:
            TypeError: If the object is not an instance of the configured message type

        Example:

            >>> encoder = ProtobufEncoder(MyMessage)
            >>> message = MyMessage()
            >>> message.name = "example"
            >>> encoded_bytes = encoder.encode(message)
        """
        return obj.SerializeToString()

    def decode(self, data: bytes) -> T:
        """Deserialize bytes to a protobuf Message.

        Args:
            data: The byte data to deserialize into a protobuf message

        Returns:
            The deserialized protobuf message instance

        Raises:
            google.protobuf.message.DecodeError: If the data cannot be parsed
                as a valid protobuf message of the configured type

        Example:

            >>> encoder = ProtobufEncoder(MyMessage)
            >>> data = b'\\x08\\x96\\x01'  # Some protobuf-encoded bytes
            >>> message = encoder.decode(data)
            >>> print(message.name)
        """
        message = self.message_type()
        message.ParseFromString(data)
        return message
