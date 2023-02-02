"""
    name: tex
    once: false
    origin: tgpy://module/tex
    priority: 1674449773.343128
    save_locals: true
"""
import telethon.events
import unicodeit

@client.on(telethon.events.NewMessage(outgoing=True))
@client.on(telethon.events.MessageEdited(outgoing=True))
async def on_tex_message(msg):
    text = msg.text
    if text.startswith(".tex ") or text.startswith(".tex\n"):
        text = text[5:]
        await msg.edit(unicodeit.replace(text))
