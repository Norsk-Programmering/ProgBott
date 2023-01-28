# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.defaults import easy_embed, get_workplace, list_workplaces
from cogs.utils.my_errors import NoWorplace

from typing import Union


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
        Kommando for å legge til kollegaer
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
        Kommando for å avslutte et arbeidsforhold
        """
        workplaces = await list_workplaces(ctx.guild)
        try:
            cwk = await get_workplace(ctx.author)
            await ctx.author.remove_roles(discord.Object(cwk, type=discord.Role), reason="Removed from workplace")
            await ctx.reply(f"Du ikke en {workplaces[cwk]} lengere", delete_after=5)
        except NoWorplace:
            await ctx.reply("Du er ikke tilknyttet en arbeidsplass", delete_after=5)
        return await ctx.message.delete(delay=5)

    @workplace_group.command(name="liste", aliases=["alle"])
    async def get_list(self, ctx: discord.Message):
        """
        Lister alle arbiedsplassene som er registrert
        """

        workplaces = await list_workplaces(ctx.guild)
        workplace_list = sorted([y.replace("-ansatt", "") for x, y in workplaces.items()], key=str.lower)
        workplace_text = "\n".join(workplace_list)
        desc = workplace_text + "\n\nSer du ikke arbeidsplassen din? " + \
            "Send logo og firma-navn til en moderator, så ordner de det!"

        embed = easy_embed(self, ctx)
        embed.title = "Disse arbeidsplassene er registrert på serveren"
        embed.description = desc
        return await ctx.reply(embed=embed)

    @workplace_group.command(name="firma", aliases=["arbeidsplass", "se"])
    async def show_workplace(self, ctx: discord.Message, arbeidsplass: Union[discord.Role, str]):
        """
        Viser enkel informasjon om en arbeidsplass
        """
        if isinstance(arbeidsplass, str):
            for _role in ctx.guild.roles:
                if _role.name.lower() == f"{arbeidsplass.lower()}-ansatt":
                    arbeidsplass = _role
                    break

        if not isinstance(arbeidsplass, discord.Role):
            return await ctx.reply("Fant ingen arbeidsplass med dette navnet")

        await ctx.invoke(self.bot.get_command("rolle"), rolle=arbeidsplass)


async def setup(bot):
    # pylint: disable=missing-function-docstring
    await bot.add_cog(Workplace(bot))
