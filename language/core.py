from language.utils import Context
from language.tokens import SymbolTable
from language.parsing import Lexer, Parser, Interpreter

GLOBALS = SymbolTable()


def interpret(filename: str, text: str):
    tokens, error = Lexer(filename, text).tokenize()
    if error: return error

    res = Parser(tokens).parse()
    if res.error: return res.error

    context = Context('<MAIN>', symbol_table=GLOBALS)
    res = Interpreter(context).visit(res.value)
    if res.error: return res.error
    return res.value
