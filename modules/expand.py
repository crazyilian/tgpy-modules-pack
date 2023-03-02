"""
    name: expand
    needs:
      shell: 0.0.0
    once: false
    origin: tgpy://module/expand
    priority: 7
    save_locals: true
    description: expand strings via bash printf (e.g. "{1..3}" -> ['1', '2', '3'])
"""
def expand(s):
    stdout = run_sync_shell(["bash", "-c", f"printf '%s\n' {s}"])[0]
    return stdout.splitlines()
