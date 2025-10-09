import re
from typing import List, Optional

from . import Column
from . import ForeignKey
from . import Constraint


class Table:
    def __init__(self, name: str):
        self.name: str = name
        self.columns: List[Column] = []
        self.primary_key: Optional[Constraint] = None
        self.unique_keys: List[Constraint] = []
        self.foreign_keys: List[ForeignKey] = []

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.lower()

    @property
    def id(self) -> str:
        name = re.sub(r'[^A-Za-z]', '_', self.name)
        return f'table_{name}'

    @property
    def normalized_name(self) -> str:
        return self.normalize_name(self.name)

    def get_column(self, name: str) -> "Column":
        for column in self.columns:
            if column.name == name:
                return column

        raise AssertionError(f'could not find column {name} in table {self.name}')
