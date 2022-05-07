"""
Cog for opprettelse av bokmerker
"""

# Discord Packages
import discord
from discord.ext import commands, tasks

# Bot Utilities
from cogs.utils.defaults import easy_embed

import asyncio
import codecs
import json
import os
from math import ceil


class Bokmerker(commands.Cog):
    """
    Klasse for opprettelse av bokmerker
    """

    def __init__(self, bot):
        self.bot = bot
        self.bookmarks_data = {}
        self.bookmarks_file = bot.data_dir + '/bokmerker/bokmerker.json'
        self.load_json('bokmerker')
        self.cacher.start()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # pylint: disable=missing-function-docstring
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = payload.emoji

        if str(emoji) == '🔖':
            return await self.add_bookmark(message, user)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # pylint: disable=missing-function-docstring
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = payload.emoji

        if str(emoji) == '🔖':
            return await self.remove_bookmark(message, user)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        # pylint: disable=missing-function-docstring
        await self.remove_all_bookmarks(payload.message_id)

    async def add_bookmark(self, message, user):
        """
        Funksjon som oppretter bokmerker
        """

        title = f'{message.author.display_name}: {message.content[:64]}...'
        if message.embeds:
            title = "Embed"
        elif message.attachments:
            title = "Vedlegg"

        bokmerke_data = {
            'tittel': title,
            'link': message.jump_url,
        }

        if not str(user.id) in self.bookmarks_data['bokmerker']:
            self.bookmarks_data['bokmerker'][str(user.id)] = {}
        elif str(message.id) in self.bookmarks_data['bokmerker'][str(user.id)]:
            return

        self.bookmarks_data['bokmerker'][str(user.id)][str(message.id)] = bokmerke_data
        self.save_json('bokmerker')
        self.load_json('bokmerker')

        await message.add_reaction('👀')
        await asyncio.sleep(5)
        await message.remove_reaction('👀', self.bot.user)

    async def remove_bookmark(self, message, user):
        """
        Funksjon som fjerner bokmerker
        """

        if not str(user.id) in self.bookmarks_data['bokmerker']:
            return
        elif not str(message.id) in self.bookmarks_data['bokmerker'][str(user.id)]:
            return

        if len(self.bookmarks_data['bokmerker'][str(user.id)]) - 1 == 0:
            del self.bookmarks_data['bokmerker'][str(user.id)]
        else:
            del self.bookmarks_data['bokmerker'][str(user.id)][str(message.id)]

        self.save_json('bokmerker')
        self.load_json('bokmerker')

    async def remove_all_bookmarks(self, message_id):
        """
        Funksjon som fjerner alle bokmerker for melding
        """

        # Dette er nok en treg og dårlig approach, men men
        try:
            for user_id in self.bookmarks_data['bokmerker']:
                if self.bookmarks_data['bokmerker'][user_id][str(message_id)]:
                    del self.bookmarks_data['bokmerker'][user_id][str(message_id)]

            self.save_json('bokmerker')
            self.load_json('bokmerker')
        except KeyError:
            pass

    @commands.guild_only()
    @commands.group(name="bokmerker")
    async def bokmerker_group(self, ctx):
        """
        Kategori for styring av bokmerker
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @bokmerker_group.command(name="vis")
    async def check(self, ctx, user: discord.Member = None):
        """
        Kommando for å vise bokmerker
        """
        if not user:
            user = ctx.author

        if not str(user.id) in self.bookmarks_data['bokmerker']:
            await ctx.message.reply("Du har ingen bokmerker.")
            return

        message = await ctx.send('Laster...')

        await message.add_reaction('⏮️')
        await message.add_reaction('⏭️')

        def check(reaction, reaction_user):
            if reaction_user is None or reaction_user.id != user.id:
                return False

            if reaction.message.id != message.id:
                return False

            if reaction.emoji in ['⏮️', '⏭️']:
                return True

            return False

        antall_bokmerker = len(self.bookmarks_data['bokmerker'][str(user.id)])
        page = 0
        max_page = ceil(antall_bokmerker / 5) - 1
        indexed_bookmarks = list(self.bookmarks_data['bokmerker'][str(user.id)].values())

        while True:
            embed = easy_embed(self, ctx)
            for i in range(page*5, min(page*5 + 5, antall_bokmerker)):
                bokmerke = indexed_bookmarks[i]

                embed.add_field(
                    name=f"{bokmerke['tittel']}",
                    value=f"[Link]({bokmerke['link']})",
                    inline=False
                )

            embed.title = "Bokmerker"
            if antall_bokmerker == 1:
                embed.description = f"{user.mention} har {antall_bokmerker} bokmerke!"
            else:
                embed.description = f"{user.mention} har {antall_bokmerker} bokmerker!"

            embed.description += f"\nSide {page + 1}/{max_page + 1}"

            await message.edit(content=None, embed=embed)

            try:
                reaction, reaction_user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                try:
                    await message.remove_reaction(reaction.emoji, reaction_user)

                    if reaction.emoji == '⏮️':
                        page = max(page - 1, 0)
                    elif reaction.emoji == '⏭️':
                        page = min(page + 1, max_page)

                except discord.Forbidden:
                    self.bot.logger.warn('Missing permission to remove reaction (manage_messages)')

            except asyncio.TimeoutError:
                await message.remove_reaction('⏮️', self.bot.user)
                await message.remove_reaction('⏭️', self.bot.user)

    @tasks.loop(hours=5)
    async def cacher(self):
        """
        Mellomlagrer bokmerker
        """
        self.save_json('bokmerker')
        self.load_json('bokmerker')
        self.bot.logger.debug('Reloaded bookmark data cache')

    def load_json(self, mode):
        """
        Lagrer bokmerker
        """

        if mode == 'bokmerker':
            with codecs.open(self.bookmarks_file, 'r', encoding='utf8') as json_file:
                self.bookmarks_data = json.load(json_file)

    def save_json(self, mode):
        """
        Laster bokmerker
        """
        if mode == 'bokmerker':
            try:
                with codecs.open(self.bookmarks_file, 'w', encoding='utf8') as outfile:
                    json.dump(self.bookmarks_data, outfile, indent=4, sort_keys=True)
            except Exception as err:
                return self.bot.logger.warn(
                    'Failed to validate JSON before saving:\n%s\n%s' % (err, self.bookmarks_data))

    def check_folder(self):
        # pylint: disable=missing-function-docstring
        _f = f'{self.bot.data_dir}/bokmerker'
        if not os.path.exists(_f):
            os.makedirs(_f)

    def check_files(self):
        # pylint: disable=missing-function-docstring
        files = [
            {f'{self.bot.data_dir}/bokmerker/bokmerker.json': {'bokmerker': {}}},
        ]
        for i in files:
            for file, default in i.items():
                try:
                    with codecs.open(file, 'r', encoding='utf8') as json_file:
                        json.load(json_file)
                except FileNotFoundError:
                    with codecs.open(file, 'w', encoding='utf8') as outfile:
                        json.dump(default, outfile)

    async def cog_load(self):
        self.check_folder()
        self.check_files()

    async def cog_unload(self):
        self.cacher.cancel()


async def setup(bot):
    # pylint: disable=missing-function-docstring
    await bot.add_cog(Bokmerker(bot))
