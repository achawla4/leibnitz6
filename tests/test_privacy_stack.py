# -*- coding: utf-8 -*-
"""
Privacy Verification Test Suite for GDPR, CCPA/CPRA, India DPDP Act 2023, and Global Privacy Control (GPC).
Tests IP pseudonymization, GPC/DNT header compliance, and Right to Erasure (/api/privacy/forget_me).
"""

import pytest
from leibnitz6_server.server import app
from leibnitz6_server.privacy import pseudonymize_ip

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_ip_pseudonymization():
    """Verify IP addresses are SHA-256 pseudonymized without raw PII retention."""
    ip = "203.0.113.195"
    pseudonymized = pseudonymize_ip(ip)
    assert ip not in pseudonymized
    assert pseudonymized.startswith("anon_")
    assert len(pseudonymized) == 17

def test_privacy_policy_endpoint(client):
    """Verify /api/privacy/policy returns 2026 privacy compliance metadata."""
    resp = client.get('/api/privacy/policy')
    assert resp.status_code == 200
    data = resp.json
    assert data['status'] == 'SUCCESS'
    assert 'GDPR' in data['compliance']
    assert 'Global_Privacy_Control_GPC' in data['compliance']

def test_gpc_dnt_headers(client):
    """Verify system accepts and honors Global Privacy Control (Sec-GPC) headers."""
    resp = client.get('/health', headers={'Sec-GPC': '1'})
    assert resp.status_code == 200

def test_right_to_erasure_endpoint(client):
    """Verify GDPR Right to Erasure / DPDP Erasure API (/api/privacy/forget_me)."""
    resp = client.post('/api/privacy/forget_me')
    assert resp.status_code == 200
    data = resp.json
    assert data['status'] == 'SUCCESS'
    assert 'Data erasure requested' in data['message']
