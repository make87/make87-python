from datetime import datetime, timezone

from make87_messages.text.text_plain_pb2 import PlainText

from make87.encodings import ProtobufEncoder
from make87.interfaces.zenoh import ZenohInterface


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_interface = ZenohInterface()
    subscriber = zenoh_interface.get_subscriber("HELLO_WORLD_MESSAGE")

    for sample in subscriber:
        message = message_encoder.decode(sample.payload.to_bytes())
        received_dt = datetime.now(tz=timezone.utc)
        publish_dt = message.header.timestamp.ToDatetime().replace(tzinfo=timezone.utc)
        print(
            f"Received message '{message.body}'. Sent at {publish_dt}. Received at {received_dt}. Took {(received_dt - publish_dt).total_seconds()} seconds."
        )


if __name__ == "__main__":
    main()
