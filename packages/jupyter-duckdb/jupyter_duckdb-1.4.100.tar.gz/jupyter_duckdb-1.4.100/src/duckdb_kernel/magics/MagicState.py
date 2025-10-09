from typing import Union, Dict, Optional

from ..db import Connection


class MagicState:
    def __init__(self, db: Connection, code: str, max_rows: Optional[int]):
        self.db: Connection = db
        self.code: Union[str, Dict] = code
        self.max_rows: Optional[int] = max_rows
        self.column_name_mapping: Dict[str, str] = {}
