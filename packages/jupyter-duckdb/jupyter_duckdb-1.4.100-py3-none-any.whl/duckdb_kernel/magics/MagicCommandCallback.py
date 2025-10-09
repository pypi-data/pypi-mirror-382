from typing import Optional, List

from . import MagicCommand, MagicState


class MagicCommandCallback:
    def __init__(self, mc: MagicCommand, silent: bool, state: MagicState, *args, **kwargs):
        self._mc: MagicCommand = mc
        self._silent: bool = silent
        self._state: MagicState = state
        self._args = args
        self._kwargs = kwargs

    @property
    def magic(self) -> MagicCommand:
        return self._mc

    def __call__(self, columns: Optional[List[str]] = None, rows: Optional[List[List]] = None):
        if self._mc.requires_code:
            self._mc(self._silent, self._state, *self._args, **self._kwargs)
        elif self._mc.requires_query_result:
            self._mc(self._silent, self._state, columns, rows, *self._args, **self._kwargs)
        else:
            self._mc(self._silent, self._state, *self._args, **self._kwargs)
