"""
    description: handler of macros
    name: macros_handler
    needs:
      macros_base: 0.0.0
    needs_pip: []
    once: false
    origin: https://t.me/tgpy_flood/26233
    priority: 28
    version: 0.1.0
    wants: {}
"""
import tgpy.api

async def macros_handler(msg, _):
    text = apply_macros(msg.text)
    if text != msg.text:
        return await msg.edit(text)

tgpy.api.exec_hooks.add("macros_handler", macros_handler)

__all__ = []
