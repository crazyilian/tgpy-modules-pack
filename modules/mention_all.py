"""
    description: mention all users in chat
    name: mention_all
    needs:
      tg_name: 0.0.0
    needs_pip: {}
    once: false
    origin: https://github.com/crazyilian/tgpy-modules/blob/main/modules/mention_all.py
    priority: 13
    version: 0.0.0
    wants: {}
"""
async def mention_all(try_usernames=True):
    users = filter(lambda x: not x.bot, await client.get_participants(ctx.msg.chat_id))
    names = list(map(lambda u: get_name(u, try_usernames), users))
    for i in range(0, len(names), 5):
        await client.send_message(ctx.msg.chat_id, '\n'.join(names[i:i + 5]))
    await ctx.msg.delete()
