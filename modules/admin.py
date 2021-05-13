import datetime
import locale
import typing

import discord
from discord.ext import commands

from lib import utils
from lib.utils import sql

locale.setlocale(locale.LC_ALL, "")

Hook = utils.Hook()
Check = utils.Check()
Get = utils.Get()


class Administration(commands.Cog, name="관리"):
    def __init__(self, miya):
        self.miya = miya

    def is_manager():
        return commands.check(Check.mgr)

    @commands.command(name="비활성화")
    @is_manager()
    async def _remove(self, ctx, number: int):
        await sql(1, f"UPDATE `cc` SET `disabled` = 'true` WHERE `no` = '{number}'")
        await ctx.message.add_reaction("<:cs_yes:659355468715786262>")

    @commands.command(name="점검")
    @commands.is_owner()
    async def _maintain(self, ctx, *, reason: typing.Optional[str] = "점검 중입니다."):
        """
        미야야 점검 [ 사유 ]


        점검 모드를 관리합니다.
        점검 모드가 활성화된 동안은 일반 유저의 명령어 사용이 중단됩니다.
        """
        msg = await ctx.reply(
            f":grey_question: 점검 모드를 어떻게 할까요?\n<:cs_yes:659355468715786262> - 켜기\n<:cs_no:659355468816187405> - 끄기"
        )
        await msg.add_reaction("<:cs_yes:659355468715786262>")
        await msg.add_reaction("<:cs_no:659355468816187405>")

        def check(reaction, user):
            return reaction.message.id == msg.id and user == ctx.author

        try:
            reaction, user = await self.miya.wait_for(
                "reaction_add", timeout=30, check=check
            )
        except:
            await msg.clear_reaction()
        else:
            if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
                operation = "true"
                await sql(1, f"UPDATE `miya` SET `maintained` = '{operation}'")
                await sql(1, f"UPDATE `miya` SET `mtr` = '{reason}'")
                await msg.edit(content=f"<:cs_yes:659355468715786262> 점검 모드를 활성화했습니다.")
            else:
                operation = "false"
                await sql(1, f"UPDATE `miya` SET `maintained` = '{operation}'")
                await msg.edit(content=f"<:cs_yes:659355468715786262> 점검 모드를 비활성화했습니다.")

    @commands.command(name="SQL")
    @commands.is_owner()
    async def _sql(self, ctx, work, *, sql):
        """
        미야야 SQL < fetch / commit > < SQL 명령 >


        SQL 구문을 실행하고, 리턴값을 반환합니다.
        """
        if work == "fetch":
            a = ""
            rows = await sql(0, sql)
            for row in rows:
                a += f"{row}\n"
            if len(a) > 1900:
                await ctx.reply(f"{a[:1900]}\n메시지 길이 제한으로 1900자까지만 출력되었습니다.")
                print(a)
            else:
                await ctx.reply(a)
        elif work == "commit":
            result = await sql(1, sql)
            await ctx.reply(result)
        else:
            raise commands.BadArgument

    @commands.command(name="제한")
    @is_manager()
    async def _black_word(self, ctx, todo, *, word):
        """
        미야야 제한 < 추가 / 삭제 > < 단어 >


        자동 차단 단어를 관리합니다.
        """
        if todo == "추가":
            result = await sql(1, f"INSERT INTO `forbidden`(`word`) VALUES('{word}')")
            if result == "SUCCESS":
                await ctx.message.add_reaction("<:cs_yes:659355468715786262>")
                await Hook.terminal(
                    1,
                    f"New Forbidden >\nAdmin - {ctx.author} ({ctx.author.id})\nPhrase - {word}",
                    "제한 기록",
                    self.miya.user.avatar_url,
                )
        elif todo == "삭제":
            result = await sql(1, f"DELETE FROM `forbidden` WHERE `word` = '{word}'")
            if result == "SUCCESS":
                await ctx.message.add_reaction("<:cs_yes:659355468715786262>")
                await Hook.terminal(
                    1,
                    f"Removed Forbidden >\nAdmin - {ctx.author} ({ctx.author.id})\nPhrase - {word}",
                    "제한 기록",
                    self.miya.user.avatar_url,
                )
        else:
            raise commands.BadArgument

    @commands.command(name="블랙")
    @is_manager()
    async def blacklist_management(
        self, ctx, todo, id, *, reason: typing.Optional[str] = "사유가 지정되지 않았습니다."
    ):
        """
        미야야 블랙 < 추가 / 삭제 > < ID > [ 사유 ]


        ID를 통해 유저나 서버의 블랙리스트를 관리합니다.
        """
        time = Get.localize(datetime.datetime.utcnow())
        if todo == "추가":
            result = await sql(
                1,
                f"INSERT INTO `blacklist`(`id`, `reason`, `admin`, `datetime`) VALUES('{id}', '{reason}', '{ctx.author.id}', '{time}')",
            )
            if result == "SUCCESS":
                await ctx.message.add_reaction("<:cs_yes:659355468715786262>")
                await Hook.terminal(
                    1,
                    f"New Block >\nVictim - {id}\nAdmin - {ctx.author} ({ctx.author.id})\nReason - {reason}",
                    "제한 기록",
                    self.miya.user.avatar_url,
                )
            else:
                await ctx.message.add_reaction("<:cs_no:659355468816187405>")
        elif todo == "삭제":
            result = await sql(1, f"DELETE FROM `blacklist` WHERE `id` = '{id}'")
            if result == "SUCCESS":
                await ctx.message.add_reaction("<:cs_yes:659355468715786262>")
                await Hook.terminal(
                    1,
                    f"Removed Block >\nUnblocked - {id}\nAdmin - {ctx.author} ({ctx.author.id})",
                    "제한 기록",
                    self.miya.user.avatar_url,
                )
            else:
                await ctx.message.add_reaction("<:cs_no:659355468816187405>")
        else:
            raise commands.BadArgument

    @commands.command(name="탈주")
    @commands.is_owner()
    async def _leave(self, ctx, guild_id: int):
        """
        미야야 탈주 < ID >


        지정한 서버에서 미야가 나갑니다.
        """
        guild = self.miya.get_guild(int(guild_id))
        if guild is not None:
            await guild.leave()
            await ctx.message.add_reaction("<:cs_yes:659355468715786262>")
        else:
            await ctx.reply("<:cs_no:659355468816187405> 서버를 발견하지 못했어요.")


def setup(miya):
    miya.add_cog(Administration(miya))
