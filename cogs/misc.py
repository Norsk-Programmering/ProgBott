# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.defaults import easy_embed
from cogs.utils.Bot_version import bot_version

import platform
import time


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo = "https://github.com/Roxedus/ProgBott"

    def get_uptime(self):
        now = time.time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        return days, hours, minutes, seconds

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

    @commands.command(name='oppetid', aliases=["uptime"], hidden=True)
    async def _uptime(self, ctx):
        days, hours, minutes, seconds = self.get_uptime()
        await ctx.send(f'{days}d {hours}h {minutes}m {seconds}s')

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

    @commands.command()
    async def info(self, ctx):
        """
        Lister info om botten, og serverrelaterte instillinger
        """
        membercount = []
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.id in membercount:
                    pass
                else:
                    membercount.append(member.id)

        dev = await self.bot.fetch_user(self.bot.appinfo.owner.id)

        desc = f"Discord-programvareagent for Norsk Programering" \
               f"Forbedringforslag mottas på [GitHub]({self.repo})"

        py_ver = platform.python_version()
        how = f"**Python-versjon:** " \
              f"[{py_ver}](https://python.org/downloads/release/python-{py_ver.replace('.', '')}/)" \
              f"\n**Discord.py-versjon:** " \
              f"[{discord.__version__}](https://github.com/Rapptz/discord.py/releases/tag/v{discord.__version__}/)" \
              f"\n**ProgBott-versjon:** {bot_version}"

        guilds = len(self.bot.guilds)
        members = len(membercount)
        days, hours, minutes, seconds = self.get_uptime()
        avatar = self.bot.user.avatar_url_as(format=None, static_format='png', size=1024)

        uptimetext = f'{days}d {hours}t {minutes}m {seconds}s'
        embed = discord.Embed(color=discord.Colour.from_rgb(245, 151, 47), description=desc)
        embed.set_author(name=dev.name, icon_url=dev.avatar_url)
        embed.set_thumbnail(url=avatar)

        embed.add_field(name="Tjenere", value=str(guilds))
        embed.add_field(name="Hvor mange?", value=f'{members} brukere')
        embed.add_field(name="Oppetid", value=uptimetext)
        embed.add_field(name="Hvordan?", value=how, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
