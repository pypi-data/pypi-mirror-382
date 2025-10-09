import re
from typing import Optional, List, Iterator

from .Token import Token


class Tokenizer:
    @staticmethod
    def tokenize(query: Token) -> Iterator[Token]:
        stack = Tokenizer()
        index, start = 0, 0
        at_start = True

        query_len = len(query)
        while index < query_len:
            offset = stack(query[index], at_start)
            at_start = False

            if offset >= 0:
                token = query[start:index + 1 - offset]
                if not token.empty:
                    yield token

                index -= offset
                start = index + 1
                at_start = True

            index += 1

        if start <= index:
            token = query[start:index + 1]
            if not token.empty:
                yield token

    def __init__(self):
        self.stack: List[str] = []
        self.escape: bool = False
        self.special_characters: int = 0
        self.special_character_re: re.Pattern = re.compile(r'''[^A-Za-zÄÖÜäöüß0-9_()\[\]{}"'.]''')

    @property
    def last_character(self) -> Optional[str]:
        if len(self.stack) > 0:
            return self.stack[-1]

    @property
    def in_single_quotes(self) -> bool:
        return self.last_character == "'"

    @property
    def in_double_quotes(self) -> bool:
        return self.last_character == '"'

    @property
    def in_quotes(self) -> bool:
        return self.in_single_quotes or self.in_double_quotes

    @property
    def in_parentheses(self) -> bool:
        return '(' in self.stack

    @property
    def in_squares(self) -> bool:
        return '[' in self.stack

    @property
    def in_braces(self) -> bool:
        return '{' in self.stack

    @property
    def in_brackets(self) -> bool:
        return self.in_parentheses or self.in_squares or self.in_braces

    def __call__(self, character: Token, at_start: bool) -> int:
        # abort if last character was an escape character
        if self.escape:
            self.escape = False
            return -1

        # escape characters
        if not self.in_quotes and not self.in_brackets and character == '\\':
            self.escape = True
            self.special_characters = 0
            return 1

        # collect special characters
        if not self.in_quotes and not self.in_brackets and self.special_characters:
            if not self.special_character_re.fullmatch(character):
                self.special_characters = 0
                return 1
            else:
                self.special_characters += 1
                return -1

        # single quotes
        if not self.in_double_quotes and not self.in_brackets and character == "'":
            if self.in_single_quotes:
                self.stack.pop()
                return 0
            else:
                self.stack.append(character)
                return -1

        # double quotes
        if not self.in_single_quotes and not self.in_brackets and character == '"':
            if self.in_double_quotes:
                self.stack.pop()
                return 0
            else:
                self.stack.append(character)
                return -1

        # brackets
        if not self.in_quotes and not self.in_squares and not self.in_braces:
            if character == '(':
                if self.in_parentheses or at_start:
                    self.stack.append(character)
                    return -1
                else:
                    return 1

            elif character == ')':
                if self.last_character == '(':
                    self.stack.pop()
                    return 0 if not self.in_parentheses else -1

                raise ValueError

        if not self.in_quotes and not self.in_parentheses and not self.in_braces:
            if character == '[':
                if self.in_squares or at_start:
                    self.stack.append(character)
                    return -1
                else:
                    return 1

            elif character == ']':
                if self.last_character == '[':
                    self.stack.pop()
                    return 0 if not self.in_squares else -1

                raise ValueError

        if not self.in_quotes and not self.in_parentheses and not self.in_squares:
            if character == '{':
                if self.in_braces or at_start:
                    self.stack.append(character)
                    return -1
                else:
                    return 1

            elif character == '}':
                if self.last_character == '{':
                    self.stack.pop()
                    return 0 if not self.in_braces else -1

                raise ValueError

        # whitespaces
        if not self.in_quotes and not self.in_brackets and character.empty:
            return 0

        # special characters that break tokens
        if not self.in_quotes and not self.in_brackets and self.special_character_re.fullmatch(character):
            self.special_characters = 1
            return 1

        return -1
