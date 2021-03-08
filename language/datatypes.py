from __future__ import annotations
from language.errors import RunTimeError


class Number:
    def __init__(self, value, pos_start=None, pos_end=None, context=None):
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.context = context

    def __repr__(self):
        return f'{self.value}'

    def copy(self):
        return Number(self.value, self.pos_start, self.pos_end, self.context)

    def setPos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def plus(self, other) -> (Number, RunTimeError):
        if isinstance(other, Number):
            return Number(self.value + other.value, context=self.context), None

    def minus(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value, context=self.context), None

    def mul(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value, context=self.context), None

    def div(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(
                    self.context,
                    'Division by zero not defined',
                    other.pos_start, other.pos_end
                )
            return Number(self.value / other.value, context=self.context), None

    def pow(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value, context=self.context), None
