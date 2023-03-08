"""
    description: ''
    name: expand
    needs: {}
    needs_pip: {}
    once: false
    origin: https://t.me/tgpy_flood/392
    priority: 20
    version: 0.0.0
    wants: {}
"""
import subprocess

def expand(s):
    stdout = subprocess.run(["bash", "-c", f"printf '%s\n' {s}"], capture_output=True, check=True, encoding="utf-8").stdout
    return stdout.splitlines()
