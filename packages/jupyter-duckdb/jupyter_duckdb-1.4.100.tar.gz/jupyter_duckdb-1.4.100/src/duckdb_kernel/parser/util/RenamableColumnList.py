from typing import Iterable, Iterator, Tuple, Dict, List

from duckdb_kernel.db import Column
from .RenamableColumn import RenamableColumn


class RenamableColumnList(list[RenamableColumn]):
    def __init__(self, *source: Iterable[RenamableColumn]):
        super().__init__((e for s in source for e in s))

    @staticmethod
    def from_iter(source: Iterable[Column]) -> 'RenamableColumnList':
        return RenamableColumnList(RenamableColumn(c) for c in source)

    @property
    def list(self) -> str:
        return ', '.join(c.current_name for c in self)

    def filter(self, *name: str) -> 'RenamableColumnList':
        result = []

        for n in name:
            r = [c for c in self if c.matches(n)]
            if len(r) == 0:
                raise AssertionError(f'unknown attribute {n}')
            if len(r) > 1:
                raise AssertionError(f'ambiguous attribute {n}')

            result.append(r)

        return RenamableColumnList(*result)

    def rename(self, source: str, target: str):
        for col in self:
            if col.matches(source):
                col.name = target
                return

        raise AssertionError(f'unknown attribute {source}')

    def map_args(self, args: Iterator[str]) -> Iterator[str]:
        for arg in args:
            for col in self:
                if col.matches(arg):
                    yield col.current_name
                    break
            else:
                yield arg

    def merge(self, other: 'RenamableColumnList') -> 'RenamableColumnList':
        cols: Dict[str, RenamableColumn] = {}

        for col in self:
            cols[col.full_name] = col

        for col in other:
            if col.full_name in cols:
                raise AssertionError(f'column {col.full_name} present in both relations')

            cols[col.full_name] = col

        return RenamableColumnList(cols.values())

    def difference(self, other: 'RenamableColumnList') -> 'RenamableColumnList':
        cols: Dict[str, RenamableColumn] = {}

        for col in self:
            cols[col.name] = col

        for col in other:
            if col.name in cols:
                del cols[col.name]

        return RenamableColumnList(cols.values())

    def intersect(self, other: 'RenamableColumnList', prefer_right: bool = False) \
            -> Tuple[List[Tuple[RenamableColumn, RenamableColumn]], 'RenamableColumnList']:
        self_cols: Dict[str, RenamableColumn] = {col.name: col for col in self}
        other_cols: Dict[str, RenamableColumn] = {col.name: col for col in other}

        replacements: Dict[RenamableColumn, RenamableColumn] = {}
        intersection: List[Tuple[RenamableColumn, RenamableColumn]] = []

        for name in tuple(self_cols.keys()):
            if name in other_cols:
                if prefer_right:
                    replacements[self_cols[name]] = other_cols[name]

                intersection.append((self_cols[name], other_cols[name]))
                del other_cols[name]

        # if len(intersection) == 0:
        #     raise AssertionError('no common attributes found for join')

        return intersection, RenamableColumnList(
            (replacements.get(x, x) for x in self_cols.values()),
            other_cols.values()
        )
