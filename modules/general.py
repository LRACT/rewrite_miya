import datetime
import locale
import os
import random
import typing

import aiohttp
import discord
import koreanbots
import psutil
from discord.ext import commands

from lib import config
from lib import utils

locale.setlocale(locale.LC_ALL, "")


class General(commands.Cog, name="일반"):
    """일반적이고 다양한 기능들"""
    def __init__(self, miya):
        self.miya = miya
        self.check = utils.Check()

    @commands.command(name="문의", aliases=["지원"])
    async def _support(self, ctx):
        await ctx.reply(
            "<:cs_id:659355469034422282> 미야에 관해 문의할 것이 있으시다면, 아래 지원 서버로 접속해주세요.\nhttps://discord.gg/tu4NKbEEnn"
        )

    @commands.command(name="도움말", aliases=["도움", "명령어"])
    @commands.bot_has_permissions(embed_links=True)
    async def _help(self, ctx, *, input: typing.Optional[str]):
        """
        미야야 도움말 [ 확장 이름 ]


        미야에게 등록된 확장과 명령어를 불러옵니다.
        """
        embed = None
        if not input:
            embed = discord.Embed(
                title="미야 사용법",
                description=f"`미야야 도움말 < 확장 이름 >`을 사용해 더 많은 정보를 보실 수 있어요!",
                color=0x5FE9FF,
                timestamp=datetime.datetime.utcnow(),
            )
            cogs_desc = ""
            for cog in self.miya.cogs:
                if (len(self.miya.get_cog(cog).get_commands()) >= 1
                        and str(cog) not in config.Hidden):
                    cogs_desc += f"`{cog}` - {self.miya.cogs[cog].__doc__}\n"
            embed.add_field(name="확장 목록", value=cogs_desc, inline=False)
            commands_desc = ""
            for command in self.miya.walk_commands():
                if not command.cog_name and not command.hidden:
                    temp = command.help.split("\n")
                    commands_desc += f"{temp[0]} - {temp[3]}\n"
            if commands_desc:
                embed.add_field(name="확장에 포함되지 않는 명령어 목록",
                                value=commands_desc,
                                inline=False)
            embed.add_field(
                name="미야에 대하여",
                value=
                f"Powered by Team Urtica with ❤ in discord.py\n봇에 대한 정보는 `미야야 미야` 명령어를 참고하세요!",
            )
        else:
            for cog in self.miya.cogs:
                if str(cog) == input:
                    embed = discord.Embed(
                        title=f"{cog} 확장의 명령어",
                        description=self.miya.cogs[cog].__doc__,
                        color=0x5FE9FF,
                        timestamp=datetime.datetime.utcnow(),
                    )
                    for command in self.miya.get_cog(cog).get_commands():
                        if not command.hidden or self.check.owner(ctx):
                            embed.add_field(
                                name=command.help.split("\n")[0],
                                value=command.help.split("\n")[3],
                                inline=False,
                            )
                    if len(embed.fields) < 1:
                        embed = discord.Embed(
                            title="음, 무엇을 말하시는 건지 모르겠네요.",
                            description=f"`{cog}` 확장은 지금 사용할 수 있는 명령어가 없어요.",
                            color=0xFF3333,
                            timestamp=datetime.datetime.utcnow(),
                        )
                    break
                else:
                    embed = discord.Embed(
                        title="음, 무엇을 말하시는 건지 모르겠네요.",
                        description=f"`{input}`(이)라는 확장은 존재하지 않아요.",
                        color=0xFF3333,
                        timestamp=datetime.datetime.utcnow(),
                    )
        embed.set_footer(text="미야를 사용해주셔서 감사합니다!")
        embed.set_author(name="도움말", icon_url=self.miya.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(name="핑")
    async def ping(self, ctx):
        """
        미야야 핑


        미야의 지연 시간을 표시합니다.
        """
        first_time = datetime.datetime.utcnow()
        m = await ctx.reply("지연 시간을 계산합니다...")
        last_time = datetime.datetime.utcnow()
        asdf = str(last_time - first_time)[6:]
        msg_latency = round(float(asdf) * 1000, 2)
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(
            psutil.Process(os.getpid()).create_time())
        shard = self.miya.get_shard(ctx.guild.shard_id)
        bot_latency = round(shard.latency * 1000, 2)
        embed = discord.Embed(color=0x5FE9FF,
                              timestamp=datetime.datetime.utcnow())
        embed.add_field(name="API 지연 시간",
                        value=f"{bot_latency}ms",
                        inline=False)
        embed.add_field(name="메시지 지연 시간",
                        value=f"{msg_latency}ms",
                        inline=False)
        embed.add_field(name="구동 시간", value=str(uptime).split(".")[0])
        embed.set_thumbnail(
            url=ctx.author.avatar_url_as(static_format="png", size=2048))
        embed.set_author(name=f"#{ctx.guild.shard_id} | 지연 시간",
                         icon_url=self.miya.user.avatar_url)
        await m.edit(content=":ping_pong: Pong!", embed=embed)

    @commands.command(name="초대")
    async def _invite(self, ctx):
        """
        미야야 초대


        미야의 초대 링크를 표시합니다.
        """
        embed = discord.Embed(
            description=
            "[여기](https://discord.com/api/oauth2/authorize?client_id=720724942873821316&permissions=2147483647&redirect_uri=https%3A%2F%2Fmiya.kro.kr&response_type=code&scope=bot%20identify%20email)를 클릭하면 초대하실 수 있어요!",
            color=0x5FE9FF,
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_author(name="미야를 초대하시겠어요?",
                         icon_url=self.miya.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(name="골라", aliases=["골라줘"])
    async def _select(self, ctx, *args):
        """
        미야야 골라 < 단어 1 > < 단어 2 > [ 단어 3 ] ...


        미야가 단어 중 랜덤하게 하나를 선택해줍니다.
        """
        if not args or len(args) <= 1:
            raise commands.BadArgument
        else:
            select = random.choice(args)
            embed = discord.Embed(description=select, color=0x5FE9FF)
            embed.set_author(name="미야의 선택은...",
                             icon_url=self.miya.user.avatar_url)
            await ctx.reply(embed=embed)

    @commands.command(name="말해", aliases=["말해줘"])
    async def _say(self, ctx, *, text):
        """
        미야야 말해 < 할말 >


        미야가 당신이 한 말을 조금 가공해서(?) 따라합니다.
        """
        embed = discord.Embed(description=text, color=0x5FE9FF)
        embed.set_author(name=f"{ctx.author}님이 말하시길...",
                         icon_url=ctx.author.avatar_url)
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(embed=embed)

    @commands.command(name="하트")
    async def _vote(self, ctx, user: typing.Optional[discord.User] = None):
        """
        미야야 하트 [ @유저 ]


        한국 디스코드 봇 리스트의 미야에게 하트를 눌러주셨는지 확인합니다.
        """
        async with ctx.channel.typing():
            if user is None:
                user = ctx.author
            try:
                response = await self.miya.koreanbots.getVote(user.id)
            except koreanbots.NotFound:
                await ctx.reply(
                    f":broken_heart: **{user}**님은 미야에게 하트를 눌러주지 않으셨어요...\n하트 누르기 : https://koreanbots.dev/bots/720724942873821316"
                )
            else:
                if response.voted:
                    await ctx.reply(
                        f":heart: **{user}**님은 미야에게 하트를 눌러주셨어요!\n하트 누르기 : https://koreanbots.dev/bots/720724942873821316"
                    )
                else:
                    await ctx.reply(
                        f":broken_heart: **{user}**님은 미야에게 하트를 눌러주지 않으셨어요...\n하트 누르기 : https://koreanbots.dev/bots/720724942873821316"
                    )

    @commands.command(name="오리", aliases=["랜덤오리"])
    async def _duck(self, ctx):
        """
        미야야 오리


        랜덤으로 아무 오리 사진이나 가져옵니다.
        """
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        "https://random-d.uk/api/v2/quack") as response:
                    p = await response.json()
                    duck = discord.Embed(color=0xFFFCC9,
                                         timestamp=datetime.datetime.utcnow())
                    duck.set_image(url=p["url"])
                    duck.set_author(name="어떠한 오리 사진에 대하여",
                                    icon_url=self.miya.user.avatar_url)
                    duck.set_footer(text=p["message"])
                    await ctx.reply(embed=duck)


def setup(miya):
    miya.add_cog(General(miya))
