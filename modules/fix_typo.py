"""
    name: fix_typo
    once: false
    origin: tgpy://module/fix_typo
    priority: 1676066830.3317404
    save_locals: true
"""

# WARNING: long spellers loading, so TGPy will take ~9 seconds longer to start

from autocorrect import Speller
import logging

logging.info("Loading spellers")
spellers = {
    'ru': Speller(lang='ru'),
    'en': Speller(lang='en')
}
logging.info("Spellers are loaded")


def typo_get_langs_probabilities(text):
    en_cnt = sum(ord('a') <= ord(c) <= ord('z') for c in text.lower())
    ru_cnt = sum(ord('а') <= ord(c) <= ord('я') for c in text.lower())
    return {
        'ru': ru_cnt / len(text),
        'en': en_cnt / len(text)
    }


def typo_fix_text(text):
    probabilities = typo_get_langs_probabilities(text)
    for lang in spellers:
        if probabilities[lang] > 0.3:
            text = spellers[lang](text)
    return text


@dot_prefixes('typo', 'ytpo', 'tpyo', 'tyop')  # dot module
async def typo(*_):
    orig = await ctx.msg.get_reply_message()
    text = typo_fix_text(orig.raw_text)  # not .text to prevent html tags because of return type in <code>
    return text


@dot_msg_handler_prefixes('typoip', 'ytpoip', 'tpyoip', 'tyopip',
                          'typopi', 'ytpopi', 'tpyopi', 'tyoppi', )  # dot_msg_handler module
async def typoip(msg):
    await msg.delete()
    orig = await msg.get_reply_message()
    text = typo_fix_text(orig.text)
    await orig.edit(text)
