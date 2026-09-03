# -*- coding: utf-8 -*-
"""
Verification Test Suite for 2D Space-Time Fourier Analysis & Hacker Footprint Detection (sigsecurityv1.txt).
Tests column-wise (time) and row-wise (space) transforms, anomaly index calculation, API endpoints, Suganita DSL, and SDK integration.
"""

import pytest
import numpy as np
from suganita_engine.signal_adapter import SignalAdapter
from suganita_engine import compile_and_run
from leibnitz6_server.server import app
from leibnitz6_sdk import Leibnitz7Client

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_space_time_2d_fourier_analysis_calculation():
    """Verify 2D FFT Space-Time analysis detects injected hacker beaconing anomaly."""
    adapter = SignalAdapter()
    for i in range(1, 9):
        adapter.generate_synthetic_signal(f"rack_node_{i}", "sinusoidal", freq=10.0 + i*2)

    # Inject periodic hacker beaconing into node 4
    t = adapter.signals['rack_node_4']['t']
    adapter.signals['rack_node_4']['y'] += 3.0 * np.sin(2 * np.pi * 150.0 * t)

    res = adapter.process_space_time_security_analysis(dataset_name="multi_col_dataset")
    assert res['status'] == 'SUCCESS'
    assert res['n_nodes'] == 8
    assert res['hacker_footprint_anomaly_index'] > 2.0
    assert 'rack_node_4' in res['suspicious_nodes']
    assert len(res['plot_b64']) > 50

def test_space_time_security_api_endpoint(client):
    """Verify REST API endpoint /api/security/space_time_analysis returns Haryana DC security telemetry results."""
    resp = client.post('/api/security/space_time_analysis', json={
        'dataset_name': 'haryana_dc_cluster_alpha'
    })
    assert resp.status_code == 200
    data = resp.json
    assert data['status'] == 'SUCCESS'
    assert data['server'] == 'Leibnitz7'
    assert 'hacker_footprint_anomaly_index' in data
    assert 'threat_level' in data
    assert len(data['plot_b64']) > 50

def test_suganita_devanagari_space_time_dsl():
    """Verify Suganita Devanagari DSL keyword 'अंतरिक्षसमय' compiles and executes 2D Space-Time analysis."""
    suganita_code = """
    लिखो "Haryana Data Center Telemetry Defense"
    अंतरिक्षसमय "datacenter_cluster"
    निरोध
    """
    res, payload = compile_and_run(suganita_code)
    logs = res.get('logs', [])
    assert len(logs) > 0
    assert any('[ANTARIKSHASAMAYA]' in log for log in logs)

def test_sdk_space_time_security_method():
    """Verify Leibnitz7Client SDK method space_time_security_analysis works offline and online."""
    sdk_client = Leibnitz7Client(client_id="Haryana_DC_Security_Agent")
    res = sdk_client.space_time_security_analysis(dataset_name="haryana_dc_test")
    assert res['status'] in ('SUCCESS', 'OFFLINE_FALLBACK')
    assert 'hacker_footprint_anomaly_index' in res
