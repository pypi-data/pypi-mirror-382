from typing import Iterator

from .RAElement import RAElement
from .RAOperator import RAOperator


class RABinaryOperator(RAOperator):
    def __init__(self, left: RAElement, right: RAElement):
        self.left: RAElement = left
        self.right: RAElement = right

    def __str__(self, indent: int = 0) -> str:
        return f'{super().__str__(indent)}\n{self.left.__str__(indent + 1)}\n{self.right.__str__(indent + 1)}'

    @property
    def children(self) -> Iterator[RAElement]:
        yield self.left
        yield self.right
