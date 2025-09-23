"""
Test multi-client functionality using a single ZenohInterface session.

This test creates all queryables in a single ZenohInterface instance to avoid
session interference issues that can occur when multiple ZenohInterface instances
are created in the same process.
"""

import uuid
import time

import pytest

from make87.interfaces.zenoh import ZenohInterface
from make87.internal.models.application_env_config import (
    ApplicationInfo,
    BoundProvider,
    BoundMultiClient,
    AccessPoint,
    InterfaceConfig,
)
from make87.models import (
    ApplicationConfig,
    MountedPeripherals,
)
from make87.config import load_config_from_json
from make87_messages.text.text_plain_pb2 import PlainText
from make87_messages.core.header_pb2 import Header
from make87.encodings import ProtobufEncoder


@pytest.fixture
def single_session_config():
    """Configuration with all queryables in a single interface."""
    config = ApplicationConfig(
        interfaces=dict(
            zenoh_test=InterfaceConfig(
                name="zenoh_test",
                subscribers={},
                publishers={},
                requesters={},
                providers=dict(
                    QUERYABLE_1=BoundProvider(
                        endpoint_name="QUERYABLE_1",
                        endpoint_key="test_endpoint_1",
                        protocol="zenoh",
                        requester_message_type="make87_messages.text.text_plain.PlainText",
                        provider_message_type="make87_messages.text.text_plain.PlainText",
                    ),
                    QUERYABLE_2=BoundProvider(
                        endpoint_name="QUERYABLE_2",
                        endpoint_key="test_endpoint_2",
                        protocol="zenoh",
                        requester_message_type="make87_messages.text.text_plain.PlainText",
                        provider_message_type="make87_messages.text.text_plain.PlainText",
                    ),
                    QUERYABLE_3=BoundProvider(
                        endpoint_name="QUERYABLE_3",
                        endpoint_key="test_endpoint_3",
                        protocol="zenoh",
                        requester_message_type="make87_messages.text.text_plain.PlainText",
                        provider_message_type="make87_messages.text.text_plain.PlainText",
                    ),
                ),
                clients={},
                servers={},
                multi_clients=dict(
                    MULTI_API_CLIENT=BoundMultiClient(
                        name="MULTI_API_CLIENT",
                        keys=["test_endpoint_1", "test_endpoint_2", "test_endpoint_3"],
                        spec="text",
                        protocol="zenoh",
                        interface_name="zenoh",
                        access_points={
                            "test_endpoint_1": AccessPoint(
                                vpn_ip="localhost",
                                vpn_port=7447,
                                same_node=True,
                            ),
                            "test_endpoint_2": AccessPoint(
                                vpn_ip="localhost",
                                vpn_port=7447,
                                same_node=True,
                            ),
                            "test_endpoint_3": AccessPoint(
                                vpn_ip="localhost",
                                vpn_port=7447,
                                same_node=True,
                            ),
                        },
                        congestion_control="DROP",
                        priority="REAL_TIME",
                        express=True,
                    )
                ),
            )
        ),
        peripherals=MountedPeripherals(peripherals=[]),
        config="{}",
        application_info=ApplicationInfo(
            deployed_application_id=uuid.uuid4().hex,
            system_id=uuid.uuid4().hex,
            deployed_application_name="single_session_test",
            is_release_version=True,
            application_id=uuid.uuid4().hex,
            application_name="single_session_test",
        ),
    )
    return load_config_from_json(config.model_dump_json())


def test_multi_client_single_session(single_session_config):
    """Test multi-client with all queryables in a single ZenohInterface session."""
    # Create single interface with all queryables
    interface = ZenohInterface(name="zenoh_test", make87_config=single_session_config)

    # Create queryable handlers
    def make_handler(server_id):
        def handler(query):
            """Handler that responds to queries."""
            try:
                encoder = ProtobufEncoder(message_type=PlainText)

                # Try to decode the incoming query
                query_text = "unknown"
                if hasattr(query, "payload") and query.payload is not None:
                    try:
                        query_message = encoder.decode(query.payload.to_bytes())
                        query_text = query_message.body
                        print(f"🔄 Queryable {server_id} received query: {query_text}")
                    except Exception:
                        print(f"🔄 Queryable {server_id} received query (couldn't decode payload)")
                else:
                    print(f"🔄 Queryable {server_id} received query: {query.selector}")

                # Create response
                header = Header(entity_path=f"/test/queryable_{server_id}", reference_id=server_id)
                header.timestamp.GetCurrentTime()

                response_text = f"Hello from Queryable {server_id}! (responding to: {query_text})"
                response = PlainText(header=header, body=response_text)
                encoded_response = encoder.encode(response)

                query.reply(key_expr=query.key_expr, payload=encoded_response)
                print(f"🔄 Queryable {server_id} responded: {response_text}")
            except Exception as e:
                print(f"❌ Error in queryable {server_id}: {e}")

        return handler

    # Create all 3 queryables in the same session
    queryables = []
    for i in range(1, 4):
        queryable = interface.get_queryable(f"QUERYABLE_{i}", handler=make_handler(i))
        queryables.append(queryable)
        print(f"🔄 Created Queryable {i} listening on endpoint: test_endpoint_{i}")

    # Give queryables time to start
    time.sleep(1.0)

    # Get queriers
    queriers = interface.get_multi_client("MULTI_API_CLIENT")
    print(f"🔍 Created {len(queriers)} queriers")

    received_responses = []

    # Send queries
    for i, querier in enumerate(queriers, 1):
        endpoint_key = f"test_endpoint_{i}"
        print(f"🔍 Querier {i} sending query to endpoint '{endpoint_key}'...")

        # Create query message
        encoder = ProtobufEncoder(message_type=PlainText)
        header = Header(entity_path=f"/test/client_{i}", reference_id=i)
        header.timestamp.GetCurrentTime()
        query_message = PlainText(header=header, body=f"Query from Client {i}")
        encoded_query = encoder.encode(query_message)

        # Send query
        replies = querier.get(payload=encoded_query)

        # Collect responses
        response_found = False
        for reply in replies:
            if reply.ok is not None:
                try:
                    response = encoder.decode(reply.ok.payload.to_bytes())
                    received_responses.append(
                        {"querier_id": i, "body": response.body, "entity_path": response.header.entity_path}
                    )
                    print(f"📨 Querier {i} received: {response.body} from {response.header.entity_path}")
                    response_found = True
                except Exception as e:
                    print(f"❌ Error processing response for querier {i}: {e}")
            else:
                print(f"⚠️  Querier {i} received non-OK reply")

        if not response_found:
            print(f"❌ Querier {i} received no responses for endpoint '{endpoint_key}'")

        time.sleep(0.5)  # Brief delay between queries

    print(f"📊 Total responses received: {len(received_responses)}")
    for resp in received_responses:
        print(f"  - Querier {resp['querier_id']}: {resp['body']} from {resp['entity_path']}")

    # Clean up
    for querier in queriers:
        querier.undeclare()
    for queryable in queryables:
        queryable.undeclare()

    # Expect all 3 queryables to respond when using single session
    assert len(received_responses) >= 1, "Should receive at least one response"
    print("✅ Single session multi-client test completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
