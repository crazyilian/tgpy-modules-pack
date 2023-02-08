"""
    name: chlayout
    once: false
    origin: tgpy://module/chlayout
    priority: 1675840405.912177
    save_locals: true
"""

en_layout = '`1234567890-=qwertyuiop[]asdfghjkl;\'\\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?'
ru_layout = 'ё1234567890-=йцукенгшщзхъфывапролджэ\\ячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,'
translation_en_to_ru = str.maketrans(dict(zip(en_layout, ru_layout)))
translation_ru_to_en = str.maketrans(dict(zip(ru_layout, en_layout)))


@dot
async def chlayout(*_):
    orig = await ctx.msg.get_reply_message()
    if [c for c in orig.text if c in 'qwertyuiop[]asdfghjkl\'~!@#$%^&QWERTYUIOP{}ASDFGHJKLZXCVBNM<>']:
        return orig.text.translate(translation_en_to_ru)
    else:
        return orig.text.translate(translation_ru_to_en)


@dot_msg_handler
async def chlayoutip(msg):
    await msg.delete()
    orig = await msg.get_reply_message()
    if [c for c in orig.text if c in 'qwertyuiop[]asdfghjkl\'~!@#$%^&QWERTYUIOP{}ASDFGHJKLZXCVBNM<>']:
        await orig.edit(orig.text.translate(translation_en_to_ru))
    else:
        await orig.edit(orig.text.translate(translation_ru_to_en))
