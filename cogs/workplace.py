# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.defaults import get_workplace, list_workplaces
from cogs.utils.my_errors import NoWorplace


class Workplace(commands.Cog):
    """
    Klasse for diverse komandoer
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.group(name="arbeidsplass", aliases=["jobb"])
    async def workplace_group(self, ctx: discord.Message):
        """
        Kategori for styring av arbeidsplass
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @workplace_group.command(name="leggtil", aliases=["add", "kollega"])
    async def add(self, ctx: discord.Message, bruker: discord.Member):
        """
        Komando for å legge til kollegaer
        """
        try:
            cwk = await get_workplace(ctx.author)
        except NoWorplace:
            await ctx.reply("Du er ikke tilknyttet en arbeidsplass", delete_after=5)
            return await ctx.message.delete(delay=5)

        workplaces = await list_workplaces(ctx.guild)

        try:
            uwk = await get_workplace(bruker)
            return await ctx.reply(f"{bruker.display_name} er allerede en {workplaces[uwk]}", delete_after=5)
        except NoWorplace:
            await bruker.add_roles(discord.Object(cwk, type=discord.Role), reason="Bound new workplace")
            try:
                await bruker.send(f"Du er nå registrert som {workplaces[cwk]} i {ctx.guild.name} "
                                  f"av {ctx.author.display_name}")
            except discord.Forbidden:
                await ctx.reply(f"{bruker.mention} er nå registrert som {workplaces[cwk]}",
                                allowed_mentions=discord.AllowedMentions(users=True), delete_after=5)
        return await ctx.message.delete(delay=5)

    @workplace_group.command(name="fjern", aliases=["remove", "oppsigelse", "slutt"])
    async def remove(self, ctx: discord.Message):
        """
        Komando for å avslutte et arbeidsforhold
        """
        workplaces = await list_workplaces(ctx.guild)
        try:
            cwk = await get_workplace(ctx.author)
            await ctx.author.remove_roles(discord.Object(cwk, type=discord.Role), reason="Removed from workplace")
            await ctx.reply(f"Du ikke en {workplaces[cwk]} lengere", delete_after=5)
        except NoWorplace:
            await ctx.reply("Du er ikke tilknyttet en arbeidsplass", delete_after=5)
        return await ctx.message.delete(delay=5)


async def setup(bot):
    # pylint: disable=missing-function-docstring
    await bot.add_cog(Workplace(bot))
