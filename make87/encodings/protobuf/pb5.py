from typing import Type, TypeVar
from google.protobuf.message import Message

from make87.encodings.base import Encoder

T = TypeVar("T", bound=Message)


class ProtobufEncoder(Encoder[T]):
    def __init__(self, message_type: Type[T]) -> None:
        """
        message_type: The specific protobuf Message class to encode/decode.
        """
        self.message_type = message_type

    def encode(self, obj: T) -> bytes:
        """
        Serialize a protobuf Message to bytes.
        """
        return obj.SerializeToString()

    def decode(self, data: bytes) -> T:
        """
        Deserialize bytes to a protobuf Message.
        """
        message = self.message_type()
        message.ParseFromString(data)
        return message
