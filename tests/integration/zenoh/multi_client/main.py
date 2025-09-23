import time
from datetime import datetime, timezone

from make87_messages.core.header_pb2 import Header
from make87_messages.text.text_plain_pb2 import PlainText
from make87.encodings import ProtobufEncoder
from make87.interfaces.zenoh import ZenohInterface


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_interface = ZenohInterface(name="zenoh_test")

    # Get multiple queriers using multi-client functionality
    queriers = zenoh_interface.get_multi_client("MULTI_API_CLIENT")
    print(f"Created {len(queriers)} queriers for multi-client 'MULTI_API_CLIENT'")

    query_count = 0
    total_responses = 0

    try:
        while query_count < 10:  # Send 10 queries per querier
            for i, querier in enumerate(queriers, 1):
                query_count += 1

                # Create query message
                header = Header(entity_path=f"/test/client_{i}", reference_id=query_count)
                header.timestamp.GetCurrentTime()
                message = PlainText(header=header, body=f"Query {query_count} from Client {i}")
                message_encoded = message_encoder.encode(message)

                print(f"Client {i} sending query {query_count}: {message.body}")

                # Send query
                response = querier.get(payload=message_encoded)

                # Process responses
                for r in response:
                    if r.ok is not None:
                        try:
                            response_message = message_encoder.decode(r.ok.payload.to_bytes())
                            received_dt = datetime.now(tz=timezone.utc)
                            sent_dt = response_message.header.timestamp.ToDatetime().replace(tzinfo=timezone.utc)
                            total_responses += 1
                            print(
                                f"Client {i} received response: '{response_message.body}' from {response_message.header.entity_path}. "
                                f"Response sent at {sent_dt}. Received at {received_dt}. "
                                f"Took {(received_dt - sent_dt).total_seconds():.3f} seconds."
                            )
                        except Exception as e:
                            print(f"Client {i} error processing response: {e}")
                    else:
                        print(f"Client {i} received non-OK response")

                time.sleep(0.5)  # Brief pause between queries

    except KeyboardInterrupt:
        print("Multi-client stopped by user")
    finally:
        print(f"Multi-client summary: Sent {query_count} queries, received {total_responses} responses")
        # Clean up queriers
        for querier in queriers:
            try:
                querier.undeclare()
            except Exception as e:
                print(f"Error undeclaring querier: {e}")


if __name__ == "__main__":
    main()
