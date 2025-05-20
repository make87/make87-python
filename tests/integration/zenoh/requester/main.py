from make87_messages.core.header_pb2 import Header
from make87_messages.text.text_plain_pb2 import PlainText
from make87.encodings import ProtobufEncoder
from make87.interfaces.zenoh import ZenohInterface, ZenohAdapter


def main():
    message_encoder = ProtobufEncoder(message_type=PlainText)
    zenoh_adapter = ZenohAdapter()
    zenoh_interface = ZenohInterface()

    requester = zenoh_interface.get_requester("EXAMPLE_ENDPOINT")
    header = Header(entity_path="/pytest/req_prv", reference_id=0)

    while True:
        header.timestamp.GetCurrentTime()
        message = PlainText(header=header, body="Hello, World! 🐍")
        message_encoded = message_encoder.encode(message)
        message_packed = zenoh_adapter.pack(message_encoded)
        response = requester.get(payload=message_packed)
        for r in response:
            if r.ok is not None:
                response_unpacked, *_ = zenoh_adapter.unpack(r.ok)
                response_message = message_encoder.decode(response_unpacked)
                print(f"Received response: {response_message}")
            else:
                print(f"Received error: {r.error.payload.to_string()}")


if __name__ == "__main__":
    main()
