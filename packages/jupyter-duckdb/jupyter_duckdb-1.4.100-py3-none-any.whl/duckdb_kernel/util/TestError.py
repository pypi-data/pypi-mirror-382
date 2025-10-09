class TestError(Exception):
    @property
    def message(self) -> str:
        return str(self)
