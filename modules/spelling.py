"""
    name: spelling
    once: false
    origin: tgpy://module/spelling
    priority: 1676066830.3317404
    save_locals: true
"""

from autocorrect import Speller
import logging

logging.info("Loading spellers")
spellers = {
    'ru': Speller(lang='ru'),
    'en': Speller(lang='en')
}
logging.info("Spellers are loaded")


def spelling_get_langs_probabilities(text):
    en_cnt = sum(ord('a') <= ord(c) <= ord('z') for c in text.lower())
    ru_cnt = sum(ord('а') <= ord(c) <= ord('я') for c in text.lower())
    return {
        'ru': ru_cnt / len(text),
        'en': en_cnt / len(text)
    }


def spelling_text(text):
    probabilities = spelling_get_langs_probabilities(text)
    for lang in spellers:
        if probabilities[lang] > 0.3:
            text = spellers[lang](text)
    return text


@dot  # dot module
async def spelling(*_):
    orig = await ctx.msg.get_reply_message()
    text = spelling_text(orig.text)
    return text


@dot_msg_handler  # dot_msg_handler module
async def spellingip(msg):
    await msg.delete()
    orig = await msg.get_reply_message()
    text = spelling_text(orig.text)
    await orig.edit(text)


async def _func(*_):
    return await spelling(*_)


for name in ['spellign', 'speling', 'spelign']:
    _func.__name__ = name
    dot(_func)  # dot module


async def _func(msg):
    return await spellingip(msg)


for name in ['spellignip', 'spelingip', 'spelignip', 'spellignpi', 'spelingpi', 'spelignpi']:
    _func.__name__ = name
    dot_msg_handler(_func)  # dot_msg_handler module
