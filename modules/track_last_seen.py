"""
    name: track_last_seen
    once: false
    origin: tgpy://module/track_last_seen
    priority: 1676485859.4033725
    save_locals: true
"""
import telethon
import asyncio


class TrackLastSeenModule:
    def __init__(self):
        self.config = UniversalModuleConfig('track_last_seen', ['notify_chat_id'], [int],
                                            default_dict={'watches': {}})  # config_loader module
        self.handlers = []
        asyncio.create_task(self.add(*self.config.watches.keys()))

    async def get_id_name_by_entities(self, entities):
        res = {}
        for ent in entities:
            if ent in self.config.watches:
                res[ent] = self.config.watches[ent]
            else:
                user = await client.get_entity(ent)
                res[user.id] = get_name(user)  # mention_all module
        return res

    async def add(self, *entities):
        id_name = await self.get_id_name_by_entities(entities)
        add_handler = []
        for id in id_name:
            self.config.watches[id] = id_name[id]
            if id not in self.handlers:
                add_handler.append(id)
        self.config.save()
        self.handlers.extend(add_handler)

        @client.on(telethon.events.UserUpdate(chats=add_handler, func=lambda e: e.status))
        async def user_update_event_handler(event):
            name = self.config.watches.get(id, None)
            if name is None:
                return
            text = ''
            if isinstance(event.status, telethon.types.UserStatusOnline):
                text = f'{name} online'
            elif isinstance(event.status, telethon.types.UserStatusOffline):
                text = f'{name} offline'
            else:
                text = f'{name} {event.status.__class__.__name__}'
            await notify(text, chat_id=self.config.notify_chat_id)  # pet_bot module

    async def remove(self, *entities):
        id_name = await self.get_id_name_by_entities(entities)
        for id in id_name:
            self.config.watches.pop(id)
        self.config.save()

    def get(self):
        return "\n".join(self.config.watches.values())


track_last_seen = TrackLastSeenModule()
