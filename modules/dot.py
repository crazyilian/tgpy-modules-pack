"""
    name: dot
    once: false
    origin: tgpy://module/dot
    priority: 11
    save_locals: true
"""

import re

from collections.abc import Awaitable
from typing import Callable, Optional, Union

# tgpy.add_code_transformer = lambda name, func: tgpy.code_transformers.insert(-1, (name, func))

DotHandler = Union[Callable[[str], Awaitable[None]], Callable[[str], None]]
Transformer = Callable[[str], str]

DOT_HANDLERS: dict[str, DotHandler] = {}


def prefix_from_func(func: Callable) -> str:
    """Extract prefix name from function."""
    return func.__name__.removeprefix('_').replace('_', '-')


def strip_docstring(code: str) -> str:
    """Strip docstring from start of a code."""
    return re.sub('^"""("{0,2}[^"])*"""\n*', '', code)


def strip_dot_prefix(prefix: str, text: str) -> Optional[str]:
    """Return string without dot-prefix or None if no dot-prefix."""
    offset = len(prefix) + 1

    if text[:offset] == f'.{prefix}' and text[offset:offset + 1] in (' ', '\n', ''):
        return text[offset + 1:]
    else:
        return None


def dot_transformer(func: Transformer) -> Transformer:
    """Add transformer for code that starts with some prefix."""
    prefix = func.__name__.replace('_', '-')

    def wrapper(code: str) -> str:
        dot_text = strip_dot_prefix(prefix, strip_docstring(code))

        if dot_text is not None:
            return func(dot_text)
        else:
            return code

    tgpy.add_code_transformer(f'dot-transformer-{prefix}', wrapper)

    return func


def dot(func: DotHandler) -> DotHandler:
    """Run some handler on code that starts with some prefix."""
    prefix = func.__name__.replace('_', '-')

    DOT_HANDLERS[prefix] = func

    def wrapper(code: str) -> str:
        dot_text = strip_dot_prefix(prefix, strip_docstring(code))
        if dot_text is not None:
            return f'await try_await(DOT_HANDLERS[{repr(prefix)}]({repr(dot_text)}))'
        else:
            return code

    tgpy.add_code_transformer(f'dot-handler-{prefix}', wrapper)

    return func
