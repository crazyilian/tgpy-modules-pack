"""
    name: shell
    once: false
    origin: tgpy://module/shell
    priority: 1674423858.862349
    save_locals: true
"""
import os
import subprocess


@dot  # dot module
async def sh(code):
    proc = await asyncio.create_subprocess_shell(
        code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    return stdout.decode() + (f"\n\nReturn code: {proc.returncode}" if proc.returncode != 0 else "")
