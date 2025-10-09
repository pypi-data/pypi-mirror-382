from typing import Tuple

from . import Column
from . import Table


class Constraint:
    def __init__(self, index: int, table: Table, columns: Tuple['Column', ...]):
        self.index: int = index
        self.table: Table = table
        self.columns: Tuple['Column', ...] = columns
