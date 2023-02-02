"""
    name: cpp
    once: false
    origin: tgpy://module/cpp
    priority: 1674431882.643803
    save_locals: true
"""
import asyncio

async def cpp_cmd(cmd):
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


def cpp_trans(cmd):
    if cmd.lower().startswith(".cpp ") or cmd.lower().startswith(".cpp\n"):
        return f"await cpp_cmd({repr(cmd[5:])})"
    return cmd


tgpy.add_code_transformer("cpp_cmd", cpp_trans)
