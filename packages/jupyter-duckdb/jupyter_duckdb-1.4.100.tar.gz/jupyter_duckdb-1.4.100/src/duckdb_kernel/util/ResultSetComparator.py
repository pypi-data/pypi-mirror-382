from datetime import date
from typing import Tuple, List, Optional


class ResultSetComparator:
    def __init__(self, left: List[Tuple | List], right: List[Tuple | List]):
        self._left: List[Tuple] = [tuple(t) for t in left]
        self._right: List[Tuple] = [tuple(t) for t in right]

    @property
    def left_only(self) -> List[Tuple]:
        return self.__only(self._left, self._right)

    @property
    def right_only(self) -> List[Tuple]:
        return self.__only(self._right, self._left)

    @staticmethod
    def __only(left: List[Tuple], right: List[Tuple]) -> List[Tuple]:
        right = right.copy()
        result = []

        for row in left:
            right_index = ResultSetComparator._row_in(right, row)

            if right_index is not None:
                del right[right_index]
            else:
                result.append(row)

        return result

    @property
    def ordered_left_only(self) -> List[Tuple]:
        return self.__ordered_only(self._left, self._right)

    @property
    def ordered_right_only(self) -> List[Tuple]:
        return self.__ordered_only(self._right, self._left)

    @staticmethod
    def __ordered_only(left: List[Tuple], right: List[Tuple]) -> List[Tuple]:
        result = []
        i = 0

        for row in left:
            position = ResultSetComparator._row_in(right[i:], row)
            if position is not None:
                i += position + 1
            else:
                result.append(row)

        return result

    @staticmethod
    def _row_in(rows: List[Tuple], row: Tuple) -> Optional[int]:
        for i, sr in enumerate(rows):
            if ResultSetComparator._rows_equal(sr, row):
                return i

        return None

    @staticmethod
    def _rows_equal(left: Tuple, right: Tuple) -> bool:
        if len(left) != len(right):
            return False

        for le, re in zip(left, right):
            if isinstance(le, float) or isinstance(re, float):
                if abs(le - re) > 1e-6:
                    return False
            elif isinstance(le, date) or isinstance(re, date):
                if str(le) != str(re):
                    return False
            elif le != re:
                return False

        return True
