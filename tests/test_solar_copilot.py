# -*- coding: utf-8 -*-
"""
Tests for Solar Copilot Component (Phase 3 Validation)
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solar_copilot import SolarLLMClient, build_completion_prompt, build_explanation_prompt, app

def test_prompt_formatting():
    prompt = build_completion_prompt('लिखो "TEST"')
    assert "Suganita" in prompt
    assert 'लिखो "TEST"' in prompt
    
    explanation_prompt = build_explanation_prompt('निरोध')
    assert "Explanation" in explanation_prompt

def test_client_completion_fallback():
    client = SolarLLMClient(endpoint_url="http://127.0.0.1:9999/fake_endpoint")
    comp = client.complete_code('लिखो "REAL"')
    assert "प्रवेश" in comp or "रूपरेखा" in comp
    assert "निरोध" in comp

def test_client_explanation_fallback():
    client = SolarLLMClient(endpoint_url="http://127.0.0.1:9999/fake_endpoint")
    code = 'लिखो "Header"\nप्रवेश "Field"\nरूपरेखा "Plot"\nनिरोध'
    expl = client.explain_code(code)
    assert "UI label" in expl
    assert "FFT spectrum" in expl

def test_copilot_rest_service():
    test_client = app.test_client()
    
    res = test_client.post('/api/copilot/complete', json={'prompt': 'लिखो Test'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'SUCCESS'
    assert 'completion' in data

    res = test_client.post('/api/copilot/explain', json={'code': 'निरोध'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'SUCCESS'
    assert 'explanation' in data

if __name__ == "__main__":
    pytest.main([__file__])
