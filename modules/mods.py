import locale
import typing

import discord
from discord.ext import commands

from lib.utils import sql

locale.setlocale(locale.LC_ALL, "")


class Moderation(commands.Cog, name="관리"):
    """쉽고 빠른 ||~~군기 잡기~~|| 유저 관리"""

    def __init__(self, miya):
        self.miya = miya

    @commands.command(name="뮤트")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def _mute(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: typing.Optional[str] = "사유가 지정되지 않았어요.",
    ):
        """
        미야야 뮤트 < @유저 > [ 사유 ]


        지정된 뮤트 역할을 유저에게 적용합니다. 뮤트 역할의 설정이 필요합니다.
        """
        rows = await sql(
            0, f"SELECT * FROM `guilds` WHERE `guild` = '{ctx.guild.id}'")
        role = ctx.guild.get_role(int(rows[0][2]))
        if role is not None and role < ctx.guild.me.top_role:
            if role not in member.roles:
                if member.guild_permissions.administrator:
                    await ctx.reply(
                        f"<:cs_no:659355468816187405> 지정한 유저가 서버의 관리자 권한을 가지고 있어 취소되었어요."
                    )
                else:
                    await member.add_roles(role, reason=reason)
                    await ctx.reply(
                        f"<:mute:761151751583301682> **{member}**님을 뮤트했어요.\n사유 : *{reason}*"
                    )
            else:
                await ctx.reply(
                    f"<:mute:761151751583301682> 그 유저는 이미 뮤트되어 있어요!")
        else:
            await ctx.reply(
                f"<:cs_no:659355468816187405> 이 명령어를 실행하려면 뮤트에 사용할 역할이 지정되어 있어야 해요. `미야야 뮤트설정 `@역할`` 명령어를 사용해 설정을 완료해주세요."
            )

    @commands.command(name="언뮤트")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def _unmute(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: typing.Optional[str] = "사유가 지정되지 않았어요.",
    ):
        """
        미야야 언뮤트 < @유저 > [ 사유 ]


        유저의 뮤트 상태를 해제합니다. 뮤트 역할의 설정이 필요합니다.
        """
        rows = await sql(
            0, f"SELECT * FROM `guilds` WHERE `guild` = '{ctx.guild.id}'")
        role = ctx.guild.get_role(int(rows[0][2]))
        if role is not None and role < ctx.guild.me.top_role:
            if role in member.roles:
                await member.remove_roles(role, reason=reason)
                await ctx.reply(
                    f"<:mic:761152232447148042> **{member}**님의 뮤트 상태를 해제했어요.\n사유 : {reason}"
                )
            else:
                await ctx.reply(f"<:mic:761152232447148042> 그 유저는 뮤트되지 않았어요!")
        else:
            await ctx.reply(
                f"<:cs_no:659355468816187405> 이 명령어를 실행하려면 뮤트에 사용할 역할이 지정되어 있어야 해요. `미야야 뮤트설정 `@역할`` 명령어를 사용해 설정을 완료해주세요."
            )

    @commands.command(name="슬로우", aliases=["슬로우모드"])
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def _slowmode(self, ctx, number: str):
        """
        미야야 슬로우 < 1 ~ 21600 사이의 정수 / 끄기 >


        실행한 채널의 메시지 딜레이를 설정합니다.
        """
        if not number.isdecimal() and number != "끄기":
            raise commands.BadArgument
        elif number == "끄기":
            await ctx.channel.edit(slowmode_delay=0)
            await ctx.reply(f":hourglass: 채널의 메시지 딜레이를 삭제했어요!")
        elif int(number) > 21600 or int(number) <= 0:
            raise commands.BadArgument
        else:
            await ctx.channel.edit(slowmode_delay=int(number))
            await ctx.reply(
                f":hourglass: 채널의 메시지 딜레이를 {number}초로 설정했어요!\n \n`채널 관리` 혹은 `메시지 관리` 권한을 가진 사람에게는 적용되지 않아요.\n채널의 메시지 딜레이를 취소하려면 `미야야 슬로우 끄기` 명령어를 사용해주세요."
            )

    @commands.command(name="추방", aliases=["킥"])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def _kick(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: typing.Optional[str] = "사유가 지정되지 않았어요.",
    ):
        """
        미야야 추방 < 유저 > [ 사유 ]


        서버에서 유저를 추방합니다.
        """
        if member.top_role < ctx.guild.me.top_role:
            try:
                await member.send(
                    f"<a:ban_cat:761149577444720640> **{ctx.guild.name}** 서버에서 추방당하셨어요.\n추방한 관리자 : {ctx.author}\n사유 : {reason}"
                )
            except:
                pass
            await ctx.guild.kick(member, reason=reason)
            await ctx.reply(
                f"<a:ban_cat:761149577444720640> **{member}**님을 서버에서 추방했어요!\n사유 : {reason}"
            )
        else:
            await ctx.reply(
                f"<:cs_no:659355468816187405> 미야가 추방하려는 유저보다 권한이 낮거나 같아 추방하지 못했어요."
            )

    @commands.command(name="차단", aliases=["밴", "벤"])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def _ban(
        self,
        ctx,
        user: discord.Member,
        delete: typing.Optional[int] = 0,
        *,
        reason: typing.Optional[str] = "사유가 지정되지 않았어요.",
    ):
        """
        미야야 차단 < 유저 > [ 메시지 삭제 일 수 ( ~7일까지 ) ] [ 사유 ]


        서버에서 유저를 차단합니다.
        """
        if user.top_role < ctx.guild.me.top_role:
            try:
                await user.send(
                    f"<a:ban_guy:761149578216603668> {ctx.author.mention} **{ctx.guild.name} 서버에서 영구적으로 차단당하셨어요.\n차단한 관리자 : {ctx.author}\n사유 : {reason}"
                )
            except:
                pass
            await ctx.guild.ban(user,
                                delete_message_days=delete,
                                reason=reason)
            await ctx.reply(
                f"<a:ban_guy:761149578216603668> **{user}**님을 서버에서 차단했어요!\n메시지 삭제 일 수 : {delete}일\n사유 : {reason}"
            )
        else:
            await ctx.reply(
                f"<:cs_no:659355468816187405> 미야가 차단하려는 유저보다 권한이 낮거나 같아 차단하지 못했어요."
            )

    @commands.command(name="청소", aliases=["삭제"])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.channel)
    async def _purge(self, ctx, num: int):
        """
        미야야 청소 < 1 ~ 100 사이의 정수 >


        설정한 갯수 만큼의 메세지를 채널에서 삭제합니다.
        """
        if num <= 100 and num > 0:
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit=num)
            await ctx.send(
                f"<:cs_trash:659355468631769101> {ctx.author.mention} {len(deleted)}개의 메세지를 삭제했어요!",
                delete_after=3,
            )
        else:
            raise commands.BadArgument


def setup(miya):
    miya.add_cog(Moderation(miya))
