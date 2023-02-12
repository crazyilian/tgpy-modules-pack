"""
    name: qalc
    once: false
    origin: tgpy://module/qalc
    priority: 1676220994.567941
    save_locals: true
"""
@dot_transformer  # dot module
def qalc(text):
    return f'.sh qalc "{text}"'
