"""
    description: ''
    name: uptime
    needs: {}
    needs_pip: []
    once: false
    origin: https://raw.githubusercontent.com/crazyilian/tgpy-modules/main/modules/uptime.py
    priority: 30
    version: 0.0.0
    wants: {}
"""
from datetime import datetime

start_time = datetime.now()


def uptime():
    return datetime.now() - start_time
