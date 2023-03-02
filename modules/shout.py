"""
    description: ''
    name: shout
    needs: {}
    needs_pip: []
    once: false
    origin: https://t.me/tgpy_flood/27736
    priority: 25
    version: 0.0.0
    wants: {}
"""
vowels = 'АОУЫЭЯЁЮИЕAOUIEY'

async def shout():
    original = await ctx.msg.get_reply_message()
    text = original.raw_text.upper()
    ok = (i for i in range(len(text) - 1, -1, -1) if text[i] in vowels)
    pos = next(ok, -1)
    return text[:pos] + text[pos] * 5 + text[pos:]
