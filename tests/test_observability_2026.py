# -*- coding: utf-8 -*-
"""
Verification Test Suite for 2026 Unified Observability & OpenTelemetry Stack:
OpenTelemetry W3C tracecontext headers, Grafana Loki structured log stream,
Tempo / Jaeger OTLP spans, Datadog APM headers, and Observability as Code manifests.
"""

import os
import pytest
from leibnitz6_server.server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_opentelemetry_w3c_traceparent_injection(client):
    """Verify OpenTelemetry W3C traceparent and Datadog trace ID header injection."""
    resp = client.get('/health')
    assert resp.status_code == 200
    assert 'traceparent' in resp.headers
    assert resp.headers['traceparent'].startswith('00-')
    assert 'x-datadog-trace-id' in resp.headers

def test_otel_traces_endpoint(client):
    """Verify OpenTelemetry / Tempo / Jaeger trace span retrieval endpoint (/api/observability/traces)."""
    # Trigger request to generate span
    client.get('/health')

    resp = client.get('/api/observability/traces')
    assert resp.status_code == 200
    data = resp.json
    assert data['status'] == 'SUCCESS'
    assert data['telemetry_standard'] == 'OpenTelemetry_v1.28_OTLP'
    assert len(data['traces']) > 0

def test_grafana_loki_logs_endpoint(client):
    """Verify Grafana Loki log stream endpoint (/api/observability/loki)."""
    resp = client.get('/api/observability/loki')
    assert resp.status_code == 200
    data = resp.json
    assert data['status'] == 'SUCCESS'
    assert data['log_engine'] == 'Grafana_Loki_v2026'
    assert len(data['streams']) > 0

def test_datadog_apm_endpoint(client):
    """Verify Datadog APM & AI-to-AI monitoring endpoint (/api/observability/datadog)."""
    resp = client.get('/api/observability/datadog')
    assert resp.status_code == 200
    data = resp.json
    assert data['status'] == 'SUCCESS'
    assert 'ai_monitoring' in data

def test_observability_as_code_manifests_exist():
    """Verify Grafana Dashboard JSON and OpenTelemetry Collector Config exist."""
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    assert os.path.exists(os.path.join(base_dir, 'grafana', 'dashboard.json'))
    assert os.path.exists(os.path.join(base_dir, 'otel-collector-config.yaml'))
