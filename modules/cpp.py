"""
    name: cpp
    once: false
    origin: tgpy://module/cpp
    priority: 10001
    save_locals: true
"""
import asyncio
import subprocess


@dot  # dot module
async def cpp(cmd):
    with open("/tmp/tmp.cpp", "w") as out:
        out.write(cmd)

    proc = await asyncio.create_subprocess_exec(
        "g++", "-std=c++20", "/tmp/tmp.cpp", "-o", "/tmp/cpp_res",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    stdout, _ = await proc.communicate()

    if proc.returncode != 0:
        return stdout.decode()

    proc = await asyncio.create_subprocess_exec(
        "/tmp/cpp_res",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    stdout, _ = await proc.communicate()

    return stdout.decode()
