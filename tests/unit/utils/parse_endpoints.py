import pytest
from make87.utils import parse_endpoints, Endpoints, CongestionControl, Priority


def test_parse_endpoints_valid_json(monkeypatch):
    valid_json = '{"endpoints": [{"endpoint_name": "test_endpoint", "endpoint_key": "test_key", "requester_message_type": "test_type", "provider_message_type": "test_type", "endpoint_type": "REQ"}]}'
    monkeypatch.setenv("ENDPOINTS", valid_json)
    endpoints = parse_endpoints()
    assert isinstance(endpoints, Endpoints)
    assert len(endpoints.endpoints) == 1
    assert endpoints.endpoints[0].endpoint_name == "test_endpoint"


def test_parse_endpoints_invalid_json(monkeypatch):
    invalid_json = '{"endpoints": [invalid_json]}'
    monkeypatch.setenv("ENDPOINTS", invalid_json)
    with pytest.raises(ValueError):
        parse_endpoints()


def test_parse_endpoints_missing_env(monkeypatch):
    monkeypatch.delenv("ENDPOINTS", raising=False)
    endpoints = parse_endpoints()
    assert isinstance(endpoints, Endpoints)
    assert len(endpoints.endpoints) == 0


def test_parse_endpoints_with_congestion_control(monkeypatch):
    valid_json = '{"endpoints": [{"endpoint_name": "test_endpoint", "endpoint_key": "test_key", "requester_message_type": "test_type", "provider_message_type": "test_type", "endpoint_type": "REQ", "congestion_control": "DROP"}]}'
    monkeypatch.setenv("ENDPOINTS", valid_json)
    endpoints = parse_endpoints()
    assert isinstance(endpoints, Endpoints)
    assert len(endpoints.endpoints) == 1
    assert endpoints.endpoints[0].congestion_control == CongestionControl.DROP


def test_parse_endpoints_with_priority(monkeypatch):
    valid_json = '{"endpoints": [{"endpoint_name": "test_endpoint", "endpoint_key": "test_key", "requester_message_type": "test_type", "provider_message_type": "test_type", "endpoint_type": "REQ", "priority": "REAL_TIME"}]}'
    monkeypatch.setenv("ENDPOINTS", valid_json)
    endpoints = parse_endpoints()
    assert isinstance(endpoints, Endpoints)
    assert len(endpoints.endpoints) == 1
    assert endpoints.endpoints[0].priority == Priority.REAL_TIME


def test_parse_endpoints_with_express(monkeypatch):
    valid_json = '{"endpoints": [{"endpoint_name": "test_endpoint", "endpoint_key": "test_key", "requester_message_type": "test_type", "provider_message_type": "test_type", "endpoint_type": "REQ", "express": false}]}'
    monkeypatch.setenv("ENDPOINTS", valid_json)
    endpoints = parse_endpoints()
    assert isinstance(endpoints, Endpoints)
    assert len(endpoints.endpoints) == 1
    assert endpoints.endpoints[0].express is False
