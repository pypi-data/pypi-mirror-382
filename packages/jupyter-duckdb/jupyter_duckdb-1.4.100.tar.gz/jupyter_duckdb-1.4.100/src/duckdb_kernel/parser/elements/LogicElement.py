from typing import Iterator

from ..util.RenamableColumnList import RenamableColumnList


class LogicElement:
    order = 0

    def __str__(self) -> str:
        raise NotImplementedError

    def to_sql(self, cols: RenamableColumnList) -> str:
        raise NotImplementedError
