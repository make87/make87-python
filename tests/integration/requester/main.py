import time
from datetime import timezone

from make87_messages.core.header_pb2 import Header
from make87_messages.text.text_plain_pb2 import PlainText
import make87


def main():
    make87.initialize()
    endpoint = make87.get_requester(
        name="EXAMPLE_ENDPOINT", requester_message_type=PlainText, provider_message_type=PlainText
    )

    while True:
        message = PlainText(header=make87.create_header(Header), body="Hello, World! 🐍")
        try:
            response = endpoint.request(message, timeout=10.0)
            print(
                f"Received response: {response.body}. Round trip took"
                f" {response.header.timestamp.ToDatetime().replace(tzinfo=timezone.utc) - message.header.timestamp.ToDatetime().replace(tzinfo=timezone.utc)} seconds."
            )
        except make87.ProviderNotAvailable:
            print("Endpoint not available. Retrying in 1 second.")
        finally:
            time.sleep(1)


if __name__ == "__main__":
    main()
