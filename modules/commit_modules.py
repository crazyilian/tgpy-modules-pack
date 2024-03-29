"""
    description: ''
    name: commit_modules
    needs:
      shell: 0.2.0
    needs_pip: {}
    once: false
    origin: https://t.me/c/1796785408/3593
    priority: 33
    version: 0.1.3
    wants: {}
"""
from tgpy.api import config


def save_registry():
    reg = '"""\n    sources:\n' + \
          "\n".join([f'        {name}: {repr(source)}' for name, source in config.get("registry").items()]) + \
          '\n"""'
    with open('tgpy-modules-pack/registry.txt', 'w') as f:
        f.write(reg)


async def commit_modules():
    return await shell("""
cd tgpy-modules-pack
git pull
git add .
git commit -m "`date`"
git push
""")
