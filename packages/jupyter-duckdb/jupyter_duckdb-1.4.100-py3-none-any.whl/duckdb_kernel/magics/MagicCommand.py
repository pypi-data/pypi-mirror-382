from typing import Any, List, Tuple, Callable, Dict, Set


class MagicCommand:
    _ARG = '''([^ ]+?|'.+?'|".+?")?'''

    def __init__(self, *names: str):
        self._names: Tuple[str, ...] = names

        self._arguments: List[Tuple[str, Any, str]] = []
        self._flags: List[Tuple[str, str]] = []
        self._optionals: List[Tuple[str, Any, str]] = []
        self._disables: Set[str] = set()
        self._code: bool = False
        self._result: bool = False
        self._default: bool = False

        self._on: List[Callable] = []

    @property
    def names(self) -> Tuple[str, ...]:
        return self._names

    @property
    def args(self) -> List[Tuple[str, Any, str]]:
        return self._arguments

    @property
    def flags(self) -> List[Tuple[str, str]]:
        return self._flags

    @property
    def optionals(self) -> List[Tuple[str, Any, str]]:
        return self._optionals

    @property
    def disables(self) -> Set[str]:
        return self._disables

    @property
    def requires_code(self) -> bool:
        return self._code

    @property
    def requires_query_result(self) -> bool:
        return self._result

    @property
    def is_default(self) -> bool:
        return self._default

    def arg(self, name: str, default_value: Any = None, description: str = None) -> 'MagicCommand':
        if len(self._arguments) > 0:
            ln, ldv, _ = self._arguments[-1]
            if ldv is not None and default_value is None:
                raise ValueError(f'argument {name} without default value registered after argument {ln} with default value {ldv}')

        self._arguments.append((name, default_value, description))
        return self

    def opt(self, name: str, default_value: Any = None, description: str = None) -> 'MagicCommand':
        self._optionals.append((name, default_value, description))
        return self

    def flag(self, name: str, description: str = None) -> 'MagicCommand':
        self._flags.append((name, description))
        return self

    def disable(self, *name: str) -> 'MagicCommand':
        for n in name:
            self._disables.add(n)

        return self

    def code(self, code: bool) -> 'MagicCommand':
        self._code = code
        return self

    def result(self, result: bool) -> 'MagicCommand':
        self._result = result
        return self

    def on(self, fun: Callable) -> 'MagicCommand':
        self._on.append(fun)
        return self

    def default(self, default: bool) -> 'MagicCommand':
        self._default = default
        return self

    @property
    def parameters(self) -> str:
        args = ' +'.join([self._ARG] * len(self._arguments))
        flags = ''.join(f'( +({name}))?' for name, *_ in self._flags)
        opts = ''.join(f'( +({name}) +{self._ARG})?' for name, *_ in self._optionals)

        return f'^ *{args}{flags}{opts} *$'

    def __call__(self, silent: bool, *args, **kwargs) -> Dict[str, Any]:
        result = {}

        for fun in self._on:
            r = fun(silent, *args, **kwargs)
            if r is not None:
                for k, v in r.items():
                    result[k] = v

        return result
