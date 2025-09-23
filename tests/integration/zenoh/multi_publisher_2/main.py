import time

from make87_messages.text.text_plain_pb2 import PlainText
from make87_messages.core.header_pb2 import Header
from make87.interfaces.zenoh import ZenohInterface
from make87.encodings import ProtobufEncoder


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_interface = ZenohInterface(name="zenoh_test")

    publisher = zenoh_interface.get_publisher("PUB_2")
    header = Header(entity_path="/pytest/multi_pub_sub_2", reference_id=2)

    message_count = 0
    while True:
        header.timestamp.GetCurrentTime()
        message = PlainText(header=header, body=f"Hello from Publisher 2! Message #{message_count} 🎯")
        message_encoded = message_encoder.encode(message)
        publisher.put(payload=message_encoded)

        print(f"[Publisher 2] Published: {message.body}")
        message_count += 1
        time.sleep(3)  # Publish every 3 seconds


if __name__ == "__main__":
    main()
