"""
    name: expand
    once: false
    origin: tgpy://module/expand
    priority: 1000
    save_locals: true
"""
import subprocess

def expand(s):
    stdout = subprocess.run(["bash", "-c", f"printf '%s\n' {s}"], capture_output=True, check=True, encoding="utf-8").stdout
    return stdout.splitlines()
