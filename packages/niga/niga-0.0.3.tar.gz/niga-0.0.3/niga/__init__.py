from typing import Iterable


def replace_in_sequence(initial_str: str, replace_args: Iterable[str | Iterable[str]]) -> str:
    # replace_args should be an Iterable such that " ''.replace(o, n) for o, n in replace_args " is valid
    return exhaust_iterable((initial_str := initial_str.replace(o, n)) for o, n in replace_args) or initial_str


def exhaust_iterable(__i: Iterable) -> None:
    for _ in __i:
        pass



