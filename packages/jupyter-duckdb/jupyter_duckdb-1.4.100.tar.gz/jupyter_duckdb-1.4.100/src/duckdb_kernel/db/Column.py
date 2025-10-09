import re

from .Table import Table


class Column:
    def __init__(self, table: Table, name: str, data_type: str, null: bool):
        self.table: Table = table
        self.name: str = name
        self.data_type: str = data_type
        self.null: bool = null

    def __hash__(self):
        return self.name.__hash__()

    @property
    def id(self) -> str:
        name = re.sub(r'[^A-Za-z]', '_', self.name)
        return f'{self.table.id}_column_{name}'

    def copy(self) -> 'Column':
        return Column(self.table, self.name, self.data_type)
