# -*- coding: utf-8 -*-
"""
Verification Test Suite for 2026 WCAG 2.2 Level AA, European Accessibility Act (EAA),
ADA Compliance, ARIA 1.3 Landmarks, and WebAuthn Passkeys Endpoint.
"""

import os
import pytest
from leibnitz6_server.server import app
from leibnitz6_server.accessibility import run_wcag_22_audit

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_accessibility_audit_endpoint(client):
    """Verify AI Accessibility Auditor API endpoint (/api/accessibility/audit)."""
    resp = client.get('/api/accessibility/audit')
    assert resp.status_code == 200
    data = resp.json
    assert data['standard'] == 'WCAG_2.2_Level_AA'
    assert 'European_Accessibility_Act_EAA' in data['regulations_compliance']
    assert data['compliance_score_percent'] == 100.0

def test_webauthn_passkeys_endpoint(client):
    """Verify Accessible WebAuthn Passkeys Registration endpoint (/api/accessibility/passkeys/register)."""
    resp = client.post('/api/accessibility/passkeys/register')
    assert resp.status_code == 200
    data = resp.json
    assert data['status'] == 'SUCCESS'
    assert data['standard'] == 'WebAuthn_FIDO2_Passkeys'
    assert data['cognitive_accessibility'] == 'Cognitive_Penalty_Free_Authentication'

def test_netlify_html_wcag_compliance():
    """Audit NetlifySitev3/leibnitz6.html for WCAG 2.2 Level AA standards."""
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'NetlifySitev3', 'leibnitz6.html'))
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    audit = run_wcag_22_audit(html_content)
    assert audit['compliance_score_percent'] == 100.0
    assert len(audit['violations']) == 0
