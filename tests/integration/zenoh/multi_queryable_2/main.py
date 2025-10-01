from datetime import datetime, timezone

from make87_messages.text.text_plain_pb2 import PlainText
from make87_messages.core.header_pb2 import Header

from make87.encodings import ProtobufEncoder
from make87.interfaces.zenoh import ZenohInterface


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_interface = ZenohInterface(name="zenoh_test")

    queryable = zenoh_interface.get_queryable("QUERYABLE_2")
    print("Queryable 2 started listening...")

    while True:
        with queryable.recv() as query:
            try:
                message = message_encoder.decode(query.payload.to_bytes())
                received_dt = datetime.now(tz=timezone.utc)
                publish_dt = message.header.timestamp.ToDatetime().replace(tzinfo=timezone.utc)
                print(
                    f"Queryable 2 received query '{message.body}' from {message.header.entity_path}. "
                    f"Sent at {publish_dt}. Received at {received_dt}. "
                    f"Took {(received_dt - publish_dt).total_seconds():.3f} seconds."
                )

                # Create response
                header = Header(entity_path="/test/queryable_2", reference_id=2)
                header.timestamp.GetCurrentTime()

                response_message = PlainText(
                    header=header,
                    body=f"Response from Queryable 2 to: {message.body}",
                )
                message_encoded = message_encoder.encode(response_message)

                query.reply(key_expr=query.key_expr, payload=message_encoded)
                print(f"Queryable 2 responded to query: {message.body}")
            except Exception as e:
                print(f"Queryable 2 error processing query: {e}")


if __name__ == "__main__":
    main()
