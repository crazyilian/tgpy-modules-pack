"""
    description: ''
    name: pipdep
    needs: {}
    needs_pip: []
    once: false
    origin: https://t.me/tgpy_flood/10012
    priority: 1
    save_locals: true
    version: 0.0.0
    wants: {}
"""
import ast
import importlib
import subprocess
import sys

def install_pip_package(name):
    subprocess.run([sys.executable, "-m", "pip", "install", name], check=True)

dep_names = set()
for module in modules:
    code = modules[module].code
    try:
        mod = ast.parse(code)
    except Exception:
        continue
    for node in ast.walk(mod):
        if isinstance(node, ast.Import):
            for alias in node.names:
                dep_names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            dep_names.add(node.module)

for name in dep_names:
    try:
        importlib.import_module(name)
    except ImportError as e:
        if e.name == name:
            install_pip_package(name)
