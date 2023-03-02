"""
    description: ''
    name: sh_macro
    needs: {}
    needs_pip: []
    once: false
    origin: https://t.me/tgpy_flood/24320
    priority: 31
    version: 0.0.0
    wants: {}
"""


@add_macro("sh")
def sh_macro(code):
    import os
    import subprocess
    proc = subprocess.run([os.getenv("SHELL") or "/bin/sh", "-c", code], encoding="utf-8", stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    return proc.stdout + (f"\n\nReturn code: {proc.returncode}" if proc.returncode != 0 else "")


__all__ = []
