# Discord Packages
from discord.ext import commands

from random import randint


class Broder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self._filter(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            await self._filter(after)

    async def _filter(self, message, **kwarg):
        word_ = [("bruh", "bruh"), ("rox", "Du kalte?")]
        content_ = message.content.lower()
        for word, yeet in word_:
            if word in content_:
                if int(randint(0, 100)) <= 15:
                    await message.reply(yeet, mention_author=True)


def setup(bot):
    bot.add_cog(Broder(bot))
