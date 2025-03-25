from datetime import datetime, timezone

from make87_messages.text.text_plain_pb2 import PlainText
import make87


def main():
    make87.initialize()
    topic = make87.get_subscriber(name="HELLO_WORLD_MESSAGE", message_type=PlainText)

    def callback(message: PlainText):
        received_dt = datetime.now(tz=timezone.utc)
        publish_dt = message.header.timestamp.ToDatetime().replace(tzinfo=timezone.utc)
        print(
            f"Received message '{message.body}'. Sent at {publish_dt}. Received at {received_dt}. Took {(received_dt - publish_dt).total_seconds()} seconds."
        )

    topic.subscribe(callback)
    make87.loop()


if __name__ == "__main__":
    main()
