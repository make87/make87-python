from datetime import datetime, timezone
import threading
import time

from make87_messages.text.text_plain_pb2 import PlainText

from make87.encodings import ProtobufEncoder
from make87.interfaces.zenoh import ZenohInterface


def handle_subscriber(subscriber, subscriber_id, message_encoder):
    """Handle messages for a single subscriber."""
    print(f"Subscriber {subscriber_id} started listening...")
    for sample in subscriber:
        try:
            message = message_encoder.decode(sample.payload.to_bytes())
            received_dt = datetime.now(tz=timezone.utc)
            publish_dt = message.header.timestamp.ToDatetime().replace(tzinfo=timezone.utc)
            print(
                f"[Subscriber {subscriber_id}] Received message '{message.body}' on key '{sample.key_expr}'. "
                f"Sent at {publish_dt}. Received at {received_dt}. "
                f"Took {(received_dt - publish_dt).total_seconds():.3f} seconds."
            )
        except Exception as e:
            print(f"[Subscriber {subscriber_id}] Error processing message: {e}")


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_interface = ZenohInterface(name="zenoh_test")

    # Get multiple subscribers using the multi_subscriber functionality
    subscribers = zenoh_interface.get_multi_subscriber("MULTI_HELLO_WORLD")

    print(f"Created {len(subscribers)} subscribers for multi-subscriber 'MULTI_HELLO_WORLD'")

    # Start a thread for each subscriber
    threads = []
    for i, subscriber in enumerate(subscribers):
        thread = threading.Thread(target=handle_subscriber, args=(subscriber, i + 1, message_encoder), daemon=True)
        thread.start()
        threads.append(thread)

    try:
        # Keep the main thread alive
        print("Multi-subscriber running. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down multi-subscriber...")
    finally:
        # Clean up subscribers
        for subscriber in subscribers:
            try:
                subscriber.undeclare()
            except Exception as e:
                print(f"Error undeclaring subscriber: {e}")


if __name__ == "__main__":
    main()
