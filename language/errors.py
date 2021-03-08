from language.utils import Position


# ===========================
# ERROR BASE
# ===========================
class ErrorBase:
    def __init__(self, name: str, details: str, pos_start: Position, pos_end: Position):
        self.name = name
        self.details = details
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        error = f'Error in file {self.pos_start.filename}, line {self.pos_start.line_no + 1}\n\n'
        error += self.point_error() + '\n\n'
        error += f'{self.name}: {self.details}'
        return error

    def point_error(self):
        err = ''
        text = self.pos_start.text

        idx_start = max(text.rfind('\n', 0, self.pos_start.index), 0)
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

        num_lines = self.pos_end.line_no - self.pos_start.line_no + 1
        for i in range(num_lines):
            line = text[idx_start: idx_end]
            col_start = self.pos_start.col_no if i == 0 else 0
            col_end = self.pos_end.col_no if i == num_lines - 1 else len(line) - 1

            err += line + '\n'
            err += ' ' * col_start + '^' * (col_end - col_start)

            idx_start = idx_end
            idx_end = text.find('\n', idx_start + 1)
            if idx_end < 0: idx_end = len(text)

        return err.replace('\t', '')


# ===========================
# Invalid Character
# ===========================
class InvalidCharError(ErrorBase):
    def __init__(self, details, pos_start, pos_end):
        super().__init__('Invalid Character', details, pos_start, pos_end)


# ===========================
# Invalid Syntax
# ===========================
class InvalidSyntaxError(ErrorBase):
    def __init__(self, details, pos_start, pos_end):
        super().__init__('Invalid Syntax', details, pos_start, pos_end)


# ===========================
# Runtime Error
# ===========================
class RunTimeError(ErrorBase):
    def __init__(self, context, details, pos_start, pos_end):
        super().__init__('Runtime Error', details, pos_start, pos_end)
        self.context = context

    def __repr__(self):
        error = self.traceback() + '\n'
        error += self.point_error() + '\n'
        error += f'{self.name}: {self.details}'
        return error

    def traceback(self):
        err = ''
        pos = self.pos_start.copy()
        context = self.context

        while context:
            err = f'\tError in file {pos.filename}, line {pos.line_no + 1} of {context.context_name},\n' + err
            pos = context.parent_entry
            context = context.parent

        return 'Traceback:\n' + err


# ===========================
# Expected Character
# ===========================
class ExpectedCharError(ErrorBase):
    def __init__(self, details, pos_start: Position, pos_end: Position):
        super().__init__('Expected Character', details, pos_start, pos_end)
