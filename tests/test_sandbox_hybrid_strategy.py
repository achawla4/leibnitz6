# -*- coding: utf-8 -*-
"""
Verification Test Suite for Telemetry Sandboxing & Hybrid Validation Strategy.
Tests air-gapped memory isolation, benchmark F1-Score calculation, threat hunting mode, and REST endpoints.
"""

import pytest
from leibnitz6_server.sandbox import TelemetrySandbox, HybridStrategyEngine
from leibnitz6_server.server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_telemetry_sandbox_payload_sanitization():
    """Verify TelemetrySandbox strips binary/text payloads and retains only numerical signal dimensions."""
    sandbox = TelemetrySandbox()
    raw_feed_items = [
        {'timestamp': 100.5, 'payload_length': 1420, 'raw_bytes': b'\xef\xbf\xbdMALWARE', 'src_ip': '192.168.1.100'},
        {'timestamp': 100.6, 'payload_length': 64, 'raw_bytes': b'\x00\x01SHELL', 'src_ip': '192.168.1.101'}
    ]
    sanitized = sandbox.sanitize_feed_payload(raw_feed_items)
    assert len(sanitized) == 2
    assert 'raw_bytes' not in sanitized[0]
    assert 'src_ip' not in sanitized[0]
    assert sanitized[0]['length'] == 1420.0

def test_hybrid_engine_benchmark_accuracy_metrics():
    """Verify HybridStrategyEngine computes Precision, Recall, and F1-Score against ground-truth labels."""
    engine = HybridStrategyEngine()
    detected = ['Rack_Node_03', 'Rack_Node_07']
    ground_truth = ['Rack_Node_03', 'Rack_Node_07']
    
    metrics = engine.evaluate_benchmark_accuracy(detected, ground_truth, total_nodes=10)
    assert metrics['precision'] == 100.0
    assert metrics['recall'] == 100.0
    assert metrics['f1_score'] == 100.0
    assert metrics['false_positive_rate'] == 0.0

def test_hybrid_threat_validation_api_benchmark_mode(client):
    """Verify /api/security/hybrid_threat_validation in benchmark mode returns F1-Score and sandbox status."""
    resp = client.post('/api/security/hybrid_threat_validation', json={
        'source': 'stratosphere_ctu13',
        'threat_type': 'c2_beaconing',
        'mode': 'benchmark'
    })
    assert resp.status_code == 200
    data = resp.json
    assert data['server'] == 'Leibnitz7'
    assert data['sandbox_status'] == 'AIR_GAPPED_MEM_ISOLATION_ACTIVE'
    assert 'benchmark_metrics' in data
    assert data['benchmark_metrics']['f1_score'] > 0.0

def test_hybrid_threat_validation_api_threat_hunting_mode(client):
    """Verify /api/security/hybrid_threat_validation in threat hunting mode runs unsupervised 2D FFT scan."""
    resp = client.post('/api/security/hybrid_threat_validation', json={
        'source': 'certstream_live',
        'threat_type': 'botnet_dDoS',
        'mode': 'threat_hunting'
    })
    assert resp.status_code == 200
    data = resp.json
    assert data['validation_mode'] == 'threat_hunting'
    assert 'threat_hunting_summary' in data
