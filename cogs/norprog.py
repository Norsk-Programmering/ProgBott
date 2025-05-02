"""
Cog for funksjoner spesialsyd til Norsk Programmering
"""

# Discord Packages
import discord
from discord.ext import commands

from pprint import pprint


class Norprog(commands.Cog):
    """
    Diverse funksjoner
    """

    def __init__(self, bot):
        self.bot = bot
        self.settings = bot.settings.joiner

    # @commands.command()
    # async def jointest(self, ctx, bruker: discord.Member):
    #     await self._join(member=bruker)
    #     await ctx.reply(content=", ".join([x.name for x in bruker.roles]))

    async def _join(self, member: discord.Member):
        if role := self.settings.get(str(member.guild.id), False):
            await member.add_roles(discord.Object(role, type=discord.Role), reason="Ble med på serveren")


async def setup(bot):
    _n = Norprog(bot)
    bot.add_listener(_n._join, "on_member_join")
    await bot.add_cog(_n)


async def teardown(bot):
    _n = Norprog(bot)
    bot.remove_listener(_n._join)
