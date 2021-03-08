# ===========================
# RESULTS BASE
# ===========================
class ResultBase:
    def __init__(self):
        self.error = None
        self.value = None

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


# ===========================
# PARSE RESULT
# ===========================
class ParseResult(ResultBase):
    def __init__(self):
        super().__init__()
        self.advanced = 0

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            self.advanced += res.advanced
            return res.value

        self.advanced += 1
        return res

    def failure(self, error):
        if not self.error or self.advanced == 0:
            self.error = error
        return self


# ===========================
# RUNTIME RESULT
# ===========================
class RuntimeResult(ResultBase):
    def register(self, res):
        if res.error: self.error = res.error
        return res.value
