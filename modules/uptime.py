"""
    name: uptime
    once: false
    origin: https://t.me/tgpy_flood/6513
    priority: 15
    save_locals: true
"""
from datetime import datetime

start_time = datetime.now()


def uptime():
    return datetime.now() - start_time
