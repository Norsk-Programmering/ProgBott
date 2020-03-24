import discord
import time
import platform

from .utils.defaults import easy_embed

from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', hidden=True)
    async def _ping(self, ctx):
        embed = easy_embed(self, ctx)
        embed.title = "Ping!"
        start = time.perf_counter()
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        duration = int((end - start) * 1000)
        edit = f'Pong!\nPing: {duration}ms | websocket: {int(self.bot.latency * 1000)}ms'
        embed.description = edit
        await message.edit(embed=embed)

    @commands.command(name='uptime', hidden=True)
    async def _uptime(self, ctx):
        embed = easy_embed(self, ctx)
        now = time.time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        embed.description = f'{days}d {hours}h {minutes}m {seconds}s'
        await ctx.send(embed=embed)

    @commands.command(name='guilds')
    @commands.is_owner()
    async def _guilds(self, ctx):
        embed = easy_embed(self, ctx)
        guilds = ""
        for guild in self.bot.guilds:
            guilds += f"{guild.name}\n"
        embed.description = f'```\n{guilds}\n```'
        embed.title = f'{self.bot.user.name} is in'
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
