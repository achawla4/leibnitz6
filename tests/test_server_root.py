# -*- coding: utf-8 -*-
"""
Unit test suite verifying root route '/' and '/health' endpoints on Leibnitz 7 server.
"""

import pytest
from leibnitz6_server.server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_root_index_endpoint(client):
    """Verify root GET / returns 200 OK (leibnitz6.html or status JSON)."""
    resp = client.get('/')
    assert resp.status_code == 200

def test_health_endpoint(client):
    """Verify /health returns 200 OK and Leibnitz7 server info."""
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.json
    assert data['server'] == 'Leibnitz7'
    assert data['status'] == 'ONLINE'
