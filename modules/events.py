import asyncio
import datetime
import json
import locale

import aiohttp
import discord
from discord.ext import commands

from lib import utils
from lib.utils import Forbidden, Maintaining, NoReg, sql

locale.setlocale(locale.LC_ALL, "")

Hook = utils.Hook()


class Listeners(commands.Cog, name="이벤트 리스너"):
    def __init__(self, miya):
        self.miya = miya

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard):
        await Hook.terminal(
            0,
            f"Shard Disconnected >\nShard ID - #{shard}",
            "샤드 기록",
            self.miya.user.avatar_url,
        )

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard):
        await Hook.terminal(
            0,
            f"Shard Resumed >\nShard ID - #{shard}",
            "샤드 기록",
            self.miya.user.avatar_url,
        )
        await self.miya.change_presence(
            status=discord.Status.idle,
            activity=discord.Game(f"#{shard} | 미야야 도움말"),
            shard_id=shard,
        )

    @commands.Cog.listener()
    async def on_shard_connect(self, shard):
        await Hook.terminal(
            0,
            f"Shard Connected >\nShard ID - #{shard}",
            "샤드 기록",
            self.miya.user.avatar_url,
        )
        await self.miya.change_presence(
            status=discord.Status.idle,
            activity=discord.Game(f"#{shard} | 미야야 도움말"),
            shard_id=shard,
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        perms = {
            "administrator": "관리자",
            "manage_guild": "서버 관리하기",
            "manage_roles": "역할 관리하기",
            "manage_permissions": "권한 관리하기",
            "manage_channels": "채널 관리하기",
            "kick_members": "멤버 추방하기",
            "ban_members": "멤버 차단하기",
            "manage_nicknames": "별명 관리하기",
            "manage_webhooks": "웹훅 관리하기",
            "manage_messages": "메시지 관리하기",
        }
        if isinstance(error, commands.CommandNotFound) or isinstance(
            error, commands.NotOwner
        ):
            return
        if isinstance(error, Forbidden):
            await ctx.reply(str(error), embed=error.embed)
        elif isinstance(error, NoReg) or isinstance(error, Maintaining):
            await ctx.reply(str(error))
        elif isinstance(error, discord.NotFound) or isinstance(
            error, commands.NoPrivateMessage
        ):
            return
        elif isinstance(error, discord.Forbidden):
            await ctx.reply(f"<:cs_no:659355468816187405> 권한 부족 등의 이유로 명령어 실행에 실패했어요.")
        elif isinstance(error, commands.MissingPermissions):
            mp = error.missing_perms
            p = perms[mp[0]]
            await ctx.reply(
                f"<:cs_no:659355468816187405> 당신은 이 명령어를 실행할 권한이 없어요.\n해당 명령어를 실행하려면 이 권한을 가지고 계셔야 해요. `{p}`"
            )
        elif isinstance(error, commands.BotMissingPermissions):
            mp = error.missing_perms
            p = perms[mp[0]]
            await ctx.reply(
                f"<:cs_no:659355468816187405> 미야에게 명령어를 실행할 권한이 부족해 취소되었어요.\n해당 명령어를 실행하려면 미야에게 이 권한이 필요해요. `{p}`"
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"<:cs_stop:665173353874587678> 잠시 기다려주세요. 해당 명령어를 사용하려면 {round(error.retry_after, 2)}초를 더 기다리셔야 해요.\n해당 명령어는 `{error.cooldown.per}`초에 `{error.cooldown.rate}`번만 사용할 수 있어요."
            )
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(
            error, commands.BadArgument
        ):
            if isinstance(error, commands.MemberNotFound) or isinstance(
                error, commands.UserNotFound
            ):
                await ctx.reply(
                    f":mag_right: `{error.argument}`(이)라는 유저를 찾을 수 없었어요. 정확한 유저를 지정해주세요!"
                )
            elif isinstance(error, commands.ChannelNotFound):
                await ctx.reply(
                    f":mag_right: `{error.argument}`(이)라는 채널을 찾을 수 없었어요. 정확한 채널을 지정해주세요!"
                )
            elif isinstance(error, commands.ChannelNotReadable):
                await ctx.reply(
                    f"<:cs_no:659355468816187405> `{error.argument}` 채널에 미야가 접근할 수 없어요. 미야가 읽을 수 있는 채널로 지정해주세요!"
                )
            elif isinstance(error, commands.RoleNotFound):
                await ctx.reply(
                    f":mag_right: `{error.argument}`(이)라는 역할을 찾을 수 없었어요. 정확한 역할을 지정해주세요!"
                )
            else:
                usage = ctx.command.help.split("\n")[0]
                await ctx.reply(
                    f"<:cs_console:659355468786958356> `{usage}`(이)가 올바른 명령어에요!"
                )
        else:
            await Hook.terminal(
                0,
                f"Error >\nContent - {ctx.message.content}\nException - {error}",
                "명령어 처리 기록",
                self.miya.user.avatar_url,
            )
            await ctx.reply(
                f":warning: 명령어 실행 도중 오류가 발생했어요.\n오류 해결을 위해 Discord 지원 서버로 문의해주세요. https://discord.gg/tu4NKbEEnn"
            )

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return

        if msg.channel.type == discord.ChannelType.private:
            return

        if (
            "discord.gg" in msg.content
            or "discord.com/invite" in msg.content
            or "discordapp.com/invite" in msg.content
        ):
            rows = await sql(
                0, f"SELECT * FROM `guilds` WHERE `guild` = '{msg.guild.id}'"
            )
            if rows:
                if rows[0][3] == "true":
                    if msg.channel.topic is None or "=무시" not in msg.channel.topic:
                        try:
                            await msg.delete()
                            await msg.channel.send(
                                f"<:cs_trash:659355468631769101> {msg.author.mention} 서버 설정에 따라 이 채널에는 Discord 초대 링크를 포스트하실 수 없어요."
                            )
                        except:
                            return

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await Hook.terminal(
            0,
            f"Join >\nGuild - {guild.name} ({guild.id})",
            "서버 입퇴장 기록",
            self.miya.user.avatar_url,
        )
        grows = await sql(0, f"SELECT * FROM `guilds` WHERE `guild` = '{guild.id}'")
        if not grows:
            g_result = await sql(
                1,
                f"INSERT INTO `guilds`(`guild`, `eventLog`, `muteRole`, `linkFiltering`, `warn_kick`) VALUES('{guild.id}', '1234', '1234', 'false', '0')",
            )
            default_join_msg = "{member}님 **{guild}**에 오신 것을 환영해요! 현재 인원 : {count}명"
            default_quit_msg = "{member}님 안녕히 가세요.. 현재 인원 : {count}명"
            m_result = await sql(
                1,
                f"INSERT INTO `membernoti`(`guild`, `channel`, `join_msg`, `remove_msg`) VALUES('{guild.id}', '1234', '{default_join_msg}', '{default_quit_msg}')",
            )
            if g_result == "SUCCESS" and m_result == "SUCCESS":
                await Hook.terminal(
                    0,
                    f"Registered >\nGuild - {guild.name} ({guild.id})",
                    "서버 등록 기록",
                    self.miya.user.avatar_url,
                )
                try:
                    embed = discord.Embed(
                        title="미야를 초대해주셔서 감사해요!",
                        description="""
`미야야 채널설정 공지 #채널` 명령어를 사용해 공지 채널을 설정해주세요.
미야에 관련된 문의 사항은 [지원 서버](https://discord.gg/tu4NKbEEnn)에서 하실 수 있어요!
미야의 더욱 다양한 명령어는 `미야야 도움말` 명령어로 살펴보세요!
                        """,
                        timestamp=datetime.datetime.utcnow(),
                        color=0x5FE9FF,
                    )
                    embed.set_author(name="반가워요!", icon_url=self.miya.user.avatar_url)
                    await guild.owner.send(
                        f"<:cs_notify:659355468904529920> {guild.owner.mention}",
                        embed=embed,
                    )
                except:
                    await Hook.terminal(
                        0,
                        f"Owner DM Failed >\nGuild - {guild.name} ({guild.id})",
                        "서버 입퇴장 기록",
                        self.miya.user.avatar_url,
                    )
            else:
                await Hook.terminal(
                    0,
                    f"Register Failed >\nGuild - {guild.name} ({guild.id})\nguilds Table - {g_result}\nmemberNoti Table - {m_result}",
                    "서버 등록 기록",
                    self.miya.user.avatar_url,
                )
                await guild.text_channels[0].send(
                    f"<:cs_stop:665173353874587678> {guild.owner.mention} 미야 설정이 정상적으로 완료되지 않았습니다.\n자세한 내용은 https://discord.gg/tu4NKbEEnn 으로 문의해주세요."
                )
        rows = await sql(0, f"SELECT * FROM `blacklist` WHERE `id` = '{guild.id}'")
        rows2 = await sql(
            0, f"SELECT * FROM `blacklist` WHERE `id` = '{guild.owner.id}'"
        )
        if rows or rows2:
            try:
                temp = None
                if rows:
                    temp = rows
                elif rows2:
                    temp = rows2
                else:
                    await guild.leave()
                    return
                admin = self.miya.get_user(int(temp[0][2]))
                embed = discord.Embed(
                    title=f"이런, {guild.name} 서버는 (혹은 그 소유자가) 차단되었어요.",
                    description=f"""
차단에 관해서는 지원 서버를 방문해주세요.
사유 : {temp[0][1]}
관리자 : {admin}
차단 시각 : {temp[0][3]}
                    """,
                    timestamp=datetime.datetime.utcnow(),
                    color=0xFF3333,
                )
                embed.set_author(name="초대 제한", icon_url=self.miya.user.avatar_url)
                await guild.owner.send(
                    f"<:cs_notify:659355468904529920> {guild.owner.mention} https://discord.gg/tu4NKbEEnn",
                    embed=embed,
                )
            except:
                await Hook.terminal(
                    0,
                    f"Owner DM Failed >\nGuild - {guild.name} ({guild.id})",
                    "서버 입퇴장 기록",
                    self.miya.user.avatar_url,
                )
                admin = self.miya.get_user(int(temp[0][2]))
                embed = discord.Embed(
                    title=f"이런, {guild.name} 서버는 (혹은 그 소유자가) 차단되었어요.",
                    description=f"""
차단에 관해서는 지원 서버를 방문해주세요.
사유 : {temp[0][1]}
관리자 : {admin}
차단 시각 : {temp[0][3]}
                    """,
                    timestamp=datetime.datetime.utcnow(),
                    color=0xFF3333,
                )
                embed.set_author(name="초대 제한", icon_url=self.miya.user.avatar_url)
                await guild.text_channels[0].send(
                    f"<:cs_notify:659355468904529920> {guild.owner.mention} https://discord.gg/tu4NKbEEnn",
                    embed=embed,
                )
            await Hook.terminal(
                0,
                f"Blocked Guild >\nGuild - {guild.name} ({guild.id})\nOwner - {guild.owner} ({guild.owner.id})",
                "서버 입퇴장 기록",
                self.miya.user.avatar_url,
            )
            await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await Hook.terminal(
            0,
            f"Quit >\nGuild - {guild.name} ({guild.id})",
            "서버 입퇴장 기록",
            self.miya.user.avatar_url,
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot == False:
            rows = await sql(
                0, f"SELECT * FROM `membernoti` WHERE `guild` = '{member.guild.id}'"
            )
            if not rows:
                return
            else:
                value = rows[0]
                channel = member.guild.get_channel(int(value[1]))
                if channel is not None and value[2] != "":
                    try:
                        msg = value[2].replace("{member}", str(member.mention))
                        msg = msg.replace("{guild}", str(member.guild.name))
                        msg = msg.replace("{count}", str(member.guild.member_count))
                        await channel.send(msg)
                    except Exception as e:
                        await Hook.terminal(
                            0,
                            f"MemberNoti Failed >\nGuild - {member.guild.name} ({member.guild.id})\nException - {e}",
                            "유저 입퇴장 알림 기록",
                            self.miya.user.avatar_url,
                        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot == False:
            rows = await sql(
                0, f"SELECT * FROM `membernoti` WHERE `guild` = '{member.guild.id}'"
            )
            if not rows:
                return
            else:
                value = rows[0]
                channel = member.guild.get_channel(int(value[1]))
                if channel is not None and value[3] != "":
                    try:
                        msg = value[3].replace("{member}", str(member))
                        msg = msg.replace("{guild}", str(member.guild.name))
                        msg = msg.replace("{count}", str(member.guild.member_count))
                        await channel.send(msg)
                    except Exception as e:
                        await Hook.terminal(
                            0,
                            f"MemberNoti Failed >\nGuild - {member.guild.name} ({member.guild.id})\nException - {e}",
                            "유저 입퇴장 알림 기록",
                            self.miya.user.avatar_url,
                        )


def setup(miya):
    miya.add_cog(Listeners(miya))
