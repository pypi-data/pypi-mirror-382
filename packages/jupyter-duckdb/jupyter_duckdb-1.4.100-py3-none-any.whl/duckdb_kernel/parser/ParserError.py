class ParserError(Exception):
    def __init__(self, message: str, depth: int):
        super().__init__(message)

        self.message: str = message
        self.depth: int = depth


class RAParserError(ParserError):
    pass


class DCParserError(ParserError):
    pass


class LogicParserError(ParserError):
    pass
