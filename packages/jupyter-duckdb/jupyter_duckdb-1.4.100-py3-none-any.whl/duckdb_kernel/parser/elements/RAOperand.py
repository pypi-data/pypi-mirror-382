from typing import Dict, Tuple, Iterator

from duckdb_kernel.db import Table
from .RAElement import RAElement
from ..util.RenamableColumnList import RenamableColumnList


class RAOperand(RAElement):
    def __init__(self, relation: str):
        self.relation: str = relation

    def __str__(self, indent: int = 0) -> str:
        return f'{super().__str__(indent)}: {self.relation}'

    @property
    def name(self) -> str:
        return self.relation

    @property
    def children(self) -> Iterator[RAElement]:
        return
        yield

    def to_sql(self, tables: Dict[str, Table]) -> Tuple[str, RenamableColumnList]:
        table_keys = {key.lower(): key for key in tables}
        relation_lower = self.relation.lower()

        if relation_lower not in table_keys:
            raise AssertionError(f'unknown relation {self.relation}')

        cols = RenamableColumnList.from_iter(tables[table_keys[relation_lower]].columns)
        column_names = ', '.join(c.rename() for c in cols)

        return f'SELECT DISTINCT {column_names} FROM {self.relation}', cols
