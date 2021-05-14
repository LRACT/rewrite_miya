import datetime
import random
import typing

import discord
from discord.ext import commands

from lib.utils import sql


class Economy(commands.Cog, name="경제"):
    """미야와 함께 갑부가 되기 3분 강좌"""
    def __init__(self, miya):
        self.miya = miya

    @commands.command(name="지갑", aliases=["돈", "잔고"])
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
    async def _gamble(self, ctx, money):
        """
        미야야 주사위 < 금액 >


        미야와 주사위 도박을 진행합니다.
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
            user1 = random.randint(1, 6)
            user2 = random.randint(1, 6)
            bot1 = random.randint(1, 6)
            bot2 = random.randint(1, 6)
            user = user1 + user2
            bot = bot1 + bot2
            embed, rest = None, None
            if user < bot:
                embed = discord.Embed(
                    title=f"🎲 {ctx.author.name}님의 주사위 도박 결과",
                    timestamp=datetime.datetime.utcnow(),
                    color=0xFF9999,
                )
                embed.set_footer(text="모두 잃어버린 나")
                minus = int(money) * (bot - user)
                if minus < int(rows[0][1]):
                    rest = int(rows[0][1]) - minus
                else:
                    rest = 0
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
                plus = int(money) * (bot - user)
                rest = int(rows[0][1]) + plus
            embed.set_author(name="카케구루이", icon_url=self.miya.user.avatar_url)
            embed.set_thumbnail(
                url=ctx.author.avatar_url_as(static_format="png", size=2048))
            embed.add_field(name="미야의 주사위",
                            value=f"🎲 `{bot1}`, `{bot2}`",
                            inline=True)
            embed.add_field(
                name=f"{ctx.author.name}님의 주사위",
                value=f"🎲 `{user1}`, `{user2}`",
                inline=True,
            )
            await sql(
                1,
                f"UPDATE `users` SET `money` = '{rest}' WHERE `user` = '{ctx.author.id}'",
            )
            await ctx.reply(embed=embed)

    @commands.command(name="홀짝")
    async def _simple(self, ctx, money):
        """
        미야야 홀짝 < 금액 >


        미야와 홀짝 도박을 진행합니다.
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
            msg = await ctx.reply(
                "🎲 홀짝 도박을 시작할게요! 당신의 선택은 무엇인가요?\n1️⃣ - 홀\n2️⃣ - 짝")
            await msg.add_reaction("1️⃣")
            await msg.add_reaction("2️⃣")

            def check(reaction, user):
                return reaction.message.id == msg.id and user == ctx.author

            try:
                reaction, user = await self.miya.wait_for("reaction_add",
                                                          timeout=30,
                                                          check=check)
            except:
                await msg.edit(
                    content="⚡ 고민되는 선택인가요? 그럼, 좀 더 고민해보시고 다시 시도해주세요.",
                    delete_after=10)
            else:
                list = None
                if str(reaction.emoji) == "1️⃣":
                    list = ["홀", 1, 3, 5, 7, 9]
                elif str(reaction.emoji) == "2️⃣":
                    list = ["짝", 2, 4, 6, 8, 10]
                result = random.randint(1, 10)
                if result in list:
                    receive = int(rows[0][1]) + int(money)
                    await sql(
                        1,
                        f"UPDATE `users` SET `money` = '{receive}' WHERE `user` = {ctx.author.id}",
                    )
                    await msg.edit(
                        content=
                        f"🕹 축하드려요! 뭐, 이런 게 초보자의 행운이려나요.\n당신의 선택 - `{list[0]}`, 결과 - `{result}`"
                    )
                else:
                    receive = int(rows[0][1]) - int(money)
                    await sql(
                        1,
                        f"UPDATE `users` SET `money` = '{receive}' WHERE `user` = {ctx.author.id}",
                    )
                    await msg.edit(
                        content=
                        f"🎬 안타깝네요. 뭐, 늘 이길 수만은 없는 법이니까요.\n당신의 선택 - `{list[0]}`, 결과 - `{result}`"
                    )


def setup(miya):
    miya.add_cog(Economy(miya))
