# -*- coding: utf-8 -*-
"""
Suganita Engine Core Package
"""

from .tokens import Token, TokenType, DEVANAGARI_KEYWORDS, ASCII_ALIASES
from .lexer import Lexer
from .parser import Parser, ProgramNode
from .vm import SuganitaVM
from .signal_adapter import SignalAdapter

def compile_and_run(source_code: str, source_filename: str = "signal1.su") -> tuple[dict, str]:
    """
    Convenience function to tokenize, parse, execute a Suganita script,
    and generate the formatted .su output payload string.
    """
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    vm = SuganitaVM()
    summary = vm.run(ast)
    su_output = vm.generate_su_output(source_filename)
    return summary, su_output
