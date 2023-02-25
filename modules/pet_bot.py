"""
    name: pet_bot
    once: false
    origin: tgpy://module/pet_bot
    priority: 10000
    save_locals: true
"""

import telethon
from tgpy.utils import DATA_DIR
from tgpy import app
import asyncio

# config_loader module
PetBotConfig = UniversalModuleConfig('pet_bot', ['bot_token'], [str],
                                     default_dict={'session_filename': str(DATA_DIR / 'PetBot.session')})

pet_bot = telethon.TelegramClient(
    PetBotConfig.session_filename, app.client.api_id, app.client.api_hash
)
pet_bot.parse_mode = 'html'
asyncio.create_task(pet_bot.start(bot_token=PetBotConfig.bot_token))


@dot  # dot module
async def notify(text, chat_id=None, **kwargs):
    if not text:
        text = "Something happened"
    if chat_id is None:
        me = await client.get_me()
        chat_id = me.id
    await pet_bot.send_message(chat_id, text, **kwargs)
