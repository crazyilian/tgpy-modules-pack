"""
    description: decorator dot to make function usable through .{prx}, but run it as hook
    name: dot_hook
    needs:
      try_await: 0.0.0
    needs_pip: []
    once: false
    origin: https://raw.githubusercontent.com/crazyilian/tgpy-modules/main/modules-src/dot_hook.py
    priority: 28
    version: 0.0.0
    wants: {}
"""
import tgpy.api


def dot_hook(prx, prevent=True):
    """decorator to make function usable through .{prx}, but run it as hook"""

    def prx_decorator(f):
        async def prx_hook(message, is_edit):
            txt = message.raw_text
            if txt.lower().startswith(f".{prx} ") or txt.lower().startswith(f".{prx}\n"):
                txt = txt[len(prx) + 2:]
                res = await try_await(f(txt, message=message, is_edit=is_edit))
            elif txt.lower() == f".{prx}":
                res = await try_await(f(message=message, is_edit=is_edit))
            else:
                return True

            if prevent:
                return False
            return res

        tgpy.api.exec_hooks.add(prx, prx_hook)
        return f

    return prx_decorator
