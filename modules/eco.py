import datetime
import random
import typing

import discord
from discord.ext import commands

from lib.utils import sql


class Economy(commands.Cog, name="경제"):
    """[ 개발 중 ] 미야로 돈벌기 ㄹㅇㅋㅋ"""

    def __init__(self, miya):
        self.miya = miya

    def in_guild():
        def predicate(ctx):
            return ctx.guild.id == 564418977627897887

        return commands.check(predicate)

    @commands.command(name="지갑", aliases=["돈", "잔고"])
    @in_guild()
    async def _wallet(self, ctx, user: typing.Optional[discord.User] = None):
        """
        미야야 지갑 [ @유저 ]


        지정한 유저( 혹은 본인 )의 지갑 정보를 확인합니다.
        """
        if user is None:
            user = ctx.author
        rows = await sql(0,
                         f"SELECT * FROM `users` WHERE `user` = '{user.id}'")
        if not rows:
            await ctx.reply(
                f"<:cs_no:659355468816187405> **{user}**님은 미야 서비스에 가입하지 않으셨어요."
            )
        else:
            embed = discord.Embed(
                title=f"💳 {user}님의 지갑 정보",
                timestamp=datetime.datetime.utcnow(),
                color=0x5FE9FF,
            )
            embed.add_field(name="가지고 있는 코인",
                            value=f"{rows[0][1]}개",
                            inline=False)
            embed.add_field(name="곧 더 많은 기능이 찾아옵니다...",
                            value="새로운 기능도 많이 기대해주세요!",
                            inline=False)
            embed.set_thumbnail(
                url=user.avatar_url_as(static_format="png", size=2048))
            embed.set_author(name="지갑", icon_url=self.miya.user.avatar_url)
            await ctx.reply(embed=embed)

    @commands.command(name="돈받기")
    @commands.cooldown(rate=1, per=43200, type=commands.BucketType.user)
    @in_guild()
    async def _money(self, ctx):
        """
        미야야 돈받기


        300 코인을 지급합니다. 12시간에 한 번만 사용 가능합니다.
        """
        rows = await sql(
            0, f"SELECT * FROM `users` WHERE `user` = '{ctx.author.id}'")
        plus = int(rows[0][1]) + 300
        await sql(
            1,
            f"UPDATE `users` SET `money` = '{plus}' WHERE `user` = '{ctx.author.id}'"
        )
        await ctx.reply("🎋 당신의 잔고에 `300` 코인을 추가했어요!\n매 12시간마다 다시 지급받으실 수 있어요.")

    @commands.command(name="도박")
    @in_guild()
    async def _gamble(self, ctx, money):
        """
        미야야 도박 < 금액 >


        금액을 걸고 주사위 도박을 진행합니다.
        """
        rows = await sql(
            0, f"SELECT * FROM `users` WHERE `user` = '{ctx.author.id}'")
        if money in ["모두", "전체", "올인"]:
            money = rows[0][1]
        elif money.isdecimal() is not True:
            raise commands.BadArgument

        if int(rows[0][1]) == 0 or int(rows[0][1]) < int(money):
            await ctx.reply(f"🍋 코인이 부족해요! 현재 코인 : {rows[0][1]}개")
        else:
            user = random.randint(1, 6)
            bot = random.randint(1, 6)
            embed, rest = None, None
            if user < bot:
                embed = discord.Embed(
                    title=f"🎲 {ctx.author.name}님의 주사위 도박 결과",
                    timestamp=datetime.datetime.utcnow(),
                    color=0xFF9999,
                )
                embed.set_footer(text="모두 잃어버린 나")
                rest = int(rows[0][1]) - int(money)
            elif user == bot:
                embed = discord.Embed(
                    title=f"🎲 {ctx.author.name}님의 주사위 도박 결과",
                    timestamp=datetime.datetime.utcnow(),
                    color=0x333333,
                )
                embed.set_footer(text="그래도 잃지는 않은 나")
                rest = int(rows[0][1])
            elif user > bot:
                embed = discord.Embed(
                    title=f"🎲 {ctx.author.name}님의 주사위 도박 결과",
                    timestamp=datetime.datetime.utcnow(),
                    color=0x99FF99,
                )
                embed.set_footer(text="봇을 상대로 모든 것을 가져간 나")
                rest = int(rows[0][1]) + int(money)
            embed.set_author(name="카케구루이", icon_url=self.miya.user.avatar_url)
            embed.set_thumbnail(
                url=ctx.author.avatar_url_as(static_format="png", size=2048))
            embed.add_field(name="미야의 주사위", value=f"`🎲 {bot}`", inline=True)
            embed.add_field(name=f"{ctx.author.name}님의 주사위",
                            value=f"`🎲 {user}`",
                            inline=True)
            await sql(
                1,
                f"UPDATE `users` SET `money` = '{rest}' WHERE `user` = '{ctx.author.id}'",
            )
            await ctx.reply(embed=embed)

    @commands.command(name="매수")
    @in_guild()
    async def _buy(self, ctx, stock, value):
        if stock not in ["Simplified", "Qualified", "Sharklified"]:
            raise commands.BadArgument
        else:
            user = (await sql(
                0,
                f"SELECT * FROM `users` WHERE `user` = '{ctx.author.id}'"))[0]
            stat = (await
                    sql(0,
                        f"SELECT * FROM `stocks` WHERE `name` = '{stock}'"))[0]
            if value in ["모두", "전체", "올인"]:
                value = round(int(user[1]) / int(stat[1]))
            elif value.isdecimal() is not True:
                raise commands.BadArgument
            # todo 사는 것과 관련한 기능


def setup(miya):
    miya.add_cog(Economy(miya))
