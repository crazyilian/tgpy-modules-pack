"""
    description: generate random from expanded string (e.g. rand("{1..100}") -> random
      int from 1 to 100)
    name: rand
    needs:
      dot: 0.1.0
      expand: 0.0.0
    needs_pip: {}
    once: false
    origin: https://raw.githubusercontent.com/crazyilian/tgpy-modules/main/modules-src/rand.py
    priority: 23
    version: 0.0.0
    wants: {}
"""
import random


@dot('rand')  # dot module
def rand(s=''):
    return random.choice(expand(s))
