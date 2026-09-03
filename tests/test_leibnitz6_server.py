# -*- coding: utf-8 -*-
"""
Tests for Leibnitz6 Server & Sahai Anytime Coding (Phase 2 Validation)
"""

import os
import sys
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from leibnitz6_server import TransmitProtocolHandler, AnytimeEncoder, AnytimeDecoder, app

def test_protocol_header_parsing():
    handler = TransmitProtocolHandler()
    header_text = """
    SUGANITA_TRANSMIT_HEADER v1.0
    FILE: signal1.su
    CLIENT: StructuredNotepad_v3
    """
    meta = handler.parse_header(header_text)
    assert meta['version'] in ('v1.0', '1.0')
    assert meta['filename'] == 'signal1.su'
    assert meta['client'] == 'StructuredNotepad_v3'

def test_transmission_processing(tmp_path):
    handler = TransmitProtocolHandler(processed_dir=str(tmp_path))
    header = "SUGANITA_TRANSMIT_HEADER v1.0\nFILE: signal1.su"
    code = """
    लिखो "Testing Transmission"
    प्रवेश "Signal_Payload"
    रूपरेखा "Spectral_Graph"
    """
    res = handler.process_transmission(header, code)
    assert res['status'] == 'SUCCESS'
    assert res['output_filename'] == 'signal1out.su'
    assert os.path.exists(res['output_path'])

def test_sahai_anytime_coding_signal():
    encoder = AnytimeEncoder()
    decoder = AnytimeDecoder(total_samples=500)
    
    t = np.linspace(0, 1, 500)
    orig_sig = np.sin(2 * np.pi * 10 * t).astype(np.float32)
    
    frames = encoder.encode_signal_buffer(orig_sig)
    assert len(frames) == 3
    
    # Test progressive refinement decoding
    # Layer 0 (Coarse Base)
    sig0 = decoder.ingest_frame(frames[0])
    status0 = decoder.get_refinement_status()
    assert status0['highest_level_received'] == 0
    assert status0['fidelity_pct'] == 33.33
    
    # Layer 1 (Medium)
    sig1 = decoder.ingest_frame(frames[1])
    status1 = decoder.get_refinement_status()
    assert status1['highest_level_received'] == 1
    
    # Layer 2 (Full Precision)
    sig2 = decoder.ingest_frame(frames[2])
    status2 = decoder.get_refinement_status()
    assert status2['highest_level_received'] == 2
    assert np.allclose(orig_sig, sig2, atol=1e-3)

def test_flask_server_endpoints():
    client = app.test_client()
    
    # Test /health
    res = client.get('/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'ONLINE'
    
    # Test /api/transmit
    code = "लिखो HelloServer\nप्रवेश Data1\n"
    res = client.post('/api/transmit', json={'header': 'FILE: signal1.su', 'source_code': code})
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'SUCCESS'

def test_remote_installer_endpoint():
    test_client = app.test_client()
    res = test_client.get('/install.py')
    assert res.status_code == 200
    assert "LEIBNITZ" in res.get_data(as_text=True)

def test_telemetry_metrics_monitoring():
    test_client = app.test_client()
    
    # Trigger a transmit call to log telemetry
    code = "लिखो TelemetryTest\nप्रवेश Data1\n"
    test_client.post('/api/transmit', json={'header': 'FILE: telemetry.su', 'source_code': code}, headers={'X-Client-ID': 'Test_Unit_Client'})
    
    # Query /api/metrics JSON endpoint
    res = test_client.get('/api/metrics')
    assert res.status_code == 200
    metrics = res.get_json()
    assert metrics['status'] == 'SUCCESS'
    assert metrics['total_requests'] >= 1
    assert 'Test_Unit_Client' in metrics['clients']

    # Query /admin/dashboard HTML endpoint
    dash_res = test_client.get('/admin/dashboard')
    assert dash_res.status_code == 200
    assert "Leibnitz 6 Network Server Telemetry" in dash_res.get_data(as_text=True)

def test_seychelles_geoblock():
    test_client = app.test_client()
    res = test_client.get('/health', headers={'CF-IPCountry': 'SC'})
    assert res.status_code == 403
    data = res.get_json()
    assert data['status'] == 'SEC_GEOBLOCK_ENFORCED'
    assert 'Seychelles' in data['error']

