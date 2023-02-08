"""
    name: dot_msg_handler
    once: false
    origin: tgpy://module/dot_msg_handler
    priority: 12
    save_locals: true
"""

from collections.abc import Awaitable
from typing import Callable, List, Union
import telethon

DotMsgHandler = Union[Callable[[telethon.types.Message], Awaitable[None]], Callable[[telethon.types.Message], None]]

DOT_MSG_HANDLER_PREFIXES: List[str] = []


def dot_msg_handler(func: DotMsgHandler) -> DotMsgHandler:
    """Run some handler on code that starts with some prefix."""
    prefix = func.__name__.replace('_', '-')
    DOT_MSG_HANDLER_PREFIXES.append(prefix)

    @client.on(telethon.events.NewMessage(outgoing=True))
    @client.on(telethon.events.MessageEdited(outgoing=True))
    async def wrapper(msg: telethon.types.Message) -> None:
        dot_text = strip_dot_prefix(prefix, strip_docstring(msg.text))
        if dot_text is not None:
            await try_await(func(msg))

    return func


def clear_dot_caller_code(code: str) -> str:
    for prefix in DOT_MSG_HANDLER_PREFIXES:
        dot_text = strip_dot_prefix(prefix, strip_docstring(code))
        if dot_text is not None:
            return ''
    return code


tgpy.add_code_transformer(f'clear-dot-caller-code', clear_dot_caller_code)
