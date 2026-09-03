# -*- coding: utf-8 -*-
"""
Suganita Token Definitions and Lexical Constants
Based on Suganita PDF Specification (Nyaya Logic, Vedic Math, Paninian Grammar, Sankhya & Yoga).
"""

from enum import Enum, auto

class TokenType(Enum):
    # Special Tokens
    EOF = auto()
    ERROR = auto()
    NEWLINE = auto()
    
    # Identifiers & Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    
    # Punctuation & Delimiters
    DANDA = auto()          # । (Statement terminator)
    VISARGA = auto()        # ः (Assignment / Association)
    BLOCK_START = auto()     # ᳵ or {
    BLOCK_END = auto()       # ᳶ or }
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    COMMA = auto()          # ,
    
    # Keywords - Nyaya Logic & Control Flow
    YADI = auto()           # यदि (if)
    ANYATHA = auto()        # अन्यथा (else)
    HETU = auto()           # हेतु (cause / condition / jump if zero)
    UDAHARANA = auto()      # उदाहरण (example / jump if nonzero)
    KRAMA = auto()          # क्रम (for loop)
    JABATAKA = auto()       # जबतक (while loop)
    
    # Keywords - Execution & Halting
    KARYA = auto()          # कार्य (function)
    MUKHYA = auto()         # मुख्य (main entry)
    VAPASA = auto()         # वापस (return)
    AHVANA = auto()         # आह्वान (call)
    PRATYAVARTANA = auto()  # प्रत्यावर्तन (return)
    NIRODHA = auto()        # निरोध (halt)
    SHU = auto()            # शु / शूः (sunya / NOP / pause)
    
    # Operators & Vedic Arithmetic
    YOGA = auto()           # योग (+)
    VYAVAKALANA = auto()    # व्यवकलन (-)
    GUNANA = auto()         # गुणन (*)
    BHAGAHARA = auto()      # भागहार (/)
    SHESHA = auto()         # शेष (%)
    
    # Comparisons & Logical Rules
    TULYA = auto()          # तुल्य (==)
    ATULYA = auto()         # अतुल्य (!=)
    HINA = auto()           # हीन (<)
    SHRESTHA = auto()       # श्रेष्ठ (>)
    ANVAYA = auto()         # अन्वय (AND)
    VYATIREKA = auto()      # व्यतिरेक (OR)
    NISEDHA = auto()        # निषेध (NOT)
    
    # Hardware & Signal Primitives
    LIKHO = auto()          # लिखो (print / emit)
    ANKA_LIKHO = auto()     # अङ्क_लिखo (print int)
    SPARSHA_PADHO = auto()  # स्पर्श_पढ़ो (digital read)
    SPARSHA_LIKHO = auto()  # स्पर्श_लिखो (digital write)
    RASA_PADHO = auto()     # रस_पढ़ो (analog read / signal read)
    RUKO = auto()           # रुको (delay)
    RUPAREKHA = auto()      # रूपरेखा (plot / spectrum preview)
    BAHUSTAMBHA = auto()     # बहुस्तम्भ (multi-column signal load)
    SAMYUKTA = auto()        # संयुक्त (joint analysis / cross-correlation)
    SANCHATMAKA = auto()     # संचात्मक (batch processing)
    ANTARIKSHASAMAYA = auto() # अंतरिक्षसमय (space-time 2D fourier security analysis)
    
    # VM Stack Opcodes
    PRAVESHA = auto()       # प्रवेश (push)
    VISARJANA = auto()      # विसर्जन (pop)
    PUNARAVRTTI = auto()    # पुनरावृत्ति (dup)
    PARIVARTA = auto()      # परिवर्तन (swap)
    
    # ML Primitives
    MODEL = auto()          # मॉडल (model)
    PURVANUMANA = auto()    # पूर्वानुमान (predict)
    SUTRA_SAMUHA = auto()   # सूत्र_समूह (tensor)
    BHARA_STHAPANA = auto() # भार_स्थापन (load weights)
    REKHA_PARIVARTANA = auto() # रेखा_परिवर्तन (linear map)
    SIMA = auto()           # सीमा (threshold)


# Mapping of Devanagari string representations to TokenType
DEVANAGARI_KEYWORDS = {
    'यदि': TokenType.YADI,
    'अन्यथा': TokenType.ANYATHA,
    'हेतु': TokenType.HETU,
    'उदाहरण': TokenType.UDAHARANA,
    'क्रम': TokenType.KRAMA,
    'जबतक': TokenType.JABATAKA,
    'कार्य': TokenType.KARYA,
    'मुख्य': TokenType.MUKHYA,
    'वापस': TokenType.VAPASA,
    'आह्वान': TokenType.AHVANA,
    'प्रत्यावर्तन': TokenType.PRATYAVARTANA,
    'निरोध': TokenType.NIRODHA,
    'शु': TokenType.SHU,
    'शूः': TokenType.SHU,
    'योग': TokenType.YOGA,
    'व्यवकलन': TokenType.VYAVAKALANA,
    'गुणन': TokenType.GUNANA,
    'भागहार': TokenType.BHAGAHARA,
    'शेष': TokenType.SHESHA,
    'तुल्य': TokenType.TULYA,
    'अतुल्य': TokenType.ATULYA,
    'हीन': TokenType.HINA,
    'श्रेष्ठ': TokenType.SHRESTHA,
    'अन्वय': TokenType.ANVAYA,
    'व्यतिरेक': TokenType.VYATIREKA,
    'निषेध': TokenType.NISEDHA,
    'लिखो': TokenType.LIKHO,
    'अङ्क_लिखो': TokenType.ANKA_LIKHO,
    'स्पर्श_पढ़ो': TokenType.SPARSHA_PADHO,
    'स्पर्श_लिखो': TokenType.SPARSHA_LIKHO,
    'रस_पढ़ो': TokenType.RASA_PADHO,
    'रुको': TokenType.RUKO,
    'रूपरेखा': TokenType.RUPAREKHA,
    'बहुस्तम्भ': TokenType.BAHUSTAMBHA,
    'संयुक्त': TokenType.SAMYUKTA,
    'संचात्मक': TokenType.SANCHATMAKA,
    'अंतरिक्षसमय': TokenType.ANTARIKSHASAMAYA,
    'प्रवेश': TokenType.PRAVESHA,
    'विसर्जन': TokenType.VISARJANA,
    'पुनरावृत्ति': TokenType.PUNARAVRTTI,
    'परिवर्तन': TokenType.PARIVARTA,
    'मॉडल': TokenType.MODEL,
    'पूर्वानुमान': TokenType.PURVANUMANA,
    'सूत्र_समूह': TokenType.SUTRA_SAMUHA,
    'भार_स्थापन': TokenType.BHARA_STHAPANA,
    'रेखा_परिवर्तन': TokenType.REKHA_PARIVARTANA,
    'सीमा': TokenType.SIMA,
}

# Optional ASCII aliases for rapid tooling / fallback
ASCII_ALIASES = {
    'if': TokenType.YADI,
    'else': TokenType.ANYATHA,
    'func': TokenType.KARYA,
    'main': TokenType.MUKHYA,
    'return': TokenType.VAPASA,
    'halt': TokenType.NIRODHA,
    'nop': TokenType.SHU,
    'print': TokenType.LIKHO,
    'push': TokenType.PRAVESHA,
    'pop': TokenType.VISARJANA,
    'delay': TokenType.RUKO,
    'plot': TokenType.RUPAREKHA,
    'multicolumn': TokenType.BAHUSTAMBHA,
    'joint': TokenType.SAMYUKTA,
    'batch': TokenType.SANCHATMAKA,
}


class Token:
    def __init__(self, type_: TokenType, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, L{self.line}:C{self.column})"
