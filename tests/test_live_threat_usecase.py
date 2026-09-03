# -*- coding: utf-8 -*-
"""
Verification Test Suite for Live Threat Feed Ingestion & 2D Space-Time Use Case Validation.
Tests CTU-13, URLhaus, Certstream, CISA AIS feed preprocessors and /api/security/live_threat_test endpoint.
"""

import pytest
from leibnitz6_server.threat_feeds import fetch_and_preprocess_threat_feed, THREAT_SOURCES
from leibnitz6_server.server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_threat_feed_sources_registry():
    """Verify threat feed sources registry contains Stratosphere CTU-13, URLhaus, Certstream, and CISA AIS."""
    assert "stratosphere_ctu13" in THREAT_SOURCES
    assert "urlhaus_feed" in THREAT_SOURCES
    assert "certstream_live" in THREAT_SOURCES
    assert "cisa_ais_honeypot" in THREAT_SOURCES

def test_fetch_and_preprocess_threat_feed_c2_beaconing():
    """Verify preprocessor converts raw packet timing into a 2D matrix with labeled Fourier signatures."""
    res = fetch_and_preprocess_threat_feed(source_key="stratosphere_ctu13", threat_type="c2_beaconing")
    assert res['n_nodes'] == 10
    assert len(res['telemetry_matrix']) == 10
    assert len(res['fourier_signatures']) > 0
    assert any("C2 Heartbeat" in sig for sig in res['fourier_signatures'])

def test_fetch_and_preprocess_threat_feed_botnet_ddos():
    """Verify botnet DDoS threat type generates spatial Fourier synchronization signatures."""
    res = fetch_and_preprocess_threat_feed(source_key="certstream_live", threat_type="botnet_dDoS")
    assert len(res['fourier_signatures']) > 0
    assert any("Spatial Fourier Sync" in sig for sig in res['fourier_signatures'])

def test_live_threat_test_rest_api_endpoint(client):
    """Verify /api/security/live_threat_test returns 2D FFT heatmap image and identified Fourier signatures."""
    resp = client.post('/api/security/live_threat_test', json={
        'source': 'stratosphere_ctu13',
        'threat_type': 'c2_beaconing'
    })
    assert resp.status_code == 200
    data = resp.json
    assert data['server'] == 'Leibnitz7'
    assert 'hacker_footprint_anomaly_index' in data
    assert 'fourier_signatures' in data
    assert len(data['plot_b64']) > 50
