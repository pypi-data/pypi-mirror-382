from .ParserError import DCParserError
from .elements import *
from .tokenizer import *


class DCParser:
    @staticmethod
    def parse_query(query: str) -> DC_SET:
        # create initial token set
        initial_token = Token(query)
        tokens = tuple(Tokenizer.tokenize(initial_token))

        # split at |
        for i, token in enumerate(tokens):
            if token in DC_SET.symbols():
                return DC_SET(
                    DCParser.parse_projection(*tokens[:i]),
                    DCParser.parse_condition(*tokens[i + 1:])
                )

        # raise exception if query is not in the correct format
        raise DCParserError('The expression shall be of the format "{ x1, ..., xn | f(x1, ..., xn) }".', 0)

    @staticmethod
    def parse_projection(*tokens: Token, depth: int = 0) -> LogicOperand:
        if len(tokens) == 1:
            tokens = tuple(Tokenizer.tokenize(tokens[0]))

        return LogicOperand(*tokens)

    @staticmethod
    def parse_condition(*tokens: Token, depth: int = 0) -> LogicElement:
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
                        DCParser.parse_condition(*tokens[:-i], depth=depth + 1),
                        DCParser.parse_condition(*tokens[-i + 1:], depth=depth + 1)
                    )

        # not
        if tokens[0] in LOGIC_NOT.symbols():
            return LOGIC_NOT(
                DCParser.parse_condition(*tokens[1:])
            )

        # operand
        if len(tokens) == 1:
            return LogicOperand(*tokens)
        elif len(tokens) == 2:
            return DCOperand(
                tokens[0],
                tuple(Tokenizer.tokenize(tokens[1])),
                depth=depth + 1
            )
        else:
            return DCOperand(
                tokens[0],
                tokens[1:],
                depth=depth + 1
            )
