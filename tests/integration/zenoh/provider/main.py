from datetime import datetime, timezone

from make87_messages.text.text_plain_pb2 import PlainText
from make87_messages.core.header_pb2 import Header

from make87.encodings import ProtobufEncoder
from make87.interfaces.zenoh import ZenohInterface


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_interface = ZenohInterface()

    provider = zenoh_interface.get_provider("EXAMPLE_ENDPOINT")

    while True:
        with provider.recv() as query:
            message = message_encoder.decode(query.payload.to_bytes())
            received_dt = datetime.now(tz=timezone.utc)
            publish_dt = message.header.timestamp.ToDatetime().replace(tzinfo=timezone.utc)
            print(
                f"Received message '{message.body}'. Sent at {publish_dt}. Received at {received_dt}. Took {(received_dt - publish_dt).total_seconds()} seconds."
            )

            header = Header()
            header.CopyFrom(message.header)
            header.timestamp.GetCurrentTime()

            response_message = PlainText(
                header=header,
                body=message.body[::-1],  # Reverse the message body for demonstration
            )
            message_encoded = message_encoder.encode(response_message)

            query.reply(key_expr=query.key_expr, payload=message_encoded)


if __name__ == "__main__":
    main()
