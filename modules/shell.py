"""
    name: shell
    once: false
    origin: tgpy://module/shell
    priority: 1674423858.862349
    save_locals: true
"""
import os
import subprocess


async def run_shell(code):
    proc = await asyncio.create_subprocess_shell(
        code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    return stdout.decode(), proc.returncode



@dot  # dot module
async def sh(code):
    text, returncode = await run_shell(code)
    return text + (f"\n\nReturn code: {returncode}" if returncode != 0 else "")

