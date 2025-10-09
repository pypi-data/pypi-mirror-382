from typing import Tuple, Iterator

from . import Column
from . import Constraint


class ForeignKey:
    def __init__(self, columns: Tuple['Column', ...], constraint: Constraint):
        self.columns: Tuple['Column', ...] = columns
        self.constraint: Constraint = constraint

    @property
    def references(self) -> Iterator[Tuple['Column', 'Column']]:
        for source, target in zip(self.columns, self.constraint.columns):
            yield source, target
