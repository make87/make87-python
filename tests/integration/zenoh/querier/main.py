import time

from make87_messages.core.header_pb2 import Header
from make87_messages.text.text_plain_pb2 import PlainText
from make87.encodings import ProtobufEncoder
from make87.interfaces.zenoh import ZenohInterface


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_interface = ZenohInterface(name="zenoh_test")

    querier = zenoh_interface.get_querier("HELLO_WORLD_MESSAGE")
    header = Header(entity_path="/pytest/req_prv", reference_id=0)

    while True:
        header.timestamp.GetCurrentTime()
        message = PlainText(header=header, body="Hello, World! 🐍")
        message_encoded = message_encoder.encode(message)
        response = querier.get(payload=message_encoded)
        for r in response:
            if r.ok is not None:
                response_message = message_encoder.decode(r.ok.payload.to_bytes())
                print(f"Received response: {response_message.body}")
        time.sleep(0.1)


if __name__ == "__main__":
    main()
