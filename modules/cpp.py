"""
    description: 'run cpp code'
    name: cpp
    needs:
      dot: 0.1.0
    needs_pip: []
    once: false
    origin: tgpy://module/cpp
    priority: 13
    save_locals: true
    version: 0.0.0
    wants: {}
"""
import asyncio
import subprocess


@dot('cpp')
async def cpp(cmd=''):
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
