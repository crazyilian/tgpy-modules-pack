"""
    name: rand
    needs:
      dot: 0.1.0
      expand: 0.0.0
    once: false
    origin: tgpy://module/rand
    priority: 16
    save_locals: true
    description: generate random from expanded string (e.g. rand("{1..100}") -> random int from 1 to 100)
"""
import random


@dot('rand')  # dot module
def rand(s=''):
    return random.choice(expand(s))
