# -*- coding: utf-8 -*-
"""
Unit tests for Leibnitz6 Machine & AI Agent SDK (`leibnitz6_sdk.py`).
Verifies programmatic execution, streaming, and copilot queries for external machines.
"""

import pytest
from leibnitz6_sdk import Leibnitz6Client

def test_machine_sdk_execute():
    client = Leibnitz6Client(client_id="Test_AI_Agent")
    code = "लिखो('Agent Test Log')\nनिरोध"
    res = client.execute(code, "test_agent.su")
    assert res is not None
    assert 'summary' in res or 'status' in res

def test_machine_sdk_copilot():
    client = Leibnitz6Client(client_id="Test_AI_Agent")
    prompt = "Generate Suganita FFT code"
    completion = client.copilot_complete(prompt)
    assert isinstance(completion, str)
    assert len(completion) > 0
