# Discord Packages
import discord


def easy_embed(self, ctx, big_embed: bool = False):
    avatar = self.bot.user.avatar_url_as(format=None, static_format='png', size=1024)
    embed = discord.Embed(colour=ctx.author.colour)
    embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url)
    if big_embed:
        embed.set_thumbnail(url=avatar)
    return embed
