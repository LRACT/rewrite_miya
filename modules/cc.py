import datetime
import locale
import random

import aiohttp
import discord
import koreanbots
from discord.ext import commands

from lib import config, utils
from lib.utils import Forbidden, Maintaining, NoReg, sql

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
        return False

    return commands.check(search)


class CC(commands.Cog, name="지식 및 배우기"):
    def __init__(self, miya):
        self.miya = miya

    @commands.command(name="기억해", aliases=["배워"])
    @has_no_symbols()
    async def _learn(self, ctx, word, *, value):
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
                    description=f"등록되면 미야가 `{word}`라고 물어봤을 때\n```{value}```\n(이)라고 답할거에요.\n \n*부적절한 어휘 및 답변의 경우 예고 없이 삭제될 수 있어요.*",
                    color=0x5FE9FF,
                    timestamp=datetime.datetime.utcnow(),
                )
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
                            f"INSERT INTO `cc`(`no`, `word`, `description`, `user`, `disabled`) VALUES('{number}', '{word}', '{value}', '{ctx.author.id}', 'false')",
                        )
                        embed = discord.Embed(
                            title="가르쳐주셔서 고마워요!",
                            description=f"이제 `{word}`에 이렇게 답할거에요:\n```{value}```\n.",
                            color=0x5FE9FF,
                            timestamp=datetime.datetime.utcnow(),
                        )
                        await msg.edit(embed=embed)
                    else:
                        await msg.delete()
            else:
                await ctx.reply(
                    f":broken_heart: 미야에게 무언가를 가르치려면 `하트`를 눌러야 해요!\n하트 누르기 : https://koreanbots.dev/bots/720724942873821316"
                )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if (
            isinstance(error, commands.CommandNotFound)
            or isinstance(error, commands.NotOwner)
            or isinstance(error, commands.CheckFailure)
        ):
            try:
                p = await Check.identify(ctx)
            except Exception as e:
                if isinstance(e, Forbidden):
                    await ctx.reply(str(e), embed=e.embed)
                elif isinstance(e, NoReg) or isinstance(e, Maintaining):
                    await ctx.reply(str(e))
                elif isinstance(e, commands.NoPrivateMessage):
                    return
            else:
                if p is True:
                    headers = {
                        "Authorization": config.PPBToken,
                        "Content-Type": "application/json",
                    }
                    query = ctx.message.content.replace("미야야 ", "")
                    query2 = query.replace(" ", "")
                    query2.replace("\\", "")
                    query2.replace('"', "")
                    query2.replace("'", "")
                    # query2.tolower()
                    embed = None
                    rows = await sql(0, f"SELECT * FROM `cc` WHERE `word` = '{query2}'")
                    if not rows:
                        async with aiohttp.ClientSession() as cs:
                            async with cs.post(
                                config.PPBRequest,
                                headers=headers,
                                json={"request": {"query": query}},
                            ) as r:
                                response_msg = await r.json()
                                msg = response_msg["response"]["replies"][0]["text"]
                                if (
                                    msg
                                    != "앗, 저 이번 달에 할 수 있는 말을 다 해버렸어요 🤐 다음 달까지 기다려주실거죠? ☹️"
                                ):
                                    await Hook.terminal(
                                        0,
                                        f"PINGPONG Builder >\nUser - {ctx.author} ({ctx.author.id})\nSent - {query}\nReceived - {msg}\nGuild - {ctx.guild.name} ({ctx.guild.id})",
                                        "명령어 처리 기록",
                                        self.miya.user.avatar_url,
                                    )
                                    embed = discord.Embed(
                                        title=msg,
                                        description=f"[Discord 지원 서버 접속하기](https://discord.gg/tu4NKbEEnn)\n[한국 디스코드 봇 리스트 하트 누르기](https://koreanbots.dev/bots/720724942873821316)",
                                        color=0x5FE9FF,
                                    )
                                    embed.set_footer(
                                        text="이 답변은 https://pingpong.us/를 통해 만들어졌습니다."
                                    )
                                else:
                                    embed = discord.Embed(
                                        title="💭 이런, 미야가 말풍선을 모두 사용한 모양이네요.",
                                        description=f"매월 1일에 말풍선이 다시 생기니 그 때까지만 기다려주세요!\n \n[Discord 지원 서버 접속하기](https://discord.gg/tu4NKbEEnn)\n[한국 디스코드 봇 리스트 하트 누르기](https://koreanbots.dev/bots/720724942873821316)",
                                        color=0x5FE9FF,
                                    )
                                    embed.set_footer(
                                        text="이 답변은 https://pingpong.us/를 통해 만들어졌습니다."
                                    )
                    else:
                        row = random.choice(rows)
                        user = self.miya.get_user(int(row[3]))
                        embed = discord.Embed(
                            title=row[2],
                            description=f"[Discord 지원 서버 접속하기](https://discord.gg/tu4NKbEEnn)\n[한국 디스코드 봇 리스트 하트 누르기](https://koreanbots.dev/bots/720724942873821316)",
                            color=0x5FE9FF,
                        )
                        embed.set_footer(
                            text=f"이 답변은 {user.name}({row[0]})님의 지식을 통해 만들어졌습니다."
                        )
                    await ctx.reply(embed=embed)


def setup(miya):
    miya.add_cog(CC(miya))
