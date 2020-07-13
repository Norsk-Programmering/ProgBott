# Discord Packages
import discord
import random
import time


def easy_embed(self, ctx, big_embed: bool = False):
    avatar = self.bot.user.avatar_url_as(format=None, static_format='png', size=1024)
    embed = discord.Embed(colour=ctx.author.colour)
    embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url)
    if big_embed:
        embed.set_thumbnail(url=avatar)
    return embed

async def timed_question(self, ctx, question, timedoutresponse, questionembed = None):
    embed = easy_embed(self, ctx)
    await ctx.send(question, embed=questionembed)

    starttimer = time.time()
    msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
    endtimer = time.time()

    if endtimer-starttimer > 15:
        embed.title = timedoutresponse
        await ctx.send(embed=embed)
        return
    else:
        return msg

def random_hex_color():
    return random.randint(0x000000,0xFFFFFF)
