from .LogicParser import LogicParser
from .ParserError import RAParserError
from .elements import *
from .tokenizer import *


# Instead of multiple nested loops, a tree with rotation can
# probably be used with less time complexity.

class RAParser:
    @staticmethod
    def parse_query(query: str) -> RAElement:
        initial_token = Token(query)
        return RAParser.parse_tokens(initial_token, depth=0)

    @staticmethod
    def parse_tokens(*tokens: Token, target: RAOperator | RAOperand = None, depth: int = 0) -> RAElement:
        if len(tokens) == 1:
            tokens = tuple(Tokenizer.tokenize(tokens[0]))

        # binary operators
        for operator_symbols in RA_BINARY_SYMBOLS:
            # iterate tokens and match symbol
            for i in range(1, len(tokens) + 1):
                lower_token = tokens[-i].lower()

                if lower_token in operator_symbols:
                    operator = operator_symbols[lower_token]

                    # raise error if left or right operand missing
                    if i == 1:
                        raise RAParserError(f'right operand missing after {tokens[-i]}', depth)
                    if i == len(tokens):
                        raise RAParserError(f'left operand missing before {tokens[-i]}', depth)

                    # return the operator
                    # with left part of tokens and right part of tokens
                    return operator(
                        RAParser.parse_tokens(*tokens[:-i], depth=depth + 1),
                        RAParser.parse_tokens(*tokens[-i + 1:], depth=depth + 1)
                    )

        # unary operators
        for i in range(1, len(tokens) + 1):
            # iterate operators and match token
            for operator in RA_UNARY_OPERATORS:
                if tokens[-i].lower() in operator.symbols():
                    # If no target from a previous step is handed over
                    # the last token is the operators target.
                    if target is None:
                        op = operator(
                            RAParser.parse_tokens(tokens[-1], depth=depth + 1),
                            LogicParser.parse_tokens(*tokens[-i + 1:-1], depth=depth + 1)
                        )

                    # Otherwise the handed target is this operator's
                    # target.
                    else:
                        op = operator(
                            target,
                            LogicParser.parse_tokens(*tokens[-i + 1:], depth=depth + 1)
                        )

                    # If there are any more tokens the operator is
                    # the target for the next step.
                    if i < len(tokens):
                        return RAParser.parse_tokens(*tokens[:-i], target=op, depth=depth + 1)

                    # Otherwise the operator is the return value.
                    else:
                        return op

        # return as name
        if len(tokens) > 1:
            raise RAParserError(f'{tokens=}', depth)

        return RAOperand(tokens[0])
