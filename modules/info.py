import datetime
import typing

import aiohttp
import discord
from discord import AsyncWebhookAdapter
from discord import Webhook
from discord.ext import commands

from lib import utils
from lib.utils import sql


class Information(commands.Cog, name="정보"):
    """다양한 정보들을 제공하는 것들"""
    def __init__(self, miya):
        self.miya = miya
        self.get = utils.Get()

    @commands.command(name="서버정보")
    async def _serverinfo(self, ctx):
        """
        미야야 서버정보


        명령어를 실행한 서버의 정보와 미야 설정을 불러옵니다.
        """
        async with ctx.channel.typing():
            embed = discord.Embed(title=f"{ctx.guild.name} 정보 및 미야 설정",
                                  color=0x5FE9FF)
            guilds = await sql(
                0, f"SELECT * FROM `guilds` WHERE `guild` = '{ctx.guild.id}'")
            memberNoti = await sql(
                0,
                f"SELECT * FROM `membernoti` WHERE `guild` = '{ctx.guild.id}'")
            muteRole = "설정되어 있지 않아요!"
            memberCh = "설정되어 있지 않아요!"
            logCh = "설정되어 있지 않아요!"
            if guilds[0][2] != 1234:
                role = ctx.guild.get_role(int(guilds[0][2]))
                if role is not None:
                    muteRole = role.mention
            if memberNoti[0][1] != 1234:
                channel = ctx.guild.get_channel(int(memberNoti[0][1]))
                if channel is not None:
                    memberCh = channel.mention
            if guilds[0][1] != "None":
                async with aiohttp.ClientSession() as session:
                    try:
                        webhook = Webhook.from_url(
                            guilds[0][1], adapter=AsyncWebhookAdapter(session))
                        channel = ctx.guild.get_channel(int(
                            webhook.channel_id))
                        if channel is not None:
                            logCh = channel.mention
                    except:
                        pass
            location = {
                "amsterdam": "네덜란드 - 암스테르담",
                "brazil": "브라질",
                "dubai": "아랍에미리트 - 두바이",
                "eu_central": "유럽 - 중부",
                "eu_west": "유럽 - 서부",
                "europe": "유럽",
                "frankfurt": "독일 - 프랑크푸르트",
                "hongkong": "홍콩",
                "india": "인도",
                "japan": "일본",
                "london": "영국 - 런던",
                "russia": "러시아",
                "singapore": "싱가포르",
                "southafrica": "남아프리카",
                "south-korea": "대한민국",
                "sydney": "호주 - 시드니",
                "us-central": "미국 - 중부",
                "us-east": "미국 - 동부",
                "us-south": "미국 - 남부",
                "us-west": "미국 - 서부",
                "vip-amsterdam": "<:vip:762569445427511307> 네덜란드 - 암스테르담",
                "vip-us-east": "<:vip:762569445427511307> 미국 - 동부",
                "vip-us-west": "<:vip:762569445427511307> 미국 - 서부",
            }
            verification = {
                discord.VerificationLevel.none:
                "**없음**\n제한 없음",
                discord.VerificationLevel.low:
                "**낮음**\n이메일 인증이 완료된 Discord 계정이어야 해요.",
                discord.VerificationLevel.medium:
                "**중간**\n이메일 인증이 완료되고, Discord에 가입한 지 5분이 지나야 해요.",
                discord.VerificationLevel.high:
                "**높음**\n이메일 인증이 완료되고, Discord에 가입한 지 5분이 지나며, 서버의 멤버가 된 지 10분이 지나야 해요.",
                discord.VerificationLevel.extreme:
                "**매우 높음**\n휴대폰 인증이 완료된 Discord 계정이어야 해요.",
            }
            time = self.get.localize(ctx.guild.created_at)
            embed.add_field(name="공지 채널",
                            value="📢 **서버의 연동 설정을 확인하세요!**",
                            inline=False)
            embed.add_field(name="멤버 알림 채널", value=memberCh)
            embed.add_field(name="로그 채널", value=logCh)
            embed.add_field(name="뮤트 역할", value=muteRole)
            embed.add_field(name="서버 부스트 인원 수",
                            value=f"{len(ctx.guild.premium_subscribers)}명")
            embed.add_field(name="서버 오너", value=f"{str(ctx.guild.owner)}님")
            embed.add_field(name="서버 인원 수", value=f"{ctx.guild.member_count}명")
            embed.add_field(name="서버 역할 갯수", value=f"{len(ctx.guild.roles)}개")
            embed.add_field(name="서버 위치",
                            value=location[str(ctx.guild.region)])
            embed.add_field(name="서버 개설 날짜", value=time)
            embed.add_field(name="서버 보안 수준",
                            value=verification[ctx.guild.verification_level])
            embed.set_author(name="이 서버의 정보",
                             icon_url=self.miya.user.avatar_url)
            embed.set_thumbnail(
                url=ctx.guild.icon_url_as(static_format="png", size=2048))
            await ctx.reply(embed=embed)

    @commands.command(name="봇정보", aliases=["미야정보", "미야"])
    async def _miyainfo(self, ctx):
        """
        미야야 미야


        미야의 정보를 표시합니다.
        """
        async with ctx.channel.typing():
            heart = await self.miya.get_rank()
            e = discord.Embed(
                description=f"""
<:koreanbots:794450277792481290> 봇 순위 : {heart}위 [하트 누르기](https://koreanbots.dev/bots/720724942873821316)
<:GitHub_W:782076841141207071> 코드 저장소 : [보러 가기](https://github.com/LRACT/Miya)
<:cs_settings:659355468992610304> 호스트 : 개인 서버 - 한국
<:cs_on:659355468682231810> 리라이트 시작 : 2020년 8월 17일
<:cs_leave:659355468803866624> 서버 수 : {len(self.miya.guilds)}개""",
                color=0x5FE9FF,
                timestamp=datetime.datetime.utcnow(),
            )
            e.set_thumbnail(url=self.miya.user.avatar_url_as(
                static_format="png", size=2048))
            e.set_author(name="미야 TMI", icon_url=self.miya.user.avatar_url)
            await ctx.reply(embed=e)

    @commands.command(name="프로필", aliases=["프사", "프로필사진", "아바타"])
    async def _profile(self, ctx, user: typing.Optional[discord.User] = None):
        """
        미야야 프로필 [ @유저 ]


        지목한 유저의 프로필을 보여줍니다.
        지목이 되지 않았을 경우 자신의 프로필을 보여줍니다.
        """
        if user is None:
            user = ctx.author
        embed = discord.Embed(color=0x5FE9FF)
        embed.set_author(name=f"{user.name}님의 프로필 사진",
                         icon_url=self.miya.user.avatar_url)
        embed.set_image(url=user.avatar_url_as(static_format="png", size=2048))
        await ctx.reply(embed=embed)

    @commands.command(name="한강")
    async def _hangang(self, ctx):
        """
        미야야 한강


        현재 한강의 수온을 출력합니다.
        """
        async with ctx.channel.typing():
            result = await self.get.hangang()
            embed = discord.Embed(
                description=f"현재 한강의 온도는 `{result[0]}`도에요!\n`측정: {result[1]}`",
                color=0x5FE9FF,
            )
            embed.set_author(name="지금 한강은", icon_url=self.miya.user.avatar_url)
            if result[0] > 15:
                embed.set_footer(text="거 수온이 뜨듯하구먼!")
            else:
                embed.set_footer(text="거 이거 완전 얼음장이구먼!")
            await ctx.reply(embed=embed)

    @commands.command(name="코로나")
    async def _corona_info(self, ctx):
        """
        미야야 코로나


        대한민국의 코로나 현황을 불러옵니다.
        """
        async with ctx.channel.typing():
            _corona = await self.get.corona()
            embed = discord.Embed(title="국내 코로나19 현황",
                                  description="질병관리청 집계 기준",
                                  color=0x5FE9FF)
            embed.add_field(name="확진자",
                            value=f"{_corona[0].split(')')[1]}명",
                            inline=True)
            embed.add_field(name="완치(격리 해제)",
                            value=f"{_corona[1]}명",
                            inline=True)
            embed.add_field(name="치료 중", value=f"{_corona[2]}명", inline=True)
            embed.add_field(name="사망", value=f"{_corona[3]}명", inline=True)
            embed.add_field(name="정보 출처",
                            value="[질병관리청](http://ncov.mohw.go.kr/)",
                            inline=True)
            embed.set_author(name="COVID-19",
                             icon_url=self.miya.user.avatar_url)
            embed.set_footer(
                text="코로나19 감염이 의심되면 즉시 보건소 및 콜센터(전화1339)로 신고바랍니다.")
            embed.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/746786600037384203/761404488023408640/unknown.png"
            )
            await ctx.reply(embed=embed)


def setup(miya):
    miya.add_cog(Information(miya))
