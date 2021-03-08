from language.datatypes import Number
from language.nodes import *
from language.errors import *
from language.tokens import TokenType, Keyword
from language.results import ParseResult, RuntimeResult


# ===========================
# LEXER
# ===========================
def isNumberToken(char: str):
    return char.isdigit() or char == '.'


def isIDOrKeyword(char: str):
    return char.isalnum() or char == '_'


class Lexer:
    def __init__(self, filename: str, text: str):
        self.filename = filename
        self.text = text

        self.pos = Position(filename, text)
        self.char = None
        self.increment()

    def increment(self):
        self.pos.increment(self.char)
        self.char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def tokenize(self):
        tokens = []

        while self.char:
            if self.char in ' \t':
                self.increment()

            elif isNumberToken(self.char):
                tokens.append(self.makeNumberToken())

            elif isIDOrKeyword(self.char):
                tokens.append(self.makeIDOrKeyword())

            elif self.char == '!':
                token, err = self.notEqToken()
                if err: return None, err
                tokens.append(token)

            elif self.char == '<':
                tokens.append(self.lessThanEqToken())

            elif self.char == '>':
                tokens.append(self.greaterThanEqToken())

            else:
                try:
                    token_type = TokenType(self.char)
                    tokens.append(Token(token_type, pos_start=self.pos))
                    self.increment()
                except ValueError:
                    char = self.char
                    pos_start = self.pos.copy()
                    self.increment()
                    return [], InvalidCharError(f"'{char}'", pos_start, self.pos)

        tokens.append(Token(TokenType.EOF, pos_start=self.pos))
        return tokens, None

    def notEqToken(self):
        pos_start = self.pos.copy()
        self.increment()

        if self.char == '=':
            self.increment()
            return Token(TokenType.NOT_EQUAL, pos_start=pos_start, pos_end=self.pos), None

        self.increment()
        return None, ExpectedCharError(
            "'=' after !",
            pos_start=pos_start, pos_end=self.pos
        )

    def lessThanEqToken(self):
        token_type = TokenType.LESS_THAN
        pos_start = self.pos.copy()
        self.increment()

        if self.char == '=':
            self.increment()
            token_type = TokenType.LESS_THAN_EQUAL

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def greaterThanEqToken(self):
        token_type = TokenType.LESS_THAN
        pos_start = self.pos.copy()
        self.increment()

        if self.char == '=':
            self.increment()
            token_type = TokenType.LESS_THAN_EQUAL

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def makeNumberToken(self):
        num = ''
        isFloat = False
        pos_start = self.pos.copy()

        while self.char and isNumberToken(self.char):
            if self.char == '.':
                if isFloat: break
                isFloat = True
                num += '.'
            else:
                num += self.char
            self.increment()

        if isFloat: return Token(TokenType['FLOAT'], float(num), pos_start, self.pos)
        return Token(TokenType['INT'], int(num), pos_start, self.pos)

    def makeIDOrKeyword(self):
        inp_str = ''
        pos_start = self.pos.copy()

        while self.char and isIDOrKeyword(self.char):
            inp_str += self.char
            self.increment()

        try:
            keyword = Keyword(inp_str)
            return Token(TokenType.KEYWORD, keyword, pos_start, self.pos)
        except ValueError:
            return Token(TokenType.IDENTIFIER, inp_str, pos_start, self.pos)


# ===========================
# PARSER
# ===========================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.token = None
        self.increment()

    def increment(self):
        self.token_index += 1
        self.token = self.tokens[self.token_index] if self.token_index < len(self.tokens) else None
        return self.token

    def binaryOperation(self, funcLeft, tokens, funcRight=None):
        if funcRight is None:
            funcRight = funcLeft

        res = ParseResult()
        left = res.register(funcLeft())
        if res.error: return res

        while self.token and (self.token.token_type in tokens or self.token.value in tokens):
            operator = self.token
            res.register(self.increment())
            right = res.register(funcRight())
            if res.error: return res

            left = BinaryOpNode(left, operator, right)

        return res.success(left)

    def parseIfExpr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.token.value == Keyword.IF:
            return res.failure(InvalidSyntaxError(
                'Expected IF statement',
                self.token.pos_start, self.token.pos_end
            ))

        res.register(self.increment())

        cond = res.register(self.expr())
        if res.error: return res

        if not self.token.value == Keyword.THEN:
            return res.failure(InvalidSyntaxError(
                'Expected THEN AFTER IF',
                self.token.pos_start, self.token.pos_end
            ))

        res.register(self.increment())

        expr = res.register(self.expr())
        if res.error: return res
        cases.append((cond, expr))

        while self.token.value == Keyword.ELIF:
            res.register(self.increment())

            cond = res.register(self.expr())
            if res.error: return res

            if not self.token.value == Keyword.THEN:
                return res.failure(InvalidSyntaxError(
                    'Expected THEN AFTER ELSEIF',
                    self.token.pos_start, self.token.pos_end
                ))

            res.register(self.increment())

            expr = res.register(self.expr())
            if res.error: return res
            cases.append((cond, expr))

        if self.token.value == Keyword.ELSE:
            res.register(self.increment())

            expr = res.register(self.expr())
            if res.error: return res
            else_case = expr

        return res.success(ConditionsNode(cases, else_case))

    def atom(self):
        res = ParseResult()
        token = self.token

        if token.token_type in (TokenType.INT, TokenType.FLOAT):
            res.register(self.increment())
            return res.success(NumberNode(token))

        elif token.token_type == TokenType.IDENTIFIER:
            res.register(self.increment())
            return res.success(VarAccessNode(token))

        elif token.token_type == TokenType.L_PAREN:
            res.register(self.increment())
            expr = res.register(self.expr())
            if res.error: return res

            if self.token.token_type == TokenType.R_PAREN:
                res.register(self.increment())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    "Expected ')'",
                    self.token.pos_start, self.token.pos_end
                ))

        elif token.value == Keyword.IF:
            expr = res.register(self.parseIfExpr())
            if res.error: return res
            return res.success(expr)

        return res.failure(InvalidSyntaxError(
            "Expected a number, or one of '+', '-' or '('!",
            token.pos_start, token.pos_end
        ))

    def power(self):
        return self.binaryOperation(self.atom, [TokenType.POWER], self.factor)

    def factor(self):
        res = ParseResult()
        token = self.token

        if token.token_type in (TokenType.PLUS, TokenType.MINUS):
            res.register(self.increment())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(token, factor))

        return self.power()

    def term(self):
        return self.binaryOperation(self.factor, (TokenType.MULTIPLY, TokenType.DIVIDE))

    def arith_expr(self):
        return self.binaryOperation(self.term, (TokenType.PLUS, TokenType.MINUS))

    def comp_expr(self):
        res = ParseResult()

        node = res.register(self.binaryOperation(self.arith_expr, (
            TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN,
            TokenType.LESS_THAN_EQUAL, TokenType.GREATER_THAN, TokenType.GREATER_THAN_EQUAL
        )))

        if res.error: return res
        return res.success(node)

    def expr(self):
        res = ParseResult()

        if self.token.value == Keyword.ASSIGN_START:
            res.register(self.increment())
            if self.token.token_type != TokenType.IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    'Expected identifier!',
                    self.token.pos_start, self.token.pos_end
                ))

            var = self.token
            res.register(self.increment())

            expr = res.register(self.expr())
            if res.error: return res

            if self.token.value != Keyword.ASSIGN_END:
                return res.failure(InvalidSyntaxError(
                    'Expected assignment to end with "hai"',
                    self.token.pos_start, self.token.pos_end
                ))

            res.register(self.increment())
            return res.success(VarAssignNode(var, expr))

        expr = res.register(self.binaryOperation(self.comp_expr, (Keyword.AND, Keyword.OR)))
        if res.error: return res.failure(InvalidSyntaxError(
            'Expected var, number, or +, - or (',
            self.token.pos_start, self.token.pos_end
        ))
        return res.success(expr)

    def parse(self):
        res = self.expr()

        if not res.error and self.token.token_type != TokenType.EOF:
            return res.failure(InvalidSyntaxError(
                'Expected +, -, * or /',
                self.token.pos_start, self.token.pos_end
            ))

        return res


# ===========================
# INTERPRETER
# ===========================
class Interpreter:
    def __init__(self, context):
        self.context = context

    def visit(self, node):
        name = f'parse{type(node).__name__}'
        method = getattr(self, name)
        return method(node)

    def parseNumberNode(self, node: NumberNode):
        return RuntimeResult().success(
            Number(node.token.value, node.token.pos_start, node.token.pos_end, self.context)
        )

    def parseUnaryOpNode(self, node: UnaryOpNode):
        res = RuntimeResult()

        num = res.register(self.visit(node.node))
        if res.error: return res

        error = None
        if node.operator.token_type == TokenType.MINUS:
            num, error = num.mul(Number(-1))

        if error: return res.failure(error)
        return res.success(num.setPos(node.pos_start, node.pos_end))

    def parseBinaryOpNode(self, node: BinaryOpNode):
        res = RuntimeResult()

        left = res.register(self.visit(node.left))
        if res.error: return res

        right = res.register(self.visit(node.right))
        if res.error: return res

        num = Number(0)
        error = None

        if node.operator.token_type == TokenType.PLUS:
            num, error = left.plus(right)
        elif node.operator.token_type == TokenType.MINUS:
            num, error = left.minus(right)
        elif node.operator.token_type == TokenType.MULTIPLY:
            num, error = left.mul(right)
        elif node.operator.token_type == TokenType.DIVIDE:
            num, error = left.div(right)
        elif node.operator.token_type == TokenType.POWER:
            num, error = left.pow(right)

        elif node.operator.token_type == TokenType.EQUAL:
            num, error = left.equalTo(right)
        elif node.operator.token_type == TokenType.NOT_EQUAL:
            num, error = left.notEqualTo(right)
        elif node.operator.token_type == TokenType.LESS_THAN:
            num, error = left.lessThan(right)
        elif node.operator.token_type == TokenType.LESS_THAN_EQUAL:
            num, error = left.lessThanEqTo(right)
        elif node.operator.token_type == TokenType.GREATER_THAN:
            num, error = left.greaterThan(right)
        elif node.operator.token_type == TokenType.GREATER_THAN_EQUAL:
            num, error = left.greaterThanEqualTo(right)

        elif node.operator.value == Keyword.AND:
            num, error = left.andWith(right)
        elif node.operator.value == Keyword.OR:
            num, error = left.orWith(right)

        if error: return res.failure(error)
        return res.success(num.setPos(node.pos_start, node.pos_end))

    def parseVarAccessNode(self, node: VarAccessNode):
        res = RuntimeResult()

        var = node.var_name.value
        value = self.context.symbol_table.get(var)

        if value is None:
            return res.failure(RunTimeError(
                self.context,
                f'{var} is not defined!',
                node.pos_start, node.pos_end
            ))

        value = value.copy().setPos(node.pos_start, node.pos_end)
        return res.success(value)

    def parseVarAssignNode(self, node: VarAssignNode):
        res = RuntimeResult()

        var = node.var_name.value
        value = res.register(self.visit(node.value))
        if res.error: return res

        self.context.symbol_table.set(var, value)
        return res.success(value)

    def parseConditionsNode(self, node: ConditionsNode):
        res = RuntimeResult()

        for cond, expr in node.cases:
            comp = res.register(self.visit(cond))
            if res.error: return res

            if comp.isTrue():
                expr_res = res.register(self.visit(expr))
                if res.error: return res
                return res.success(expr_res)

        if node.else_case:
            else_res = res.register(self.visit(node.else_case))
            if res.error: return res
            return res.success(else_res)

        return res.success(None)
