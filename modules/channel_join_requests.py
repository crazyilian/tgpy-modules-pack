"""
    name: channel_join_requests
    once: false
    origin: tgpy://module/channel_join_requests
    priority: 1673128541.938998
    save_locals: true
"""

from telethon import functions

ChannelJoinRequestsConfig = UniversalModuleConfig('channel_join_requests',
                                                  default_dict={'channel_ids': [], 'requesters': {}})


class ChannelJoinRequests:
    def __init__(self, channel_id):
        self.id = channel_id
        self.name = None

    def get_requesters(self):
        return ChannelJoinRequestsConfig.requesters[self.id]

    async def get_updates(self):
        full_channel = await client(functions.channels.GetFullChannelRequest(self.id))
        self.name = full_channel.chats[0].title

        new_users = []
        requesters = self.get_requesters().copy()
        for user in full_channel.users:
            if user.is_self:
                continue
            if user.id not in requesters:
                new_users.append(user)
            else:
                requesters.remove(user.id)
        joined_users_id = requesters
        return new_users, joined_users_id

    async def save_updates(self, new_users, joined_users_id):
        for user in new_users:
            ChannelJoinRequestsConfig.requesters[self.id].append(user.id)
        for user_id in joined_users_id:
            ChannelJoinRequestsConfig.requesters[self.id].remove(user_id)
        ChannelJoinRequestsConfig.save()

    async def update_name(self):
        full_channel = await client(functions.channels.GetFullChannelRequest(self.id))
        self.name = full_channel.chats[0].title
        return self.name


join_requests_channels = [ChannelJoinRequests(id) for id in ChannelJoinRequestsConfig.channel_ids]


def channel_join_requests_get_requesters():
    result = {}
    for channel in join_requests_channels:
        result[channel.id] = channel.get_requesters()
    return result


def channel_join_requests_add_channel(channel_id):
    ChannelJoinRequestsConfig.channel_ids.append(channel_id)
    ChannelJoinRequestsConfig.requesters[channel_id] = []
    ChannelJoinRequestsConfig.save()
    join_requests_channels.append(ChannelJoinRequests(channel_id))


def channel_join_requests_remove_channel(channel_id):
    if channel_id not in ChannelJoinRequestsConfig.channel_ids:
        return
    ChannelJoinRequestsConfig.channel_ids.remove(channel_id)
    ChannelJoinRequestsConfig.requesters.pop(channel_id)
    ChannelJoinRequestsConfig.save()
    for ind, channel in enumerate(join_requests_channels, 0):
        if channel.id == channel_id:
            join_requests_channels.pop(ind)
            break


def channel_join_requests_get_channels():
    return ChannelJoinRequestsConfig.channel_ids


async def channel_join_requests_update():
    for channel in join_requests_channels:
        new_users, joined_users_id = await channel.get_updates()
        await channel.save_updates(new_users, joined_users_id)

        if new_users or True:
            notify_message = f'New joining requests in channel "{channel.name}"'
            for user in new_users:
                user = await client.get_entity(user)  # fix user.username == None
                notify_message += f'\n' + get_name(user)  # mention_all module
            await notify(notify_message)  # notification module


cron_add_job(channel_join_requests_update, "0 * * * *")  # cron module
