# -*- coding: utf-8 -*-
"""
Suganita AST Parser
Parses Suganita token stream into abstract syntax trees for VM & Signal engine execution.
"""

from .tokens import Token, TokenType

class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements: list[ASTNode]):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode({self.statements})"

class LiteralNode(ASTNode):
    def __init__(self, value, val_type: str):
        self.value = value
        self.val_type = val_type # 'string', 'number', 'identifier'

    def __repr__(self):
        return f"LiteralNode({repr(self.value)}, type={self.val_type})"

class PrintNode(ASTNode):
    def __init__(self, expression: ASTNode):
        self.expression = expression

    def __repr__(self):
        return f"PrintNode({self.expression})"

class PushNode(ASTNode):
    def __init__(self, value: ASTNode):
        self.value = value

    def __repr__(self):
        return f"PushNode({self.value})"

class PopNode(ASTNode):
    def __repr__(self):
        return "PopNode()"

class AssignNode(ASTNode):
    def __init__(self, name: str, value: ASTNode):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"AssignNode({self.name} = {self.value})"

class FunctionCallNode(ASTNode):
    def __init__(self, name: str, args: list[ASTNode]):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCallNode({self.name}, args={self.args})"

class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: list[ASTNode], else_branch: list[ASTNode] = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch or []

    def __repr__(self):
        return f"IfNode(cond={self.condition}, then={self.then_branch}, else={self.else_branch})"

class PlotNode(ASTNode):
    def __init__(self, target: ASTNode, title: str = "Signal Spectrum"):
        self.target = target
        self.title = title

    def __repr__(self):
        return f"PlotNode(target={self.target}, title={repr(self.title)})"

class MultiColumnNode(ASTNode):
    def __init__(self, target: ASTNode):
        self.target = target

    def __repr__(self):
        return f"MultiColumnNode({self.target})"

class JointAnalysisNode(ASTNode):
    def __init__(self, title: str = "Leibnitz 7 Joint Signal Analysis"):
        self.title = title

    def __repr__(self):
        return f"JointAnalysisNode(title={repr(self.title)})"

class BatchProcessNode(ASTNode):
    def __init__(self, target: ASTNode):
        self.target = target

    def __repr__(self):
        return f"BatchProcessNode({self.target})"

class DelayNode(ASTNode):
    def __init__(self, ms: ASTNode):
        self.ms = ms

    def __repr__(self):
        return f"DelayNode({self.ms})"

class HaltNode(ASTNode):
    def __repr__(self):
        return "HaltNode()"

class NopNode(ASTNode):
    def __repr__(self):
        return "NopNode()"


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.length = len(tokens)

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx >= self.length:
            return self.tokens[-1]
        return self.tokens[idx]

    def _match(self, *types: TokenType) -> bool:
        if self._peek().type in types:
            self.pos += 1
            return True
        return False

    def _consume(self, type_: TokenType, err_msg: str) -> Token:
        tok = self._peek()
        if tok.type == type_:
            self.pos += 1
            return tok
        raise SyntaxError(f"Syntax Error at Line {tok.line}, Col {tok.column}: {err_msg} (got {tok.type.name})")

    def parse(self) -> ProgramNode:
        statements = []
        while self.pos < self.length and self._peek().type != TokenType.EOF:
            # Skip newlines / dandas at top level
            if self._match(TokenType.NEWLINE, TokenType.DANDA):
                continue
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(statements)

    def _parse_statement(self) -> ASTNode:
        tok = self._peek()

        # Print / Likho statement: लिखो <expr>
        if self._match(TokenType.LIKHO, TokenType.ANKA_LIKHO):
            expr = self._parse_expression()
            self._optional_terminator()
            return PrintNode(expr)

        # Push / Pravesha statement: प्रवेश <expr>
        if self._match(TokenType.PRAVESHA):
            expr = self._parse_expression()
            self._optional_terminator()
            return PushNode(expr)

        # Pop / Visarjana statement: विसर्जन
        if self._match(TokenType.VISARJANA):
            self._optional_terminator()
            return PopNode()

        # Plot / Ruparekha statement: रूपरेखा <expr>
        if self._match(TokenType.RUPAREKHA):
            expr = self._parse_expression()
            title = "Signal Graph"
            if isinstance(expr, LiteralNode) and expr.val_type == 'string':
                title = expr.value
            self._optional_terminator()
            return PlotNode(expr, title=title)

        # Multi-Column / Bahustambha statement: बहुस्तम्भ <csv_path_or_expr>
        if self._match(TokenType.BAHUSTAMBHA):
            expr = self._parse_expression()
            self._optional_terminator()
            return MultiColumnNode(expr)

        # Joint Analysis / Samyukta statement: संयुक्त <optional_title>
        if self._match(TokenType.SAMYUKTA):
            title = "Leibnitz 7 Joint Signal Analysis"
            if self._peek().type in (TokenType.STRING, TokenType.IDENTIFIER):
                expr = self._parse_expression()
                if isinstance(expr, LiteralNode) and expr.val_type == 'string':
                    title = expr.value
            self._optional_terminator()
            return JointAnalysisNode(title=title)

        # Batch Processing / Sanchatmaka statement: संचात्मक <dir_path>
        if self._match(TokenType.SANCHATMAKA):
            expr = self._parse_expression()
            self._optional_terminator()
            return BatchProcessNode(expr)

        # Delay / Ruko statement: रुको <ms>
        if self._match(TokenType.RUKO):
            ms = self._parse_expression()
            self._optional_terminator()
            return DelayNode(ms)

        # Halt / Nirodha: निरोध
        if self._match(TokenType.NIRODHA):
            self._optional_terminator()
            return HaltNode()

        # NOP / Shu: शु
        if self._match(TokenType.SHU):
            self._optional_terminator()
            return NopNode()

        # If / Yadi: यदि <cond> ᳵ ... ᳶ
        if self._match(TokenType.YADI):
            cond = self._parse_expression()
            then_branch = self._parse_block()
            else_branch = []
            if self._match(TokenType.ANYATHA):
                else_branch = self._parse_block()
            return IfNode(cond, then_branch, else_branch)

        # Variable Assignment: <id> ः <expr>  or  <id> = <expr>
        if tok.type == TokenType.IDENTIFIER and self._peek(1).type in (TokenType.VISARGA, TokenType.YOGA): # Visarga ः used for assignment
            name = tok.value
            self.pos += 1
            self._match(TokenType.VISARGA)
            val = self._parse_expression()
            self._optional_terminator()
            return AssignNode(name, val)

        # Function Call or Expression Statement
        expr = self._parse_expression()
        self._optional_terminator()
        return expr

    def _parse_block(self) -> list[ASTNode]:
        statements = []
        if self._match(TokenType.BLOCK_START):
            while self.pos < self.length and self._peek().type not in (TokenType.BLOCK_END, TokenType.EOF):
                if self._match(TokenType.NEWLINE, TokenType.DANDA):
                    continue
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
            self._consume(TokenType.BLOCK_END, "Expected closing block marker (ᳶ or })")
        else:
            # Single line block
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    def _parse_expression(self) -> ASTNode:
        tok = self._peek()

        if self._match(TokenType.STRING):
            return LiteralNode(tok.value, 'string')

        if self._match(TokenType.NUMBER):
            val = float(tok.value) if '.' in tok.value else int(tok.value)
            return LiteralNode(val, 'number')

        if self._match(TokenType.IDENTIFIER):
            # Check for function call
            if self._peek().type == TokenType.LPAREN:
                self.pos += 1 # consume (
                args = []
                if self._peek().type != TokenType.RPAREN:
                    args.append(self._parse_expression())
                    while self._match(TokenType.COMMA):
                        args.append(self._parse_expression())
                self._consume(TokenType.RPAREN, "Expected ')' after function arguments")
                return FunctionCallNode(tok.value, args)
            return LiteralNode(tok.value, 'identifier')

        # Fallback literal
        self.pos += 1
        return LiteralNode(tok.value, 'raw')

    def _optional_terminator(self):
        while self._match(TokenType.DANDA, TokenType.NEWLINE):
            pass
