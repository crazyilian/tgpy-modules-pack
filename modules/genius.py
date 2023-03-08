"""
    description: ''
    name: genius
    needs:
      dot: 0.1.0
    needs_pip:
      aiohttp: aiohttp
      html2text: html2text
    once: false
    origin: https://t.me/tgpy_flood/28543
    priority: 32
    version: 0.3.1
    wants: {}
"""
import ast
import json
import html2text
import aiohttp
import re

from itertools import islice


def split_every(n, iterable):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))


@dot("genius")
async def genius(query):
    data = await (await aiohttp_session.get("https://genius.com/api/search/multi", params={"q": query})).json()
    url = None
    for section in data["response"]["sections"]:
        if section["type"] == "song":
            if not section["hits"]:
                continue
            url = section["hits"][0]["result"]["url"]
            break
    if url is None:
        return "Song not found"

    data = await (await aiohttp_session.get(url)).text()
    data = re.search(r"__PRELOADED_STATE__ = JSON\.parse\((.*)\);$", data, flags=re.M).group(1)
    data = json.loads(ast.literal_eval(data).replace(r"\$", "$"))

    song = data["songPage"]

    conv = html2text.HTML2Text()
    conv.ignore_links = True

    title = "Unknown"
    artist = "Unknown"
    for item in song["dfpKv"]:
        if item["name"] == "song_title":
            title = item["values"][0]
        elif item["name"] == "artist_name":
            artist = ", ".join(item["values"])

    text = re.sub(r"<a.*?>", "", song["lyricsData"]["body"]["html"].replace("</a>", ""))
    text = text.replace("<br>", "")
    text = text.replace("<p>", "").replace("</p>", "")
    text = text.strip()

    text = f"<a href='{url}'><b>{title}</b></a> by {artist}\n\n" + text
    for chunk in split_every(4096, text):
        await ctx.msg.respond(chunk, parse_mode="html")
    await ctx.msg.delete()


aiohttp_session = aiohttp.ClientSession()

__all__ = ["genius"]
