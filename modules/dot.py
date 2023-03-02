"""
    description: decorator dot to make function usable through .{prx}
    name: dot
    needs: {}
    needs_pip: []
    once: false
    origin: https://t.me/tgpy_flood/28421
    priority: 5
    save_locals: true
    version: 0.3.0
    wants: {}
"""
import tgpy.api

DOT_HANDLERS = dict()


def get_dot_handler(prx):
    return DOT_HANDLERS.get(prx, lambda *_: None)


def dot(prx):
    """decorator to make function usable through .{prx}"""

    def prx_decorator(f):
        DOT_HANDLERS[prx] = f

        def prx_trans(txt):
            if txt.lower().startswith(f".{prx} ") or txt.lower().startswith(f".{prx}\n"):
                txt = txt[len(prx) + 2:]
                return f"get_dot_handler({repr(prx)})({repr(txt)})"
            elif txt.lower() == f".{prx}":
                return f"get_dot_handler({repr(prx)})()"
            else:
                return txt

        tgpy.api.code_transformers.add(prx, prx_trans)
        return f

    return prx_decorator


__all__ = ["dot", "get_dot_handler"]
