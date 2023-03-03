"""
    description: ''
    name: uptime
    needs: {}
    needs_pip: {}
    once: false
    origin: https://t.me/tgpy_flood/6513
    priority: 10
    version: 0.0.0
    wants: {}
"""
from datetime import datetime
start_time = datetime.now()
def uptime():
    return datetime.now() - start_time
