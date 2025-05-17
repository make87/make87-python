from typing import Type
from google.protobuf.message import Message

from make87.encodings.base import Encoder


class ProtobufEncoder(Encoder[Message]):
    def __init__(self, message_type: Type[Message]) -> None:
        """
        message_type: The specific protobuf Message class to encode/decode.
        """
        self.message_type = message_type

    def encode(self, obj: Message) -> bytes:
        """
        Serialize a protobuf Message to bytes.
        """
        return obj.SerializeToString()

    def decode(self, data: bytes) -> Message:
        """
        Deserialize bytes to a protobuf Message.
        """
        message = self.message_type()
        message.ParseFromString(data)
        return message
