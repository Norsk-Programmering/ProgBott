"""
Cog for utløsere på ord
"""

# Discord Packages
from nextcord.ext import commands

from random import randint


class Broder(commands.Cog):
    # pylint: disable=missing-class-docstring
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # pylint: disable=missing-function-docstring
        if not message.author.bot:
            await self._filter(message)

    @commands.Cog.listener()
    async def on_message_edit(self, _before, after):
        # pylint: disable=missing-function-docstring
        if not after.author.bot:
            await self._filter(after)

    async def _filter(self, message):
        word_ = [("bruh", "bruh"), ("rox", "Du kalte?")]
        content_ = message.content.lower()
        for word, yeet in word_:
            if word in content_.split(" "):
                if int(randint(0, 100)) <= 15:
                    await message.reply(yeet, mention_author=True)


def setup(bot):
    # pylint: disable=missing-function-docstring
    bot.add_cog(Broder(bot))
