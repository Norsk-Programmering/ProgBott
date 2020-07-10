import discord
from discord.ext import commands

class Github(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.group(name="github")
    async def ghGroup(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @ghGroup.command(name="test")
    async def test(self, ctx):
        await ctx.send(text="OK")


def setup(bot):
    bot.add_cog(Github(bot))