from .elements import *
from .tokenizer import *


class LogicParser:
    @staticmethod
    def parse_query(query: str, depth: int = 0) -> LogicElement:
        initial_token = Token(query)
        return LogicParser.parse_tokens(initial_token, depth=depth)

    @staticmethod
    def parse_tokens(*tokens: Token, depth: int = 0) -> LogicElement:
        if len(tokens) == 1:
            tokens = tuple(Tokenizer.tokenize(tokens[0]))

        # logic operators
        for operator in LOGIC_BINARY_OPERATORS:
            # iterate tokens and match symbol
            for i in range(1, len(tokens) + 1):
                if tokens[-i].lower() in operator.symbols():
                    # return the operator
                    # with left part of tokens and right part of tokens
                    return operator(
                        LogicParser.parse_tokens(*tokens[:-i], depth=depth + 1),
                        LogicParser.parse_tokens(*tokens[-i + 1:], depth=depth + 1)
                    )

        # not
        if tokens[0] in LOGIC_NOT.symbols():
            return LOGIC_NOT(
                LogicParser.parse_tokens(*tokens[1:], depth=depth + 1)
            )

        # ArgList
        return LogicOperand(*tokens)
