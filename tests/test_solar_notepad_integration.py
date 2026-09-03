# -*- coding: utf-8 -*-
"""
Integration Tests: Solar .gguf AI Model + Structured Notepad v4 + Suganita DSL for Leibnitz 6.0
Verifies inline cell evaluation, inline AI auto-completion, and prompt explanation.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solar_copilot import SolarLLMClient, build_completion_prompt, build_explanation_prompt
from suganita_engine import compile_and_run

def test_solar_gguf_model_discovery():
    """Verify GGUF model manager discovers local or configured GGUF model paths."""
    client = SolarLLMClient()
    info = client.get_active_model_info()
    assert 'active_model' in info
    assert 'endpoint_url' in info

def test_suganita_inline_solar_completion():
    """Verify inline Solar Copilot auto-completion generates valid Suganita DSL tokens."""
    client = SolarLLMClient()
    
    # Test prompt starting with लिखो (Write)
    prompt1 = 'लिखो "Signal Processing Matrix"'
    completion1 = client.complete_code(prompt1)
    assert any(kw in completion1 for kw in ['प्रवेश', 'रुको', 'रूपरेखा', 'निरोध'])
    
    # Test prompt starting with प्रवेश (Input)
    prompt2 = 'प्रवेश "Spectral_Input_Buffer"'
    completion2 = client.complete_code(prompt2)
    assert any(kw in completion2 for kw in ['रुको', 'रूपरेखा', 'निरोध'])

def test_solar_code_explanation():
    """Verify Solar AI copilot code explanation of Suganita Devanagari DSL."""
    client = SolarLLMClient()
    suganita_code = """
लिखो "Suganita Spectral Analysis"
प्रवेश "Signal_Payload"
रूपरेखा "Spectral_Graph"
निरोध
"""
    explanation = client.explain_code(suganita_code)
    assert "UI label" in explanation or "Execute" in explanation
    assert "FFT spectrum" in explanation or "Spectral_Graph" in explanation

def test_structured_notepad_suganita_execution(tmp_path):
    """Verify Structured Notepad cell execution of a full Suganita signal processing script."""
    sample_suganita_script = """
# Leibnitz 6.0 Signal Test
लिखो "Leibnitz 6.0 Signal Processor"
प्रवेश "Raw_Audio_Buffer"
रुको 100
रूपरेखा "FFT_Spectral_Transform"
निरोध
"""
    out_file = tmp_path / "test_cell.su"
    summary, su_output = compile_and_run(sample_suganita_script, str(out_file))
    
    assert len(summary['logs']) >= 1
    assert any("Leibnitz 6.0 Signal Processor" in log for log in summary['logs'])
    assert len(summary['plots']) == 1
    assert 'image_b64' in summary['plots'][0]

if __name__ == "__main__":
    pytest.main([__file__])
