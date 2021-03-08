# ===========================
# POSITION
# ===========================
class Position:
    def __init__(self, filename, text, index=-1, line_no=0, col_no=-1):
        self.filename = filename
        self.text = text
        self.index = index
        self.line_no = line_no
        self.col_no = col_no

    def increment(self, char=None):
        self.index += 1
        self.col_no += 1

        if char == '\n':
            self.line_no += 1
            self.col_no = 0

        return self

    def copy(self):
        return Position(self.filename, self.text, self.index, self.line_no, self.col_no)


# ===========================
# CONTEXT
# ===========================
class Context:
    def __init__(self, context_name, parent=None, parent_entry: Position = None, symbol_table=None):
        self.context_name = context_name
        self.parent = parent
        self.parent_entry = parent_entry
        self.symbol_table = symbol_table
