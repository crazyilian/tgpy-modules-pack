"""
    name: type_anim
    once: false
    origin: tgpy://module/type_anim
    priority: 1674448649.916904
    save_locals: false
"""
import asyncio


@dot_msg_handler  # dot_msg_handler module
async def type(msg):
    await msg.delete()
    text = msg.text.removeprefix('.type ')
    chat = msg.chat_id
    rep = await msg.get_reply_message()
    message = await client.send_message(chat, '...', reply_to=rep)
    for i in range(len(text)):
        for state in range(2):
            await message.edit(text[:i + 1] + '▓░'[state])
            await asyncio.sleep(0.1)
    await message.edit(text)
