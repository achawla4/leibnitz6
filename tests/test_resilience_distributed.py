# -*- coding: utf-8 -*-
"""
Verification Test Suite for 2026 Distributed Systems Resilience & Composability Engine:
Circuit Breaker state transitions, EventBus asynchronous publishing, and Service Mesh eBPF tracing headers.
"""

import pytest
import time
from leibnitz6_server.server import app
from leibnitz6_server.resilience import CircuitBreaker, CircuitBreakerOpenException, DistributedEventBus, STATE_CLOSED, STATE_OPEN, STATE_HALF_OPEN

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_circuit_breaker_transitions():
    """Verify Circuit Breaker failure threshold and recovery timeout (Resilience4j paradigm)."""
    cb = CircuitBreaker(name="TestBreaker", failure_threshold=2, recovery_timeout_sec=0.2)
    assert cb.state == STATE_CLOSED

    def failing_func():
        raise ValueError("Simulated downstream microservice error")

    # First failure
    with pytest.raises(ValueError):
        cb.call(failing_func)
    assert cb.state == STATE_CLOSED

    # Second failure triggers OPEN state
    with pytest.raises(ValueError):
        cb.call(failing_func)
    assert cb.state == STATE_OPEN

    # Requests while OPEN fail immediately with CircuitBreakerOpenException
    with pytest.raises(CircuitBreakerOpenException):
        cb.call(lambda: "success")

    # Wait for recovery timeout to transition to HALF_OPEN
    time.sleep(0.25)
    
    # Successful call in HALF_OPEN restores CLOSED state
    res = cb.call(lambda: "recovered")
    assert res == "recovered"
    assert cb.state == STATE_CLOSED

def test_distributed_event_bus():
    """Verify asynchronous EventBus publishing and subscription (Kafka / AWS EventBridge paradigm)."""
    bus = DistributedEventBus()
    received_events = []

    def event_listener(event):
        received_events.append(event)

    bus.subscribe("suganita.executed", event_listener)
    bus.publish("suganita.executed", {"script": "test.su", "status": "SUCCESS"})

    assert len(received_events) == 1
    assert received_events[0]['event_type'] == 'suganita.executed'
    assert len(bus.get_event_history()) >= 1

def test_resilience_status_endpoint(client):
    """Verify /api/resilience/status endpoint returns Circuit Breaker & Service Mesh metadata."""
    resp = client.get('/api/resilience/status')
    assert resp.status_code == 200
    data = resp.json
    assert data['status'] == 'SUCCESS'
    assert 'circuit_breaker' in data
    assert data['service_mesh'] == 'Istio_eBPF_Accelerated'

def test_service_mesh_ebpf_headers(client):
    """Verify response contains Istio / Linkerd eBPF distributed tracing headers."""
    resp = client.get('/health')
    assert resp.status_code == 200
    assert 'x-request-id' in resp.headers
    assert 'x-service-mesh' in resp.headers
    assert 'x-circuit-breaker-state' in resp.headers
