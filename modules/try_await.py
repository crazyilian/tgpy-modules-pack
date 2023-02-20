"""
    name: try_await
    once: false
    origin: tgpy://module/try_await
    priority: 10
    save_locals: true
"""

import asyncio
import concurrent.futures


async def await_sync(func, *args, highcpu=False):
    loop = asyncio.get_event_loop()
    if not highcpu:
        return await loop.run_in_executor(None, func, *args)
    with concurrent.futures.ProcessPoolExecutor() as pool:
        return await loop.run_in_executor(pool, func, *args)


async def try_await(value):
    if hasattr(value, '__await__'):
        return await value
    else:
        return value
