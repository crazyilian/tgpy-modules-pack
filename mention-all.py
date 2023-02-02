"""
    name: mention-all
    once: false
    origin: tgpy://module/mention-all
    priority: 1674449251.69556
    save_locals: true
"""
async def mention_all():
    users = filter(lambda x: not x.bot, await client.get_participants(ctx.msg.chat_id))
    names = list(map(lambda u: "[{0}](tg://user?id={1})\n".format(u.first_name, u.id), users))
    for i in range(0, len(names), 5):
        await client.send_message(ctx.msg.chat_id, ''.join(names[i:i+5]), parse_mode="Markdown")
    await ctx.msg.delete()
