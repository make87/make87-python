from datetime import datetime, timezone

from make87_messages.text.text_plain_pb2 import PlainText
from make87_messages.core.header_pb2 import Header
from zenoh.zenoh import Query

from make87.encodings import ProtobufEncoder
from make87.interfaces.zenoh import ZenohAdapter, ZenohInterface


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_adapter = ZenohAdapter()
    zenoh_interface = ZenohInterface()

    provider = zenoh_interface.get_provider("EXAMPLE_ENDPOINT")

    while True:
        with provider.recv() as query:
            query: Query = query
            message_unpacked, key_expr, *_ = zenoh_adapter.unpack(query)
            message = message_encoder.decode(message_unpacked)
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
            message_packed = zenoh_adapter.pack(message_encoded)

            query.reply(key_expr=key_expr, payload=message_packed)


if __name__ == "__main__":
    main()
