import pytest
from make87.utils import (
    parse_topics,
    parse_endpoints,
    Topics,
    Endpoints,
    CongestionControl,
    Priority,
    Reliability,
    FifoChannel,
    RingChannel,
)


class TestPublisherTopics:
    def test_parse_topics_valid_json(self, monkeypatch):
        valid_json = '{"topics": [{"topic_name": "test_topic", "topic_key": "test_key", "message_type": "test_type", "topic_type": "PUB"}]}'
        monkeypatch.setenv("TOPICS", valid_json)
        topics = parse_topics()
        assert isinstance(topics, Topics)
        assert len(topics.topics) == 1
        assert topics.topics[0].topic_name == "test_topic"

    def test_parse_topics_invalid_json(self, monkeypatch):
        invalid_json = '{"topics": [invalid_json]}'
        monkeypatch.setenv("TOPICS", invalid_json)
        with pytest.raises(ValueError):
            parse_topics()

    def test_parse_topics_missing_env(self, monkeypatch):
        monkeypatch.delenv("TOPICS", raising=False)
        topics = parse_topics()
        assert isinstance(topics, Topics)
        assert len(topics.topics) == 0

    def test_parse_endpoints_valid_json(self, monkeypatch):
        valid_json = '{"endpoints": [{"endpoint_name": "test_endpoint", "endpoint_key": "test_key", "requester_message_type": "test_type", "provider_message_type": "test_type", "endpoint_type": "REQ"}]}'
        monkeypatch.setenv("ENDPOINTS", valid_json)
        endpoints = parse_endpoints()
        assert isinstance(endpoints, Endpoints)
        assert len(endpoints.endpoints) == 1
        assert endpoints.endpoints[0].endpoint_name == "test_endpoint"

    def test_parse_endpoints_invalid_json(self, monkeypatch):
        invalid_json = '{"endpoints": [invalid_json]}'
        monkeypatch.setenv("ENDPOINTS", invalid_json)
        with pytest.raises(ValueError):
            parse_endpoints()

    def test_parse_endpoints_missing_env(self, monkeypatch):
        monkeypatch.delenv("ENDPOINTS", raising=False)
        endpoints = parse_endpoints()
        assert isinstance(endpoints, Endpoints)
        assert len(endpoints.endpoints) == 0

    def test_parse_topics_with_congestion_control(self, monkeypatch):
        valid_json = '{"topics": [{"topic_name": "test_topic", "topic_key": "test_key", "message_type": "test_type", "topic_type": "PUB", "congestion_control": 0}]}'
        monkeypatch.setenv("TOPICS", valid_json)
        topics = parse_topics()
        assert isinstance(topics, Topics)
        assert len(topics.topics) == 1
        assert topics.topics[0].congestion_control == CongestionControl.DROP

    def test_parse_topics_with_express(self, monkeypatch):
        valid_json = '{"topics": [{"topic_name": "test_topic", "topic_key": "test_key", "message_type": "test_type", "topic_type": "PUB", "express": false}]}'
        monkeypatch.setenv("TOPICS", valid_json)
        topics = parse_topics()
        assert isinstance(topics, Topics)
        assert len(topics.topics) == 1
        assert topics.topics[0].express is False

    def test_parse_topics_with_priority(self, monkeypatch):
        valid_json = '{"topics": [{"topic_name": "test_topic", "topic_key": "test_key", "message_type": "test_type", "topic_type": "PUB", "priority": 1}]}'
        monkeypatch.setenv("TOPICS", valid_json)
        topics = parse_topics()
        assert isinstance(topics, Topics)
        assert len(topics.topics) == 1
        assert topics.topics[0].priority == Priority.REAL_TIME

    def test_parse_topics_with_reliability(self, monkeypatch):
        valid_json = '{"topics": [{"topic_name": "test_topic", "topic_key": "test_key", "message_type": "test_type", "topic_type": "PUB", "reliability": 1}]}'
        monkeypatch.setenv("TOPICS", valid_json)
        topics = parse_topics()
        assert isinstance(topics, Topics)
        assert len(topics.topics) == 1
        assert topics.topics[0].reliability == Reliability.RELIABLE


class TestSubscriberTopics:
    def test_parse_topics_with_sub_fifo(self, monkeypatch):
        valid_json = '{"topics": [{"topic_name": "test_topic", "topic_key": "test_key", "message_type": "test_type", "topic_type": "SUB", "handler": {"handler_type": "FIFO", "capacity": 10}}]}'
        monkeypatch.setenv("TOPICS", valid_json)
        topics = parse_topics()
        assert isinstance(topics, Topics)
        assert len(topics.topics) == 1
        assert topics.topics[0].handler.capacity == 10
        assert isinstance(topics.topics[0].handler, FifoChannel)

    def test_parse_topics_with_sub_ring(self, monkeypatch):
        valid_json = '{"topics": [{"topic_name": "test_topic", "topic_key": "test_key", "message_type": "test_type", "topic_type": "SUB", "handler": {"handler_type": "RING", "capacity": 20}}]}'
        monkeypatch.setenv("TOPICS", valid_json)
        topics = parse_topics()
        assert isinstance(topics, Topics)
        assert len(topics.topics) == 1
        assert topics.topics[0].handler.capacity == 20
        assert isinstance(topics.topics[0].handler, RingChannel)
