import datetime
import locale
import os
import sys
import typing

import discord
from discord.ext import commands
from EZPaginator import Paginator

from lib import utils
from lib.utils import sql

locale.setlocale(locale.LC_ALL, "")

Check = utils.Check()


class Administration(commands.Cog, name="미야 유지보수"):
    """미야의 유지 관리 및 보수에 사용되는 것들"""
    def __init__(self, miya):
        self.miya = miya
        self.black = utils.Blacklisting()

    def is_manager():
        return commands.check(Check.mgr)

    def is_owner():
        return commands.check(Check.owner)

    @commands.command(name="재시작", hidden=True)
    @is_owner()
    async def _restart(self, ctx):
        """
        미야야 재시작


        현재 프로세스를 완전히 닫고 재시작합니다.
        """
        msg = await ctx.reply(
            f":grey_question: 미야를 정말로 재시작하시겠어요? 진행 중이던 작업이 사라질 수 있어요!\n<:cs_yes:659355468715786262> - 네\n<:cs_no:659355468816187405> - 아니오"
        )
        await msg.add_reaction("<:cs_yes:659355468715786262>")
        await msg.add_reaction("<:cs_no:659355468816187405>")

        def check(reaction, user):
            return reaction.message.id == msg.id and user == ctx.author

        try:
            reaction, user = await self.miya.wait_for("reaction_add",
                                                      timeout=30,
                                                      check=check)
        except:
            await msg.delete()
        else:
            if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
                await msg.edit(content="🎬 미야가 곧 재시작됩니다...")
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                await msg.delete()

    @commands.command(name="종료", hidden=True)
    @is_owner()
    async def _shutdown(self, ctx):
        """
        미야야 종료


        미야를 로그아웃시키고 프로세스를 닫습니다.
        """
        msg = await ctx.reply(
            f":grey_question: 미야를 정말로 종료하시겠어요? 진행 중이던 작업이 사라질 수 있어요!\n<:cs_yes:659355468715786262> - 예\n<:cs_no:659355468816187405> - 아니오"
        )
        await msg.add_reaction("<:cs_yes:659355468715786262>")
        await msg.add_reaction("<:cs_no:659355468816187405>")

        def check(reaction, user):
            return reaction.message.id == msg.id and user == ctx.author

        try:
            reaction, user = await self.miya.wait_for("reaction_add",
                                                      timeout=30,
                                                      check=check)
        except:
            await msg.delete()
        else:
            if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
                await msg.edit(content="🎬 미야가 곧 종료됩니다...")
                await self.miya.logout()
            else:
                await msg.delete()

    @commands.command(name="권한", hidden=True)
    @is_owner()
    async def _permission(self, ctx, user: discord.User, permission: str):
        """
        미야야 권한 < @유저 > < 설정할 권한 >


        유저의 권한을 설정합니다.
        """
        rows = await sql(0,
                         f"SELECT * FROM `users` WHERE `user` = '{user.id}'")
        if not rows:
            raise commands.BadArgument
        await sql(
            1,
            f"UPDATE `users` SET `permission` = '{permission}' WHERE `user` = '{user.id}'",
        )
        await ctx.message.add_reaction("<:cs_yes:659355468715786262>")

    @commands.command(name="비활성화", hidden=True)
    @is_manager()
    async def _remove(self, ctx, number: int):
        """
        미야야 비활성화 < 번호 >


        가르쳐진 지식을 비활성화합니다.
        """
        rows = await sql(0, f"SELECT * FROM `cc` WHERE `no` = '{number}'")
        if not rows:
            raise commands.BadArgument
        await sql(
            1, f"UPDATE `cc` SET `disabled` = 'true' WHERE `no` = '{number}'")
        await ctx.message.add_reaction("<:cs_yes:659355468715786262>")

    @commands.command(name="활성화", hidden=True)
    @is_manager()
    async def _active(self, ctx, number: int):
        """
        미야야 활성화 < 번호 >


        비활성화된 지식을 활성화합니다.
        """
        rows = await sql(0, f"SELECT * FROM `cc` WHERE `no` = '{number}'")
        if not rows:
            raise commands.BadArgument
        await sql(
            1, f"UPDATE `cc` SET `disabled` = 'false' WHERE `no` = '{number}'")
        await ctx.message.add_reaction("<:cs_yes:659355468715786262>")

    @commands.group(name="조회", hidden=True)
    @is_manager()
    async def checkout(self, ctx):
        """
        미야야 조회 < 유저 / 단어 > < 조회할 값 >


        유저 ID 혹은 단어에 대해서 미야가 알고 있는 내용을 조회합니다.
        """
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument

    @checkout.command(name="유저", hidden=True)
    @is_manager()
    async def _user(self, ctx, user_id):
        """
        미야야 조회 유저 < 유저 ID >


        해당 유저가 가르친 모든 내용을 조회합니다.
        """
        rows = await sql(
            0,
            f"SELECT * FROM `cc` WHERE `user` = '{user_id}' ORDER BY `no` ASC")
        embeds = []
        for i in range(len(rows)):
            embed = discord.Embed(
                title=f"{user_id}에 대한 지식 목록 ({i + 1} / {len(rows)})",
                color=0x5FE9FF,
                timestamp=datetime.datetime.utcnow(),
            )
            embed.add_field(name="지식 번호", value=rows[i][0], inline=False)
            embed.add_field(name="입력 내용", value=rows[i][1], inline=False)
            embed.add_field(name="답장 내용", value=rows[i][2], inline=False)
            embed.add_field(name="비활성화되었나요?", value=rows[i][4], inline=False)
            embed.set_author(name="커맨드 목록", icon_url=self.miya.user.avatar_url)
            embeds.append(embed)
        msg = await ctx.send(embed=embeds[0])
        page = Paginator(bot=self.miya, message=msg, embeds=embeds)
        await page.start()

    @checkout.command(name="단어", hidden=True)
    @is_manager()
    async def _word(self, ctx, word):
        """
        미야야 조회 단어 < 키워드 >


        키워드에 등록된 모든 내용을 조회합니다.
        """
        word.lower()
        rows = await sql(
            0, f"SELECT * FROM `cc` WHERE `word` = '{word}' ORDER BY `no` ASC")
        embeds = []
        for i in range(len(rows)):
            embed = discord.Embed(
                title=f"{word}에 대한 지식 목록 ({i + 1} / {len(rows)})",
                color=0x5FE9FF,
                timestamp=datetime.datetime.utcnow(),
            )
            embed.add_field(name="지식 번호", value=rows[i][0], inline=False)
            embed.add_field(name="답장 내용", value=rows[i][2], inline=False)
            embed.add_field(name="가르친 유저의 ID", value=rows[i][3], inline=False)
            embed.add_field(name="비활성화되었나요?", value=rows[i][4], inline=False)
            embed.set_author(name="커맨드 목록", icon_url=self.miya.user.avatar_url)
            embeds.append(embed)
        msg = await ctx.send(embed=embeds[0])
        page = Paginator(bot=self.miya, message=msg, embeds=embeds)
        await page.start()

    @commands.command(name="점검", hidden=True)
    @is_owner()
    async def _maintain(self,
                        ctx,
                        *,
                        reason: typing.Optional[str] = "점검 중입니다."):
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
            reaction, user = await self.miya.wait_for("reaction_add",
                                                      timeout=30,
                                                      check=check)
        except:
            await msg.delete()
        else:
            if str(reaction.emoji) == "<:cs_yes:659355468715786262>":
                operation = "true"
                await sql(1, f"UPDATE `miya` SET `maintained` = '{operation}'")
                await sql(1, f"UPDATE `miya` SET `mtr` = '{reason}'")
                await msg.edit(
                    content=f"<:cs_yes:659355468715786262> 점검 모드를 활성화했습니다.")
            else:
                operation = "false"
                await sql(1, f"UPDATE `miya` SET `maintained` = '{operation}'")
                await msg.edit(
                    content=f"<:cs_yes:659355468715786262> 점검 모드를 비활성화했습니다.")

    @commands.command(name="SQL", hidden=True)
    @is_owner()
    async def _sql(self, ctx, work, *, cmd):
        """
        미야야 SQL < fetch / commit > < SQL 명령 >


        SQL 구문을 실행하고, 리턴값을 반환합니다.
        """
        if work == "fetch":
            a = ""
            rows = await sql(0, cmd)
            for row in rows:
                a += f"{row}\n"
            if len(a) > 1900:
                await ctx.reply(f"{a[:1900]}\n메시지 길이 제한으로 1900자까지만 출력되었습니다.")
                print(a)
            else:
                await ctx.reply(a)
        elif work == "commit":
            result = await sql(1, cmd)
            await ctx.reply(result)
        else:
            raise commands.BadArgument

    @commands.command(name="제한", hidden=True)
    @is_manager()
    async def _black_word(self, ctx, todo, *, word):
        """
        미야야 제한 < 추가 / 삭제 > < 단어 >


        자동 차단 단어를 관리합니다.
        """
        if todo == "추가":
            await self.black.word(ctx, 0, word)
        elif todo == "삭제":
            await self.black.word(ctx, 1, word)
        else:
            raise commands.BadArgument

    @commands.command(name="블랙", hidden=True)
    @is_manager()
    async def blacklist_management(
        self,
        ctx,
        todo,
        user: discord.User,
        *,
        reason: typing.Optional[str] = "사유가 지정되지 않았습니다.",
    ):
        """
        미야야 블랙 < 추가 / 삭제 > < 유저 > [ 사유 ]


        유저의 미야 이용을 제한합니다.
        """
        if todo == "추가":
            await self.black.user(ctx, 0, user, reason)
        elif todo == "삭제":
            await self.black.user(ctx, 1, user, reason)
        else:
            raise commands.BadArgument

    @commands.command(name="탈주", hidden=True)
    @is_owner()
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
