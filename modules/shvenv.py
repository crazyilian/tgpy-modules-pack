"""
    description: run and use shell with activated tgpy virtualenv via .shvenv
    name: shvenv
    needs:
      dot: 0.1.0
      shell: 0.1.0
    needs_pip: {}
    once: false
    origin: https://raw.githubusercontent.com/crazyilian/tgpy-modules/main/modules-src/shvenv.py
    priority: 32
    version: 0.1.0
    wants: {}
"""
import sys


def in_virtualenv():
    return (getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None)) != sys.prefix


@dot('shvenv')
async def shvenv(code=''):
    if not in_virtualenv():
        return "No virtualenv found"
    text, returncode = await run_shell(f'export PATH="{sys.prefix}/bin:$PATH" ; {code}')
    return text + (f"\n\nReturn code: {returncode}" if returncode != 0 else "")