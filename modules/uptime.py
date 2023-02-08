"""
    name: uptime
    once: false
    origin: tgpy://module/uptime
    priority: 1674328542.263713
    save_locals: true
"""
from datetime import datetime

start_time = datetime.now()


def uptime():
    return datetime.now() - start_time
