from language.tokens import Token


# ===========================
# EXPRESSION TREE NODES
# ===========================
class NumberNode:
    def __init__(self, token: Token):
        self.token = token
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end


class BinaryOpNode:
    def __init__(self, left, operator: Token, right):
        self.left = left
        self.operator = operator
        self.right = right
        self.pos_start = left.pos_start
        self.pos_end = right.pos_end


class UnaryOpNode:
    def __init__(self, operator: Token, node):
        self.operator = operator
        self.node = node
        self.pos_start = operator.pos_start
        self.pos_end = node.pos_end


class VarAccessNode:
    def __init__(self, var_name):
        self.var_name = var_name
        self.pos_start = var_name.pos_start
        self.pos_end = var_name.pos_end


class VarAssignNode:
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value
        self.pos_start = var_name.pos_start
        self.pos_end = value.pos_end


class ConditionsNode:
    def __init__(self, cases, else_case=None):
        self.cases = cases
        self.else_case = else_case
        self.pos_start = self.cases[0][1].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end
