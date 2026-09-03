# -*- coding: utf-8 -*-
"""
Suganita Devanagari Lexer / Tokenizer
Supports Devanagari codepoints, Devanagari numerals, and Sanskrit punctuation.
"""

from .tokens import Token, TokenType, DEVANAGARI_KEYWORDS, ASCII_ALIASES

DEVANAGARI_DIGITS = {
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
}

def is_devanagari_char(ch: str) -> bool:
    """Check if character is within Devanagari Unicode block (U+0900 to U+097F) or Devanagari Extended."""
    code = ord(ch)
    return (0x0900 <= code <= 0x097F) or (0x1CD0 <= code <= 0x1FFF)

def is_identifier_start(ch: str) -> bool:
    return ch.isalpha() or is_devanagari_char(ch) or ch == '_'

def is_identifier_part(ch: str) -> bool:
    return is_identifier_start(ch) or ch.isdigit() or ch in DEVANAGARI_DIGITS


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(source)

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx >= self.length:
            return '\0'
        return self.source[idx]

    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def tokenize(self) -> list[Token]:
        tokens = []
        while self.pos < self.length:
            ch = self._peek()

            # Skip whitespace (except newlines which may separate statements)
            if ch in (' ', '\t', '\r'):
                self._advance()
                continue

            if ch == '\n':
                line, col = self.line, self.column
                self._advance()
                tokens.append(Token(TokenType.NEWLINE, '\n', line, col))
                continue

            # Comments (starting with // or # or --)
            if ch == '#' or (ch == '/' and self._peek(1) == '/'):
                while self.pos < self.length and self._peek() != '\n':
                    self._advance()
                continue

            # Sanskrit Danda (।) - Statement terminator
            if ch == '।' or ch == ';':
                line, col = self.line, self.column
                self._advance()
                tokens.append(Token(TokenType.DANDA, '।', line, col))
                continue

            # Sanskrit Visarga (ः) or Colon (:) - Association/Assignment
            if ch == 'ः' or ch == ':':
                line, col = self.line, self.column
                self._advance()
                tokens.append(Token(TokenType.VISARGA, 'ः', line, col))
                continue

            # Block markers: ᳵ or {
            if ch in ('ᳵ', '{'):
                line, col = self.line, self.column
                self._advance()
                tokens.append(Token(TokenType.BLOCK_START, ch, line, col))
                continue

            # Block markers: ᳶ or }
            if ch in ('ᳶ', '}'):
                line, col = self.line, self.column
                self._advance()
                tokens.append(Token(TokenType.BLOCK_END, ch, line, col))
                continue

            # Parentheses & Punctuation
            if ch == '(':
                line, col = self.line, self.column
                self._advance()
                tokens.append(Token(TokenType.LPAREN, '(', line, col))
                continue

            if ch == ')':
                line, col = self.line, self.column
                self._advance()
                tokens.append(Token(TokenType.RPAREN, ')', line, col))
                continue

            if ch == ',':
                line, col = self.line, self.column
                self._advance()
                tokens.append(Token(TokenType.COMMA, ',', line, col))
                continue

            # String literals
            if ch in ('"', "'"):
                quote = ch
                line, col = self.line, self.column
                self._advance() # consume quote
                start_pos = self.pos
                str_val = []
                while self.pos < self.length and self._peek() != quote:
                    if self._peek() == '\\':
                        self._advance()
                    str_val.append(self._advance())
                if self.pos < self.length:
                    self._advance() # consume closing quote
                tokens.append(Token(TokenType.STRING, ''.join(str_val), line, col))
                continue

            # Numbers (ASCII or Devanagari digits)
            if ch.isdigit() or ch in DEVANAGARI_DIGITS:
                line, col = self.line, self.column
                num_chars = []
                while self.pos < self.length and (self._peek().isdigit() or self._peek() in DEVANAGARI_DIGITS or self._peek() == '.'):
                    curr = self._advance()
                    num_chars.append(DEVANAGARI_DIGITS.get(curr, curr))
                val_str = ''.join(num_chars)
                tokens.append(Token(TokenType.NUMBER, val_str, line, col))
                continue

            # Identifiers and Keywords
            if is_identifier_start(ch):
                line, col = self.line, self.column
                id_chars = []
                while self.pos < self.length and is_identifier_part(self._peek()):
                    id_chars.append(self._advance())
                word = ''.join(id_chars)

                # Check keyword mappings
                if word in DEVANAGARI_KEYWORDS:
                    tok_type = DEVANAGARI_KEYWORDS[word]
                elif word in ASCII_ALIASES:
                    tok_type = ASCII_ALIASES[word]
                else:
                    tok_type = TokenType.IDENTIFIER

                tokens.append(Token(tok_type, word, line, col))
                continue

            # Unknown character / Single character operator fallback
            line, col = self.line, self.column
            unknown_ch = self._advance()
            tokens.append(Token(TokenType.ERROR, unknown_ch, line, col))

        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens
