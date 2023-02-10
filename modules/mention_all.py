"""
    name: mention_all
    once: false
    origin: tgpy://module/mention_all
    priority: 10001
    save_locals: true
"""


def get_name(user, try_username=True):
    if try_username and user.username:
        return '@' + user.username
    return f'<a href="tg://user?id={user.id}">{user.first_name}</a>'


@dot_msg_handler  # dot_msg_handler module
async def mention_all_names(msg):
    users = filter(lambda x: not x.bot, await client.get_participants(msg.chat_id))
    names = list(map(lambda u: get_name(u, False), users))
    for i in range(0, len(names), 5):
        await client.send_message(msg.chat_id, '\n'.join(names[i:i + 5]))
    await msg.delete()


@dot_msg_handler  # dot_msg_handler module
async def mention_all(msg):
    users = filter(lambda x: not x.bot, await client.get_participants(msg.chat_id))
    names = list(map(lambda u: get_name(u, True), users))
    for i in range(0, len(names), 5):
        await client.send_message(msg.chat_id, '\n'.join(names[i:i + 5]))
    await msg.delete()
