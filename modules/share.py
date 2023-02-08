"""
    name: share
    once: false
    origin: tgpy://module/share
    priority: 101
    save_locals: true
"""
from telethon.tl.types import MessageEntityCode
import base65536
import gzip
import inspect

def encode_code(code):
    if len(code) > 4096:
        return "b65536:" + base65536.encode(gzip.compress(code.encode()))
    else:
        return code

async def send_code(code):
    code = code.strip("\n")
    await ctx.msg.respond(code, formatting_entities=[MessageEntityCode(0, len(code))])

async def share_module(name):
    code = modules[name].code
    assert code.startswith('"""')
    _, header, code = code.split('"""', 2)
    await send_code('"""' + header + '"""\n' + encode_code(code))

async def share_fn(func):
    await send_code(inspect.getsource(func))
