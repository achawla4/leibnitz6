# -*- coding: utf-8 -*-
"""
Tests for Suganita Engine Core Component (Phase 1 Validation)
"""

import os
import sys
import pytest

# Ensure workspace root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from suganita_engine import Lexer, Parser, SuganitaVM, compile_and_run, TokenType

def test_lexer_devanagari_tokens():
    code = """
    लिखो "REALInstitute"
    प्रवेश "Signal_Data_Buffer"
    रुको १०००
    निरोध
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    token_types = [t.type for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)]
    assert TokenType.LIKHO in token_types
    assert TokenType.PRAVESHA in token_types
    assert TokenType.RUKO in token_types
    assert TokenType.NIRODHA in token_types

def test_lexer_numbers():
    code = "रुको २५००"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    num_toks = [t for t in tokens if t.type == TokenType.NUMBER]
    assert len(num_toks) == 1
    assert num_toks[0].value == "2500"

def test_parser_ast():
    code = """
    लिखो "Testing Signal 1"
    प्रवेश "Sample_Payload"
    रूपरेखा "ECG_Waveform"
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert len(ast.statements) == 3

def test_vm_execution():
    code = """
    लिखो REALInstitute
    लिखo Post-QuantumEmail(Simulation)
    लिखो MessageBody
    प्रवेश Type_your_secure_message_here
    प्रवेश Type_your_additional_notes
    रूपरेखा "Sinusoidal_12Hz_Analysis"
    """
    summary, su_output = compile_and_run(code, "signal1.su")
    
    assert "REALInstitute" in summary['labels']
    assert "MessageBody" in summary['labels']
    assert "Type_your_secure_message_here" in summary['input_fields']
    assert len(summary['plots']) == 1
    assert "PLOT_B64:" in su_output
    assert "[UI_LABELS]" in su_output

if __name__ == "__main__":
    pytest.main([__file__])
