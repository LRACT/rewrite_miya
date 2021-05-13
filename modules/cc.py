import datetime
import locale
import random

import aiohttp
import discord
import koreanbots
from discord.ext import commands

from lib import config
from lib import utils
from lib.utils import Forbidden
from lib.utils import Maintaining
from lib.utils import NoReg
from lib.utils import sql

locale.setlocale(locale.LC_ALL, "")

Hook = utils.Hook()
Check = utils.Check()


def has_no_symbols():
    async def search(ctx):
        if (
            "\\" not in ctx.message.content
            and '"' not in ctx.message.content
            and "'" not in ctx.message.content
        ):
            return True
        raise commands.BadArgument

    return commands.check(search)


class CC(commands.Cog, name="기억"):
    """미야를 똑똑하게 만들기 프로젝트"""

    def __init__(self, miya):
        self.miya = miya

    @commands.command(name="기억해", aliases=["배워"])
    @has_no_symbols()
    async def _learn(self, ctx, word, *, value):
        word.lower()
        try:
            response = await self.miya.koreanbots.getVote(ctx.author.id)
        except koreanbots.NotFound:
            await ctx.reply(
                f":broken_heart: 미야에게 무언가를 가르치려면 `하트`를 눌러야 해요!\n하트 누르기 : https://koreanbots.dev/bots/720724942873821316"
            )
        else:
            if response.voted:
                embed = discord.Embed(
                    title="정말로 미야에게 이렇게 가르칠까요?",
                    description=f"등록되면 미야가 `{word}`라고 물어봤을 때```{value}```(이)라고 답할거에요.\n \n*부적절한 어휘 및 답변의 경우 예고 없이 삭제될 수 있어요.*",
                    color=0x5FE9FF,
                    timestamp=datetime.datetime.utcnow(),
                )
                embed.set_author(name="가르치기", icon_url=self.miya.user.avatar_url)
                embed.set_thumbnail(
                    url=ctx.author.avatar_url_as(static_format="png", size=2048)
                )
                embed.set_footer(text="미야를 똑똑하게 만들기 프로젝트")
                msg = await ctx.reply(embed=embed)
                await msg.add_reaction("<:cs_yes:659355468715786262>")
                await msg.add_reaction("<:cs_no:659355468816187405>")

                def check(reaction, user):
                    return reaction.message.id == msg.id and user == ctx.author

                try:
                    reaction, user = await self.miya.wait_for(
                        "reaction_add", timeout=60, check=check
                    )
                except:
                    await msg.delete()
                else:
                    if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
                        rows = await sql(0, f"SELECT * FROM `cc` ORDER BY `no` DESC")
                        number = int(rows[0][0]) + 1
                        await sql(
                            1,
                            f"INSERT INTO `cc`(`no`, `word`, `value`, `user`, `disabled`) VALUES('{number}', '{word}', '{value}', '{ctx.author.id}', 'false')",
                        )
                        embed = discord.Embed(
                            title="가르쳐주셔서 고마워요!",
                            description=f"이제 `{word}`에 이렇게 답할거에요:\n```{value}```",
                            color=0x5FE9FF,
                            timestamp=datetime.datetime.utcnow(),
                        )
                        embed.set_author(
                            name="가르치기", icon_url=self.miya.user.avatar_url
                        )
                        embed.set_thumbnail(
                            url=ctx.author.avatar_url_as(static_format="png", size=2048)
                        )
                        embed.set_footer(text="미야를 똑똑하게 만들기 프로젝트")
                        await msg.edit(embed=embed)
                    else:
                        await msg.delete()
            else:
                await ctx.reply(
                    f":broken_heart: 미야에게 무언가를 가르치려면 `하트`를 눌러야 해요!\n하트 누르기 : https://koreanbots.dev/bots/720724942873821316"
                )


def setup(miya):
    miya.add_cog(CC(miya))
