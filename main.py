import io
import locale
import sys
import traceback

import aiohttp
import discord
import koreanbots
from discord.ext import commands

from lib import config
from lib import utils

Check = utils.Check()

locale.setlocale(locale.LC_ALL, "")


class Miya(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.koreanbots = koreanbots.Client(self, config.DBKRToken)

    async def get_rank(self):
        num = 0
        while True:
            num += 1
            response = await self.koreanbots.getBots(num)
            data = [x.name for x in response]
            if "미야" in data:
                index = data.index("미야")
                result = 9 * (num - 1) + (index + 1)
                return result

    async def record(self, content):
        try:
            payload = content.encode("utf-8")
            async with aiohttp.ClientSession(raise_for_status=True) as cs:
                async with cs.post("https://hastebin.com/documents",
                                   data=payload) as r:
                    post = await r.json()
                    uri = post["key"]
                    return f"https://hastebin.com/{uri}"
        except aiohttp.ClientResponseError:
            return discord.File(io.StringIO(content), filename="Traceback.txt")


intents = discord.Intents(
    guilds=True,
    members=True,
    bans=True,
    emojis=True,
    integrations=True,
    webhooks=True,
    invites=True,
    voice_states=True,
    presences=False,
    messages=True,
    reactions=True,
    typing=True,
)
miya = Miya(
    shard_count=3,
    command_prefix="미야야 ",
    description="다재다능한 Discord 봇, 미야.",
    help_command=None,
    chunk_guilds_at_startup=True,
    intents=intents,
)


def load_modules(miya):
    failed = []
    exts = [
        "modules.info",
        "modules.general",
        "modules.settings",
        "modules.admin",
        "modules.mods",
        "modules.cc",
        "modules.eco",
        "modules.events",
        "modules.log",
        "jishaku",
    ]

    for ext in exts:
        try:
            miya.load_extension(ext)
        except Exception as e:
            print(f"{e.__class__.__name__}: {e}")
            failed.append(ext)

    return failed


@miya.check
async def process(ctx):
    p = await Check.identify(ctx)
    return p


@miya.event
async def on_error(event, *args, **kwargs):
    s = traceback.format_exc()
    content = f"{event}에 발생한 예외를 무시합니다;\n{s}"
    channel = miya.get_channel(config.Debug)
    try:
        await channel.send(content)
    except:
        record = await miya.record(content)
        if isinstance(record, discord.File):
            await channel.send(file=record)
        else:
            await channel.send(record)


load_modules(miya)
miya.run(config.BotToken)
