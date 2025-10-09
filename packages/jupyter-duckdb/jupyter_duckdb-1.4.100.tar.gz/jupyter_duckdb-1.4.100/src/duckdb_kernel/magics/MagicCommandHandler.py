import re
from typing import Dict, Tuple, List

from . import MagicCommand, MagicCommandException, MagicCommandCallback
from .MagicState import MagicState
from ..db import Connection


class MagicCommandHandler:
    def __init__(self):
        self._magics: Dict[str, MagicCommand] = {}

    def add(self, *command: MagicCommand):
        for cmd in command:
            for key in cmd.names:
                key = key.lower()
                self._magics[key] = cmd

    def __getitem__(self, key: str) -> MagicCommand:
        return self._magics[key.lower()]

    def __call__(self, silent: bool, state: MagicState) \
            -> Tuple[List[MagicCommandCallback], List[MagicCommandCallback]]:
        enabled_callbacks: List[MagicCommandCallback] = []

        # enable commands with default==True
        for magic in self._magics.values():
            if magic.is_default:
                flags = {name: False for name, _ in magic.flags}
                optionals = {name: default for name, default, _ in magic.optionals}
                callback = MagicCommandCallback(magic, silent, state, **flags, **optionals)

                enabled_callbacks.append(callback)

        # search for magic commands in code
        while True:
            # ensure code starts with '%' or '%%' but not with '%%%'
            match = re.match(r'^%{1,2}([^% ]+?)([ \t]*$| .+?$)', state.code, re.MULTILINE | re.IGNORECASE)

            if match is None:
                break

            # remove magic command from code
            start, end = match.span()
            state.code = state.code[:start] + state.code[end + 1:]

            # extract command
            command = match.group(1).lower()

            if command not in self._magics:
                raise MagicCommandException(f'unknown magic command "{command}"')

            magic = self._magics[command]

            # extract parameters
            params = match.group(2)
            match = re.match(magic.parameters, params, re.IGNORECASE)

            if match is None:
                raise MagicCommandException(f'could not parse parameters for command "{command}"')

            # extract args
            args = [group if group is not None else default
                    for group, (_, default, _) in zip(match.groups(), magic.args)]

            args = [arg[1:-1]
                    if arg is not None and (arg[0] == '"' and arg[-1] == '"' or arg[0] == "'" and arg[-1] == "'")
                    else arg
                    for arg in args]

            if any(arg is None for arg in args):
                raise MagicCommandException(f'could not parse parameters for command "{command}"')

            i = len(args) + 1

            # extract flags
            flags = {name: False for name, _ in magic.flags}

            offset = len(args) + 2 * len(magic.flags)
            while i < offset:
                name = match.group(i + 1)
                i += 2

                if name is not None:
                    flags[name.lower()] = True

            # extract optionals
            optionals = {name: default for name, default, _ in magic.optionals}

            offset = len(args) + 2 * len(magic.flags) + 3 * len(magic.optionals)
            while i < offset:
                name = match.group(i + 1)
                value = match.group(i + 2)
                i += 3

                if value is not None and (value[0] == '"' and value[-1] == '"' or value[0] == "'" and value[-1] == "'"):
                    value = value[1:-1]

                if name is not None:
                    optionals[name.lower()] = value

            # add to callbacks
            callback = MagicCommandCallback(magic, silent, state, *args, **flags, **optionals)
            enabled_callbacks.append(callback)

        # disable overwritten callbacks
        callbacks = []
        blacklist = set()

        for callback in reversed(enabled_callbacks):
            for name in callback.magic.names:
                if name in blacklist:
                    break
            else:
                callbacks.append(callback)

                for name in callback.magic.names:
                    blacklist.add(name)
                for disable in callback.magic.disables:
                    blacklist.add(disable)

        # prepare callback lists
        pre_query_callbacks = []
        post_query_callbacks = []

        for callback in reversed(callbacks):
            if not callback.magic.requires_query_result:
                pre_query_callbacks.append(callback)
            else:
                post_query_callbacks.append(callback)

        # return callbacks
        return pre_query_callbacks, post_query_callbacks
