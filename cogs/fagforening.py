# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.defaults import easy_embed, get_union, list_unions
from cogs.utils.my_errors import NoWorplace

from typing import Union


class Union(commands.Cog):
    """
    Klasse for diverse komandoer
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.group(name="fagforening", aliases=["fag"])
    async def union_group(self, ctx: discord.Message):
        """
        Kategori for styring av fagforening
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @union_group.command(name="leggtil", aliases=["add", "medlem"])
    async def add(self, ctx: discord.Message, bruker: discord.Member):
        """
        Kommando for å legge til medlemmer
        """
        try:
            cwk = await get_union(ctx.author)
        except NoWorplace:
            await ctx.reply("Du er ikke tilknyttet en fagforening", delete_after=5)
            return await ctx.message.delete(delay=5)

        unions = await list_unions(ctx.guild)

        try:
            uwk = await get_union(bruker)
            return await ctx.reply(f"{bruker.display_name} er allerede en {unions[uwk]}", delete_after=5)
        except NoWorplace:
            await bruker.add_roles(discord.Object(cwk, type=discord.Role), reason="Bound new union")
            try:
                await bruker.send(f"Du er nå registrert som {unions[cwk]} i {ctx.guild.name} "
                                  f"av {ctx.author.display_name}")
            except discord.Forbidden:
                await ctx.reply(f"{bruker.mention} er nå registrert som {unions[cwk]}",
                                allowed_mentions=discord.AllowedMentions(users=True), delete_after=5)
        return await ctx.message.delete(delay=5)

    @union_group.command(name="fjern", aliases=["remove", "oppsigelse", "slutt"])
    async def remove(self, ctx: discord.Message):
        """
        Kommando for å avslutte et arbeidsforhold
        """
        unions = await list_unions(ctx.guild)
        try:
            cwk = await get_union(ctx.author)
            await ctx.author.remove_roles(discord.Object(cwk, type=discord.Role), reason="Removed from union")
            await ctx.reply(f"Du ikke en {unions[cwk]} lengere", delete_after=5)
        except NoWorplace:
            await ctx.reply("Du er ikke tilknyttet en fagforening", delete_after=5)
        return await ctx.message.delete(delay=5)

    @union_group.command(name="liste", aliases=["alle"])
    async def get_list(self, ctx: discord.Message):
        """
        Lister alle fagforeningene som er registrert
        """

        unions = await list_unions(ctx.guild)
        union_list = sorted([y.replace("-ansatt", "") for x, y in unions.items()], key=str.lower)
        union_text = "\n".join(union_list)
        desc = union_text + "\n\nSer du ikke fagforeningen din? " + \
            "Send logo og fagforenings-navn til en moderator, så ordner de det!"

        embed = easy_embed(self, ctx)
        embed.title = "Disse fagforeningene er registrert på serveren"
        embed.description = desc
        return await ctx.reply(embed=embed)

    @union_group.command(name="firma", aliases=["fagforening", "se"])
    async def show_union(self, ctx: discord.Message, fagforening: Union[discord.Role, str]):
        """
        Viser enkel informasjon om en fagforening
        """
        if isinstance(fagforening, str):
            for _role in ctx.guild.roles:
                if _role.name.lower() == f"{fagforening.lower()}-ansatt":
                    fagforening = _role
                    break

        if not isinstance(fagforening, discord.Role):
            return await ctx.reply("Fant ingen fagforening med dette navnet")

        await ctx.invoke(self.bot.get_command("rolle"), rolle=fagforening)


async def setup(bot):
    # pylint: disable=missing-function-docstring
    await bot.add_cog(union(bot))
