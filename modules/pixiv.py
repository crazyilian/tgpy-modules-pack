"""
    name: pixiv
    once: false
    origin: tgpy://module/pixiv
    priority: 1675890236
    save_locals: false
"""

import pixivpy_async
import asyncio
import random
import time

import logging

REQUEST_ATTEMPTS = 3
ACCESS_TOKEN_TIMEOUT = 60 * 60 - 5


async def randSleep(base=0.1, rand=0.5):
    await asyncio.sleep(base + rand * random.random())


class AutoLoginAPI:
    def __init__(self, refresh_token=None, **requests_kwargs):
        super().__init__(**requests_kwargs)
        self.REFRESH_TOKEN = refresh_token
        self.api = pixivpy_async.AppPixivAPI(**requests_kwargs)
        self.last_login = 0

    def __getattr__(self, item):
        api_item = self.api.__getattribute__(item)
        logging.info('get api attr: ' + str(item))
        if not asyncio.iscoroutinefunction(api_item):
            return api_item

        async def wrapper(*args, **kwargs):
            e = None
            if 'req_auth' not in kwargs:
                kwargs['req_auth'] = True

            if self.is_expired_token():
                await self.login()
                await randSleep()

            for _ in range(REQUEST_ATTEMPTS):
                try:
                    return await api_item(*args, **kwargs)
                except (pixivpy_async.error.NoTokenError, pixivpy_async.error.NoLoginError) as e:
                    logging.error('Error while calling ' + str(item))
                    logging.error(e)
                    await self.login()
                    await randSleep()
            raise e

        return wrapper

    def is_expired_token(self):
        return time.time() - self.last_login > ACCESS_TOKEN_TIMEOUT

    async def login(self):
        logging.info('logging in...')
        await self.api.login(refresh_token=self.REFRESH_TOKEN)
        self.last_login = time.time()


class PixivUser:

    def __init__(self, user_id, refresh_token=None):
        self.USER_ID = user_id
        self.api = AutoLoginAPI(refresh_token)
        self.user_details = None

    async def iterate_request_offset(self, api_request, query_params):
        while query_params is not None:
            r = await api_request(**query_params)
            yield r
            query_params = self.api.parse_qs(r['next_url'])
            await randSleep()

    async def get_all_followers(self):
        result = []
        async for r in self.iterate_request_offset(self.api.user_follower, {"user_id": self.USER_ID}):
            result.extend(r['user_previews'])
        return result

    async def get_all_illusts(self):
        result = []
        async for r in self.iterate_request_offset(self.api.user_illusts, {"user_id": self.USER_ID}):
            result.extend(r['illusts'])
        return result

    async def get_user_details(self):
        if self.user_details is None:
            self.user_details = await self.api.user_detail(self.USER_ID)
        return self.user_details

    async def illusts_stats(self):
        illusts = await self.get_all_illusts()
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
            'Total illusts': len(illusts),
            'Total views': views,
            'Total bookmarks': bookmarks,
            'Max views': max_views,
            'Max bookmarks': max_bookmarks,
        }

    async def followers_stats(self):
        followers = await self.get_all_followers()
        return {
            'Total followers': len(followers)
        }

    async def user_stats(self):
        r = await self.get_user_details()
        user_name = r['user']['name']
        user_url = f"https://pixiv.net/en/users/{r['user']['id']}"
        return {
            "Username": user_name,
            "URL": user_url
        }

    async def text_stats(self, keys):
        user = await self.user_stats()
        message = f"🎨 Pixiv stats of <a href='{user['URL']}'>{user['Username']}</a>"
        stats = await self.illusts_stats() | await self.followers_stats()
        for key in keys:
            if key in stats:
                message += f"\n{key}: {stats[key]}"
        return message


async def edit_unknown_command(msg):
    return await msg.edit(msg.text + '\n<code>&gt; Unknown pixiv module command</code>')


async def edit_loading(msg):
    return await msg.edit(msg.text + '\n<code>&gt; Loading...</code>')


@dot_msg_handler  # dot_msg_handler module
async def pixiv(msg):
    text: str = msg.raw_text[len('.pixiv '):]
    commands = list(filter(bool, '\n'.join(filter(lambda line: not line.startswith('>'), text.split('\n'))).split()))
    tree = {
        'stats': {
            'partial': (user.text_stats, [['Total illusts', 'Total views', 'Total bookmarks', 'Total followers']]),
            'full': (user.text_stats, [['Total illusts', 'Total views', 'Total bookmarks', 'Max views', 'Max bookmarks',
                                        'Total followers']])
        }
    }
    tree['stats'][''] = tree['stats']['partial']
    tree[''] = tree['stats']

    command_index = 0
    while isinstance(tree, dict):
        c = ''
        if command_index < len(commands):
            c = commands[command_index]
            command_index += 1
        tree = tree.get(c)
        if tree is not None:
            continue
        return await edit_unknown_command(msg)

    if isinstance(tree, dict):
        return await edit_unknown_command(msg)
    await edit_loading(msg)
    ans = await try_await(tree[0](*tree[1]))  # try_await module
    await msg.edit(ans)


config = UniversalModuleConfig('pixiv', ('user_id', 'refresh_token'))  # config_loader module
user = PixivUser(config.user_id, config.refresh_token)
