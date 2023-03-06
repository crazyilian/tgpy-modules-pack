"""
    description: ''
    name: commit_modules
    needs:
      shell: 0.2.0
    needs_pip: {}
    once: false
    origin: https://t.me/c/1796785408/3026
    priority: 36
    version: 0.0.0
    wants: {}
"""
def commit_modules():
    return shell("""
cd tgpy-modules-pack
git pull
git add .
git commit -m "`date`"
git push
""")
