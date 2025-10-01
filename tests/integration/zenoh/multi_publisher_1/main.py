import time

from make87_messages.text.text_plain_pb2 import PlainText
from make87_messages.core.header_pb2 import Header
from make87.interfaces.zenoh import ZenohInterface
from make87.encodings import ProtobufEncoder


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_interface = ZenohInterface(name="zenoh_test")

    publisher = zenoh_interface.get_publisher("PUB_1")
    header = Header(entity_path="/pytest/multi_pub_sub_1", reference_id=1)

    message_count = 0
    while True:
        header.timestamp.GetCurrentTime()
        message = PlainText(header=header, body=f"Hello from Publisher 1! Message #{message_count} 🚀")
        message_encoded = message_encoder.encode(message)
        publisher.put(payload=message_encoded)

        print(f"[Publisher 1] Published: {message.body}")
        message_count += 1
        time.sleep(2)  # Publish every 2 seconds


if __name__ == "__main__":
    main()
