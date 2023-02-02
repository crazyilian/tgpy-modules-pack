"""
    name: shell
    once: false
    origin: tgpy://module/shell
    priority: 1674423858.862349
    save_locals: true
"""
import os
import subprocess

def shell(code):
    proc = subprocess.run([os.getenv("SHELL") or "/bin/sh", "-c", code], encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.stdout + (f"\n\nReturn code: {proc.returncode}" if proc.returncode != 0 else "")

def sh_trans(cmd):
    if cmd.lower().startswith(".sh "):
        return f"shell({repr(cmd[4:])})"
    return cmd

tgpy.add_code_transformer("shell", sh_trans)
