"""
    name: rand
    once: false
    origin: tgpy://module/rand
    priority: 1674424117.367438
    save_locals: true
"""
import random


@dot
def rand(s):
    return random.choice(expand(s))

# def rand_trans(text):
#     if text.startswith(".rand "):
#         return f"rand({repr(text[6:])})"
#     return text
#
# tgpy.add_code_transformer("rand", rand_trans)
