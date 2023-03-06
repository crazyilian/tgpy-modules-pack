"""
    description: generate random from expanded string (e.g. rand("{1..100}") -> random
      int from 1 to 100)
    name: rand
    needs:
      dot: 0.1.0
      expand: 0.0.0
    needs_pip: {}
    once: false
    origin: https://github.com/crazyilian/tgpy-modules/blob/main/modules/rand.py
    priority: 23
    version: 0.0.0
    wants: {}
"""
import random


@dot('rand')
def rand(s=''):
    return random.choice(expand(s))
