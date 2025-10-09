from uuid import uuid4

from duckdb_kernel.db import Column


class RenamableColumn(Column):
    def __init__(self, c: Column):
        super().__init__(c.table, c.name, c.data_type, c.null)
        self.current_name: str = c.name

    @property
    def full_name(self) -> str:
        return f'{self.table.name}.{self.name}'

    def matches(self, name: str) -> bool:
        return self.name.lower() == name.lower() or self.full_name.lower() == name.lower()

    def rename(self):
        old_name = self.current_name
        random_name = str(uuid4()).replace('-', '')
        self.current_name = f'__{self.table.name}__{self.name}__{random_name}'

        return f'{old_name} AS {self.current_name}'
