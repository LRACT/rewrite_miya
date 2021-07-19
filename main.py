import discord
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
import koreanbots
import config
import aiomysql
import aiohttp
import os
import traceback
import io


class Miya(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kb = koreanbots.Koreanbots(self, config.KBToken, run_task=True)

    async def debug(self, *args, **kwargs):
        async with aiohttp.ClientSession() as cs:
            webhook = Webhook.from_url(config.Debug, adapter=AsyncWebhookAdapter(cs))
            await webhook.send(*args, **kwargs)

    async def sql(self, type: int, exec: str):
        o = await aiomysql.connect(
            host=config.DB["host"],
            port=config.DB["port"],
            user=config.DB["user"],
            password=config.DB["password"],
            db=config.DB["schema"],
            autocommit=True,
        )
        c = await o.cursor(aiomysql.DictCursor)
        try:
            await c.execute(exec)
        except Exception as e:
            raise e
            o.close()
        else:
            if type == 0:
                results = await c.fetchall()
                o.close()
                return results
            o.close()
            return "Successfully Executed"

    async def record(self, content):
        try:
            payload = content.encode("utf-8")
            async with aiohttp.ClientSession(raise_for_status=True) as cs:
                async with cs.post("https://hastebin.com/documents", data=payload) as r:
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
bot = Miya(
    shard_count=3,
    command_prefix=commands.when_mentioned_or("미야야"),
    strip_after_prefix=True,
    max_messages=200000,
    intents=intents,
    help_command=None,
    description="더 많은 일을 간단하게, Discord에서 경험해보세요.",
    chunk_guilds_at_startup=True,
)


def startup(bot):
    modules = []
    for module in os.listdir("./exts"):
        if module.endswith(".py"):
            a = module.replace(".py", "")
            modules.append(f"exts.{a}")
    modules.append("jishaku")
    for ext in modules:
        try:
            bot.load_extension(ext)
        except Exception as e:
            s = traceback.format_exc()
            print(f"{e.__class__.__name__}: {s}")


@bot.event
async def on_error(event, *args, **kwargs):
    s = traceback.format_exc()
    content = f"{event}에 발생한 예외를 무시합니다;\n{s}"
    try:
        await bot.debug(
            f"```py\n{content}```",
            avatar_url=bot.user.avatar_url,
            username=f"{bot.user.name} 디버깅",
        )
    except:
        record = await bot.record(content)
        if isinstance(record, discord.File):
            await bot.debug(
                file=record,
                avatar_url=bot.user.avatar_url,
                username=f"{bot.user.name} 디버깅",
            )
        else:
            await bot.debug(
                record, avatar_url=bot.user.avatar_url, username=f"{bot.user.name} 디버깅"
            )


startup(bot)
bot.run(config.Token)
