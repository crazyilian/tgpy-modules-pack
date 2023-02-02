"""
    name: pixiv_stats
    once: false
    origin: tgpy://module/pixiv_stats
    priority: 1674775447
    save_locals: true
"""

import pixivpy_async
import random
import asyncio
import os
import telethon.events


class PixivModule:
    class PixivUser:
        def __init__(self, user_id, refresh_token):
            self.USER_ID = user_id
            self.REFRESH_TOKEN = refresh_token
            self.api = pixivpy_async.AppPixivAPI()

        async def login(self):
            await self.api.login(refresh_token=self.REFRESH_TOKEN)

        async def randSleep(self, base=0.1, rand=0.5):
            await asyncio.sleep(base + rand * random.random())

        async def iterate_offset(self, api_request, query_params, result, reduce_f):
            while query_params is not None:
                print('request:', query_params)
                r = await api_request(**query_params)
                result = reduce_f(result, r)
                query_params = self.api.parse_qs(r['next_url'])
                await self.randSleep()
            return result

        async def get_all_followers(self):
            return await self.iterate_offset(self.api.user_follower, {"user_id": self.USER_ID}, [],
                                             lambda a, b: a + b['user_previews'])

        async def get_all_illusts(self):
            return await self.iterate_offset(self.api.user_illusts, {"user_id": self.USER_ID}, [],
                                             lambda a, b: a + b['illusts'])

        def illusts_stats(self, illusts):
            views = 0
            bookmarks = 0
            max_views = 0
            max_bookmarks = 0
            for illust in illusts:
                views += illust['total_view']
                bookmarks += illust['total_bookmarks']
                max_views = max(max_views, illust['total_view'])
                max_bookmarks = max(max_bookmarks, illust['total_bookmarks'])
            return {
                # 'Total illusts': len(illusts),
                'Total views': views,
                'Total bookmarks': bookmarks,
                # 'Max views': max_views,
                # 'Max bookmarks': max_bookmarks,
            }

        def followers_stats(self, followers):
            return {
                'Total followers': len(followers)
            }

        async def user_details(self):
            r = await self.api.user_detail(self.USER_ID)
            user_name = r['user']['name']
            user_url = f"https://pixiv.net/en/users/{r['user']['id']}"
            return {
                "Username": user_name,
                "URL": user_url
            }

        async def get_text_stats(self):
            await self.login()
            followers = await self.get_all_followers()
            illusts = await self.get_all_illusts()
            user = await self.user_details()
            stats = self.illusts_stats(illusts) | self.followers_stats(followers)
            message = f"🎨 Pixiv stats of [{user['Username']}]({user['URL']})"
            for title in stats:
                message += f"\n{title}: {stats[title]}"
            return message

    def __init__(self):
        self.__user = self.PixivUser(int(os.getenv("PIXIV_USER_ID")), os.getenv("PIXIV_REFRESH_TOKEN"))

    async def pixiv_stats(self):
        return await self.__user.get_text_stats()


__pixiv_module = PixivModule()


@client.on(telethon.events.NewMessage(outgoing=True))
@client.on(telethon.events.MessageEdited(outgoing=True))
async def on_pixiv_message(msg):
    text = msg.text
    if text.startswith(".pixiv ") or text.startswith(".pixiv\n"):
        text = text[7:].strip()
        if text.startswith('stats'):
            await msg.edit('`Loading Pixiv stats...`', parse_mode="md", link_preview=False)
            await msg.edit(await __pixiv_module.pixiv_stats(), parse_mode="md", link_preview=False)

