"""
    name: tex
    once: false
    origin: tgpy://module/tex
    priority: 10000
    save_locals: true
"""
import unicodeit


@dot_msg_handler
async def tex(msg):
    await msg.edit(unicodeit.replace(msg.text))
