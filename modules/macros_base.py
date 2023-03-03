"""
    description: ''
    name: macros_base
    needs: {}
    needs_pip: {}
    once: false
    origin: https://t.me/tgpy_flood/24317
    priority: 6
    version: 0.0.0
    wants: {}
"""
import regex

macros = {}

def add_macro(name):
    def macro_adder(f):
        macros[name] = f
    return macro_adder

macro_re = regex.compile(r"(\w+)!(\(([^()]*(?2)?[^()]*)\))")

def applier(match):
    try:
        return macros[match.group(1)](apply_macros(match.group(3)))
    except:
        return match.group(0)

def apply_macros(txt):
    return regex.sub(macro_re, applier, txt)

__all__ = ["add_macro", "apply_macros"]
