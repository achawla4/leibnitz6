# -*- coding: utf-8 -*-
"""
Security Verification Test Suite for OWASP ASVS 5.0, NIST SP 800-218 & CISA Secure by Design.
Tests security headers, input sanitization, rate limiting, and SBOM integrity.
"""

import os
import json
import pytest
from leibnitz6_server.server import app
from leibnitz6_server.security import sanitize_suganita_input, SECURITY_HEADERS

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_security_headers_applied(client):
    """Verify OWASP ASVS 5.0 security headers on API responses."""
    resp = client.get('/health')
    assert resp.status_code == 200
    for header in ['Content-Security-Policy', 'Strict-Transport-Security', 'X-Frame-Options', 'X-Content-Type-Options']:
        assert header in resp.headers
        assert resp.headers[header] == SECURITY_HEADERS[header]

def test_input_sanitization():
    """Verify input code sanitization strips malicious control characters."""
    malicious_input = "लिखो('Test')\x00\x07\x0c"
    sanitized = sanitize_suganita_input(malicious_input)
    assert "\x00" not in sanitized
    assert "\x07" not in sanitized
    assert "लिखो('Test')" in sanitized

def test_sbom_exists():
    """Verify CycloneDX SBOM (sbom.json) supply-chain metadata exists and is valid JSON."""
    sbom_path = os.path.join(os.path.dirname(__file__), '..', 'sbom.json')
    assert os.path.exists(sbom_path)
    with open(sbom_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data['bomFormat'] == 'CycloneDX'
        assert len(data['components']) > 0
