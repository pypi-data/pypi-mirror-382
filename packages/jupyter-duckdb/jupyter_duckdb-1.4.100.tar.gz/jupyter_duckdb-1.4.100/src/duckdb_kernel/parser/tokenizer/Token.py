from typing import Optional
from uuid import uuid4


class Token(str):
    def __new__(cls, value: str, constant: 'Token' = None):
        while True:
            # strip whitespaces
            value = value.strip()

            # return if too few characters are left
            if len(value) < 2:
                break

            # remove enclosing brackets
            for cs, ce in (
                    ('(', ')'),
                    ('[', ']'),
                    ('{', '}')
            ):
                if value[0] != cs:
                    continue

                counter = 0
                for i in range(len(value)):
                    if value[i] == cs:
                        counter += 1
                    elif value[i] == ce:
                        counter -= 1

                    if counter == 0:
                        if i == len(value) - 1:
                            value = value[1:-1]

                        break

            else:
                break

        return super().__new__(cls, value)

    def __init__(self, value: str, constant: 'Token' = None):
        self.constant: Optional[Token] = constant

    @staticmethod
    def random(constant: 'Token' = None) -> 'Token':
        return Token('__' + str(uuid4()).replace('-', '_'), constant)

    @property
    def empty(self) -> bool:
        return len(self) == 0

    @property
    def is_temporary(self) -> bool:
        return self.startswith('__')

    @property
    def is_constant(self) -> bool:
        return ((self[0] == '"' and self[-1] == '"') or
                (self[0] == "'" and self[-1] == "'") or
                self.replace('.', '', 1).isnumeric())

    @property
    def no_quotes(self) -> str:
        quotes = ('"', "'")

        if self[0] in quotes and self[-1] in quotes:
            return self[1:-1]
        if self[0] in quotes:
            return self[1:]
        if self[-1] in quotes:
            return self[:-1]
        else:
            return self

    @property
    def single_quotes(self) -> str:
        # TODO Is this comparison useless because tokens are cleaned automatically?
        # TODO quotes are not automatically removed from now on
        if self[0] != '"' or self[-1] != '"':
            return self
        else:
            return f"'{self[1:-1]}'"

    def __getitem__(self, item) -> 'Token':
        return Token(super().__getitem__(item))
