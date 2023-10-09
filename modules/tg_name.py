"""
    description: get username/first name/title of telethon entity object
    name: tg_name
    needs: {}
    needs_pip: {}
    once: false
    origin: https://github.com/crazyilian/tgpy-modules/blob/main/modules/tg_name.py
    priority: 12
    version: 0.0.1
    wants: {}
"""
import telethon.tl.types


def get_name(user, try_username=True):
    if isinstance(user, telethon.tl.types.Channel) or isinstance(user, telethon.tl.types.Chat):
        return f'"{user.title}"'
    if try_username and user.username:
        return '@' + user.username
    return f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
