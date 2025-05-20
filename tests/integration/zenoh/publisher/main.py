import time

from make87_messages.text.text_plain_pb2 import PlainText
from make87_messages.core.header_pb2 import Header
from make87.interfaces.zenoh import ZenohInterface, ZenohAdapter
from make87.encodings import ProtobufEncoder


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_adapter = ZenohAdapter()
    zenoh_interface = ZenohInterface()

    publisher = zenoh_interface.get_publisher("HELLO_WORLD_MESSAGE")
    header = Header(entity_path="/pytest/pub_sub", reference_id=0)

    while True:
        header.timestamp.GetCurrentTime()
        message = PlainText(header=header, body="Hello, World! 🐍")
        message_encoded = message_encoder.encode(message)
        message_packed = zenoh_adapter.pack(message_encoded)
        publisher.put(message_packed)

        print(f"Published: {message}")
        time.sleep(1)


if __name__ == "__main__":
    main()
