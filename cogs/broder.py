# Discord Packages
from discord.ext import commands


class Broder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self._filter(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot and (after.edited_at.timestamp() - before.created_at.timestamp()) < 60:
            await self._filter(after)

    async def _filter(self, message, **kwarg):
        word_ = "bruh"
        content_ = message.content.lower()
        if word_ in content_:
            await message.channel.send("bruh")


def setup(bot):
    bot.add_cog(Broder(bot))
