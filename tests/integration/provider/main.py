from datetime import datetime, timezone

from make87_messages.core.header_pb2 import Header
from make87_messages.text.text_plain_pb2 import PlainText
import make87


def main():
    make87.initialize()
    endpoint = make87.get_provider(
        name="EXAMPLE_ENDPOINT", requester_message_type=PlainText, provider_message_type=PlainText
    )

    def callback(message: PlainText) -> PlainText:
        received_dt = datetime.now(tz=timezone.utc)
        publish_dt = message.header.timestamp.ToDatetime().replace(tzinfo=timezone.utc)
        print(
            f"Received message '{message.body}'. Sent at {publish_dt}. Received at {received_dt}. Took {(received_dt - publish_dt).total_seconds()} seconds."
        )

        return PlainText(
            header=make87.header_from_message(Header, message=message, append_entity_path="response"),
            body=message.body[::-1],
        )

    endpoint.provide(callback)
    make87.loop()


if __name__ == "__main__":
    main()
