"""
    description: executes python code in py! macros
    name: py_macro
    needs:
      macros_base: 0.0.0
    needs_pip:
      unsync: unsync
    once: false
    origin: https://t.me/tgpy_flood/28781
    priority: 7
    version: 0.1.1
    wants: {}
"""
import asyncio
from unsync import unsync
import tgpy.api

@unsync
async def py_macro_applier(code):
    return tgpy.api.tgpy_eval(code).await.result

@add_macro("py")
def py_macro(code):
    return str(py_macro_applier(code).result())

__all__ = []
