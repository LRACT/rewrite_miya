import datetime

import aiohttp
import aiomysql
import discord
from bs4 import BeautifulSoup
from discord import AsyncWebhookAdapter, Webhook
from discord.ext import commands
from pytz import timezone, utc

from lib import config


class Forbidden(commands.CheckFailure):
    def __init__(self, embed):
        self.embed = embed
        super().__init__("<a:ban_guy:761149578216603668> https://discord.gg/tu4NKbEEnn")


class NoReg(commands.CheckFailure):
    def __init__(self):
        super().__init__(
            "<:cs_id:659355469034422282> 미야와 대화하시려면, 먼저 이용 약관에 동의하셔야 해요.\n`미야야 가입` 명령어를 사용하셔서 가입하실 수 있어요!"
        )


class Maintaining(commands.CheckFailure):
    def __init__(self, reason):
        super().__init__(
            f"<:cs_protect:659355468891947008> 지금은 미야와 대화하실 수 없어요.\n```점검 중 : {reason}```"
        )


async def sql(type: int, sql: str):
    o = await aiomysql.connect(
        host=config.MySQL["host"],
        port=config.MySQL["port"],
        user=config.MySQL["username"],
        password=config.MySQL["password"],
        db=config.MySQL["schema"],
        autocommit=True,
    )
    c = await o.cursor()
    try:
        await c.execute(sql)
        if type == 0:
            rows = await c.fetchall()
            o.close()
            return rows
        o.close()
        return "SUCCESS"
    except Exception as e:
        o.close()
        raise e


class Hook:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def terminal(self, target, content, name, avatar):
        url = None
        if target == 1:
            url = config.Blacklist
        elif target == 0:
            url = config.Terminal
        else:
            raise discord.NotFound
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
            await webhook.send(f"```{content}```", username=name, avatar_url=avatar)

    async def hook(self, url, content, name, avatar):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
            await webhook.send(content, username=name, avatar_url=avatar)


class Get:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def localize(self, time):
        KST = timezone("Asia/Seoul")
        abc = utc.localize(time).astimezone(KST)
        return abc.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")

    async def hangang(self):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://hangang.dkserver.wo.tc") as r:
                response = await r.json(content_type=None)
                temp = None
                time = (response["time"]).split(" ")[0]
                if "." in response["temp"]:
                    temp = int(response["temp"].split(".")[0])
                else:
                    temp = int(response["temp"])
                return [temp, time]

    async def corona(self):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://ncov.mohw.go.kr/") as r:
                html = await r.text()
                soup = BeautifulSoup(html, "lxml")
                data = soup.find("div", class_="liveNum")
                num = data.findAll("span", class_="num")
                corona_info = [corona_num.text for corona_num in num]
                return corona_info


class Check:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hook = Hook()
        self.get = Get()

    async def mgr(self, ctx):
        mrows = await sql(0, f"SELECT * FROM `users` WHERE `user` = {ctx.author.id}")
        if not mrows:
            return False
        return mrows[0][1] == "Maintainer" or mrows[0][1] == "Administrator"

    async def identify(self, ctx):
        if ctx.channel.type == discord.ChannelType.private:
            await self.hook.terminal(
                0,
                f"On Directs >\nUser - {ctx.author} ({ctx.author.id})\nContent - {ctx.message.content}",
                "명령어 처리 기록",
                ctx.bot.user.avatar_url,
            )
            raise commands.NoPrivateMessage

        manage = await self.mgr(ctx)
        maintain = await sql(
            0, f"SELECT * FROM `miya` WHERE `miya` = '{ctx.bot.user.id}'"
        )
        if maintain[0][1] == "true" and not manage:
            await self.hook.terminal(
                0,
                f"Cancelled due to maintaining >\nUser - {ctx.author} ({ctx.author.id})\nContent - {ctx.message.content}",
                "명령어 처리 기록",
                ctx.bot.user.avatar_url,
            )
            raise Maintaining(maintain[0][2])

        reason, admin, time, banned, forbidden = None, None, None, None, None
        words = await sql(0, "SELECT * FROM `forbidden`")
        for word in words:
            if word[0] in ctx.message.content:
                forbidden = True
                banned = word[0]
        users = await sql(0, f"SELECT * FROM `users` WHERE `user` = '{ctx.author.id}'")
        rows = await sql(0, f"SELECT * FROM `blacklist` WHERE `id` = '{ctx.author.id}'")
        if rows:
            if manage is not True:
                reason = rows[0][1]
                admin = ctx.bot.get_user(int(rows[0][2]))
                time = rows[0][3]
                await self.hook.terminal(
                    0,
                    f"Blocked User >\nUser - {ctx.author} ({ctx.author.id})\nContent - {ctx.message.content}\nGuild - {ctx.guild.name} ({ctx.guild.id})",
                    "명령어 처리 기록",
                    ctx.bot.user.avatar_url,
                )
            else:
                await ctx.send("당신은 차단되었지만, 관리 권한으로 명령어를 실행했습니다.")
                await self.hook.terminal(
                    0,
                    f"Manager Bypassed >\nUser - {ctx.author} ({ctx.author.id})\nContent - {ctx.message.content}\nGuild - {ctx.guild.name} ({ctx.guild.id})",
                    "명령어 처리 기록",
                    ctx.bot.user.avatar_url,
                )
                return True
        elif forbidden is True:
            if manage is not True:
                reason = f"부적절한 언행 **[Auto]** - {banned}"
                admin = ctx.bot.user
                time = self.get.localize(datetime.datetime.utcnow())
                await sql(
                    1,
                    f"INSERT INTO `blacklist`(`id`, `reason`, `admin`, `datetime`) VALUES('{ctx.author.id}', '{reason}', '{admin.id}', '{time}')",
                )
                await self.hook.terminal(
                    1,
                    f"New Block >\nVictim - {ctx.author.id}\nAdmin - {admin} ({admin.id})\nReason - {reason}",
                    "제한 기록",
                    ctx.bot.user.avatar_url,
                )
                await self.hook.terminal(
                    0,
                    f"Forbidden >\nUser - {ctx.author} ({ctx.author.id})\nContent - {ctx.message.content}\nGuild - {ctx.guild.name} ({ctx.guild.id})",
                    "명령어 처리 기록",
                    ctx.bot.user.avatar_url,
                )
            else:
                await ctx.send("해당 단어는 차단 대상이나, 관리 권한으로 명령어를 실행했습니다.")
                await self.hook.terminal(
                    0,
                    f"Manager Bypassed >\nUser - {ctx.author} ({ctx.author.id})\nContent - {ctx.message.content}\nGuild - {ctx.guild.name} ({ctx.guild.id})",
                    "명령어 처리 기록",
                    ctx.bot.user.avatar_url,
                )
                return True
        elif not users and ctx.command.name != "가입":
            await self.hook.terminal(
                0,
                f"Cancelled >\nUser - {ctx.author} ({ctx.author.id})\nContent - {ctx.message.content}\nGuild - {ctx.guild.name} ({ctx.guild.id})",
                "명령어 처리 기록",
                ctx.bot.user.avatar_url,
            )
            raise NoReg()
        else:
            await self.hook.terminal(
                0,
                f"Processed >\nUser - {ctx.author} ({ctx.author.id})\nContent - {ctx.message.content}\nGuild - {ctx.guild.name} ({ctx.guild.id})",
                "명령어 처리 기록",
                ctx.bot.user.avatar_url,
            )
            return True
        embed = discord.Embed(
            title=f"이런, {ctx.author}님은 차단되셨어요.",
            description=f"""
차단에 관해서는 지원 서버를 방문해주세요.
사유 : {reason}
관리자 : {admin}
차단 시각 : {time}
            """,
            timestamp=datetime.datetime.utcnow(),
            color=0xFF3333,
        )
        embed.set_author(name="이용 제한", icon_url=ctx.bot.user.avatar_url)
        raise Forbidden(embed)
