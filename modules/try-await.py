"""
    name: try-await
    once: false
    origin: tgpy://module/try-await
    priority: 10
    save_locals: true
"""

async def try_await(value):
    if hasattr(value, '__await__'):
        return await value
    else:
        return value

