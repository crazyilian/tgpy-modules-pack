"""
    description: ''
    name: dunder_fix
    needs: {}
    needs_pip: {}
    once: false
    origin: https://t.me/tgpy_flood/26781
    priority: 33
    version: 0.0.0
    wants: {}
"""
from telethon.tl.types import MessageEntityItalic

async def dunder_hook(msg, _):
    edited = False
    ents = []
    for ent in sorted(msg.entities or [], key=lambda x: -x.offset):
        if isinstance(ent, MessageEntityItalic):
            edited = True
            msg.raw_text = msg.raw_text[:ent.offset] + '__' + msg.raw_text[ent.offset:ent.offset + ent.length] + '__' + msg.raw_text[ent.offset + ent.length:]
        else:
            ents.append(ent)
    if edited:
        msg.entities = ents

import tgpy.api
tgpy.api.exec_hooks.add('dunder_fix', dunder_hook)

__all__ = []
