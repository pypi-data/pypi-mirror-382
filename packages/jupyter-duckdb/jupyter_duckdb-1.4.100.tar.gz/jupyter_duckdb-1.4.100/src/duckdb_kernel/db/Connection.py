from typing import Dict, List, Tuple, Any

from .Table import Table


class Connection:
    def __init__(self, path: str):
        self.path: str = path

    def close(self):
        pass

    def copy(self) -> 'Connection':
        raise NotImplementedError

    @staticmethod
    def plain_explain() -> bool:
        return False

    @staticmethod
    def multiple_statements_per_query() -> bool:
        return True

    def __str__(self) -> str:
        raise NotImplementedError

    def execute(self, query: str) -> Tuple[List[str], List[List[Any]]]:
        raise NotImplementedError

    def analyze(self) -> Dict[str, Table]:
        raise NotImplementedError
