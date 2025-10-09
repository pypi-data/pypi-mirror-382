_delimiters = ('"', "'")


def strip_delimiters(value: str):
    while True:
        value = value.strip()

        if len(value) == 0:
            return value

        if value[0] != value[-1] or value[0] not in _delimiters:
            return value

        value = value[1:-1]
