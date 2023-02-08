"""
    name: mention-all
    once: false
    origin: tgpy://module/mention-all
    priority: 1674449251.69556
    save_locals: true
"""


def get_name(user, try_username=True):
    if try_username and user.username:
        return '@' + user.username
    return "[{0}](tg://user?id={1})\n".format(user.first_name, user.id)


@dot_msg_handler
async def mention_all_names(msg):
    users = filter(lambda x: not x.bot, await client.get_participants(msg.chat_id))
    names = list(map(lambda u: get_name(u, False), users))
    for i in range(0, len(names), 5):
        await client.send_message(msg.chat_id, ''.join(names[i:i + 5]), parse_mode="Markdown")
    await msg.delete()


@dot_msg_handler
async def mention_all(msg):
    users = filter(lambda x: not x.bot, await client.get_participants(msg.chat_id))
    names = list(map(lambda u: get_name(u, True), users))
    for i in range(0, len(names), 5):
        await client.send_message(msg.chat_id, ''.join(names[i:i + 5]), parse_mode="Markdown")
    await msg.delete()
