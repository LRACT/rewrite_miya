import datetime

import aiohttp
import discord
from discord import AsyncWebhookAdapter
from discord import Webhook
from discord.ext import commands

from lib.utils import sql


class Logger(commands.Cog, name="기록장"):
    """미야의 이벤트 로그를 남기기 3분 강의"""
    def __init__(self, bot):
        self.bot = bot

    async def log(self, guild_id):
        rows = await sql(
            0, f"SELECT `eventLog` FROM `guilds` WHERE `guild` = '{guild_id}'")
        if not rows:
            return None
        else:
            return rows[0][0]

    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        if msg.author.bot:
            return

        files = []
        if msg.attachments:
            for attachment in msg.attachments:
                try:
                    temp = await attachment.to_file(use_cached=True)
                    files.append(temp)
                except:
                    continue

        embed = discord.Embed(timestamp=datetime.datetime.utcnow(),
                              color=0xA5FFEB)
        embed.add_field(
            name="메시지를 보낸 이",
            value=f"{msg.author.mention} ({msg.author.id})",
            inline=False,
        )
        embed.add_field(
            name="메시지가 있던 채널",
            value=
            f"{msg.channel.mention} ({msg.channel.name}, {msg.channel.id})",
            inline=False,
        )
        embed.set_thumbnail(
            url=msg.guild.icon_url_as(static_format="png", size=2048))
        embed.set_author(name="메시지 삭제 이벤트", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=msg.guild.name, icon_url=msg.guild.icon_url)
        url = await self.log(msg.guild.id)
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(
                    url, adapter=AsyncWebhookAdapter(session))
            except:
                return
            else:
                await webhook.send(
                    username=f"{msg.author} (삭제됨)",
                    files=files,
                    avatar_url=msg.author.avatar_url_as(format="png",
                                                        size=2048),
                    content=msg.content,
                    embed=embed,
                )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or after.author.bot:
            return

        if before.content == after.content:
            return

        embed = discord.Embed(timestamp=datetime.datetime.utcnow(),
                              color=0xA5FFEB)
        embed.add_field(
            name="메시지를 보낸 이",
            value=f"{after.author.mention} ({after.author.id})",
            inline=False,
        )
        embed.add_field(
            name="메시지가 수정된 채널",
            value=
            f"{after.channel.mention} ({after.channel.name}, {after.channel.id})",
            inline=False,
        )
        embed.add_field(
            name="메시지 바로가기",
            value=
            f"https://discord.com/channels/{after.guild.id}/{after.channel.id}/{after.id}",
            inline=False,
        )
        if before.content is not None:
            embed.add_field(name="수정 전", value=before.content, inline=False)
        embed.add_field(name="수정 후", value=after.content, inline=False)
        embed.set_thumbnail(
            url=after.guild.icon_url_as(static_format="png", size=2048))
        embed.set_author(name="메시지 수정 이벤트", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=after.guild.name, icon_url=after.guild.icon_url)
        url = await self.log(after.guild.id)
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(
                    url, adapter=AsyncWebhookAdapter(session))
            except:
                return
            else:
                await webhook.send(
                    username=f"{after.author} (수정됨)",
                    avatar_url=after.author.avatar_url_as(format="png",
                                                          size=2048),
                    content="아래에서 내용을 확인하세요.",
                    embed=embed,
                )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="유저가 서버에 입장했습니다.",
            description=f"< 입장한 유저 : {member.mention}\n",
            timestamp=datetime.datetime.utcnow(),
            color=0x15FF0E,
        )
        embed.set_thumbnail(
            url=member.avatar_url_as(static_format="png", size=2048))
        embed.set_footer(text=member.guild.name,
                         icon_url=member.guild.icon_url)
        embed.set_author(name="멤버 입장 이벤트", icon_url=self.bot.user.avatar_url)
        url = await self.log(member.guild.id)
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(
                    url, adapter=AsyncWebhookAdapter(session))
            except:
                return
            else:
                await webhook.send(
                    username=f"{member} (입장함)",
                    avatar_url=member.avatar_url_as(format="png", size=2048),
                    content="아래에서 내용을 확인하세요.",
                    embed=embed,
                )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        roles = ""
        for role in member.roles:
            roles += f"{role.mention} "
        embed = discord.Embed(
            title="유저가 서버에서 나갔습니다.",
            description=f"< 퇴장한 유저 : {member.mention}\n< 가지고 있던 역할 {roles}",
            timestamp=datetime.datetime.utcnow(),
            color=0xFF0000,
        )
        embed.set_thumbnail(
            url=member.guild.icon_url_as(static_format="png", size=2048))
        embed.set_footer(text=member.guild.name,
                         icon_url=member.guild.icon_url)
        embed.set_author(name="멤버 퇴장 이벤트", icon_url=self.bot.user.avatar_url)
        url = await self.log(member.guild.id)
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(
                    url, adapter=AsyncWebhookAdapter(session))
            except:
                return
            else:
                await webhook.send(
                    username=f"{member} (퇴장함)",
                    avatar_url=member.avatar_url_as(format="png", size=2048),
                    content="아래에서 내용을 확인하세요.",
                    embed=embed,
                )


def setup(bot):
    bot.add_cog(Logger(bot))
