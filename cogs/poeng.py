"""
Modul for tildeling av stjerner
"""

# Discord Packages
import discord
from discord.ext import commands, tasks

# Bot Utilities
from cogs.utils.defaults import easy_embed
from cogs.utils.mermaid import mermaid

import asyncio
import codecs
import json
import os
from pprint import pformat


class Poeng(commands.Cog):
    """
    Klasse for tildeling av stjerner
    """

    def __init__(self, bot):
        self.bot = bot
        self.teller_data = {}
        self.settings_file = bot.data_dir + '/poeng/innstilinger.json'
        self.teller_file = bot.data_dir + '/poeng/teller.json'
        self.chart = open("flowchart.mermaid", "r").read()
        self.load_json('settings')
        self.load_json('teller')
        self.cacher.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Funksjon for å sette lytter for nye meldinger
        """
        if not message.author.bot and message.mentions:
            await self._filter(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Funksjon for å sette lytter for redigerte meldinger
        """
        try:
            if not after.author.bot and after.mentions \
                    and (after.edited_at.timestamp() - before.created_at.timestamp()) < 60:
                await self._filter(after, before=before)
        except AttributeError:
            pass

    async def _filter(self, message, before=None):
        def check(message):
            # pylint: disable=missing-function-docstring
            for word in self.settings_data['takk']:
                word = word.lower()
                content = message.content.lower()
                if (
                    word in content and
                        (
                            "hjelp" in
                            (
                                message.channel.name or
                                message.channel.category.name).lower()
                        )
                    ) or (
                        content.startswith(word) or
                        content.endswith(word) or
                        content[:-1].endswith(word)
                ):
                    return True
        if not before:
            if check(message):
                return await self.add_star(message)
        elif before:
            if check(before):
                return
            if check(message):
                return await self.add_star(message)

    async def add_star(self, message):
        """
        Funksjon som gir stjerne
        """
        emoji = self.bot.get_emoji(743471543706976256)
        emoji_str = f'<:forkast:{emoji.id}>'
        dudes = {'id': [], 'mention': []}
        embed = easy_embed(self, message)
        for dude in message.mentions:
            if dude is self.bot.user:
                continue
            if dude is message.author:
                continue
            dudes['id'].append(dude.id)
            dudes["mention"].append(dude.mention)
        if not dudes['id']:
            return
        await message.add_reaction(emoji)
        msg_data = {
            'hjelper': dudes['id'],
            'giver': message.author.id,
            'link': message.jump_url
        }
        embed.title = "Ny stjerne tildelt!"
        embed.description = f'{message.author.mention} ga {", ".join(dudes["mention"])} en stjerne!'
        reply = await message.reply(f"Registrerer stjerne\nreager med {emoji_str} for å avbryte")
        async with message.channel.typing():

            def check(reaction, user):
                if user is None or user.id != message.author.id:
                    return False

                if reaction.message.id != message.id:
                    return False

                if reaction.emoji == emoji:
                    return True

                return False

            try:
                await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                await message.remove_reaction(emoji, self.bot.user)
                try:
                    await message.remove_reaction(emoji, message.author)
                except discord.Forbidden:
                    self.bot.logger.warn('Missing permission to remove reaction (manage_messages)')
                return await reply.delete()

            except asyncio.TimeoutError:
                self.teller_data['meldinger'][str(message.id)] = msg_data
                try:
                    await reply.edit(content=None, embed=embed)
                except discord.HTTPException as err:
                    self.bot.logger.error(f'Edit failed. $${err}$$ @@{pformat(embed.to_dict())}@@')
                await message.remove_reaction(emoji, self.bot.user)
                try:
                    return await message.remove_reaction(emoji, message.author)
                except discord.Forbidden:
                    return self.bot.logger.warn('Missing permission to remove reaction (manage_messages)')

    @commands.guild_only()
    @commands.group(name="stjerne")
    async def poeng_group(self, ctx):
        """
        Kategori for styring av poeng
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @poeng_group.command(name="diagram", aliases=["flow", "logikk", "hvordan"])
    async def chart(self, ctx):
        """
        Kommando for å se logikk for stjerner
        """
        takkeord = ", ".join(self.settings_data['takk'])
        chart = self.chart.replace("$takkord$", takkeord)
        chart_link = await mermaid(chart)
        embed = easy_embed(self, ctx)
        embed.set_image(url=chart_link)
        embed.title = "Logikken bak stjernene"
        await ctx.reply(embed=embed)

    @poeng_group.command(name="sjekk")
    async def check(self, ctx, user: discord.Member = None):
        """
        Kommando for å sjekke stjerner
        """
        if not user:
            user = ctx.author
        embed = easy_embed(self, ctx)
        counter = 0
        for msg in self.teller_data['meldinger']:
            for helper in self.teller_data['meldinger'][msg]['hjelper']:
                if helper == user.id:
                    counter += 1
                    if counter <= 5:
                        fyr = "Ukjent bruker"
                        try:
                            fyr = self.bot.get_user(self.teller_data['meldinger'][msg]['giver']).name
                        except AttributeError:
                            pass
                        embed.add_field(
                            name=f"Hjalp {fyr} her:",
                            value=f"[Link]({self.teller_data['meldinger'][msg]['link']})",
                            inline=False
                        )
        embed.title = "Boken"
        desc = f'{user.mention} har {counter} stjerner i boka.'
        if counter == 1:
            desc = f'{user.mention} har {counter} stjerne i boka'
        if 5 <= counter:
            desc = f'{user.mention} har {counter} stjerner i boka'
        if 10 <= counter:
            desc = f'{user.mention} har jobbet bra, her er det {counter} stjerner i boka!'
        if 15 <= counter:
            desc = f'{user.mention} har lagt inn en fantastisk jobb, {counter} stjerner i boka!'
        if 30 <= counter:
            desc = f'{user.mention} er utrolig, {counter} stjerner i boka!'
        if 50 <= counter:
            desc = f'{user.mention} er uvurderlig, {counter} stjerner i boka!'
        if embed.fields:
            desc += f'\n\nViser de {len(embed.fields)} første:'
        embed.description = desc
        await ctx.send(embed=embed)

    @commands.is_owner()
    @poeng_group.group()
    async def admin(self, ctx):
        """
        Kategori for instillinger
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @admin.command(name='takk')
    async def set_thanks(self, ctx, thanks_phrase):
        """
        Kommando for å sette takkeord
        """
        try:
            self.settings_data['takk'].append(thanks_phrase)
            await ctx.send(f'La til {thanks_phrase} i lista')
        except KeyError:
            self.settings_data['takk'] = []
            self.settings_data['takk'].append(thanks_phrase)
        except Exception:
            return self.bot.logger.error("Failed to set thanks_phrase: {thanks_phrase}")
        self.save_json('settings')
        self.load_json('settings')

    @tasks.loop(hours=5)
    async def cacher(self):
        """
        Mellomlagrer stjerner
        """
        self.save_json('teller')
        self.load_json('teller')
        self.bot.logger.debug('Reloaded star data cache')

    def load_json(self, mode):
        """
        Lagrer stjerner
        """
        if mode == 'teller':
            with codecs.open(self.teller_file, 'r', encoding='utf8') as json_file:
                self.teller_data = json.load(json_file)
        elif mode == 'settings':
            with codecs.open(self.settings_file, 'r', encoding='utf8') as json_file:
                self.settings_data = json.load(json_file)

    def save_json(self, mode):
        """
        Laster stjerner
        """
        if mode == 'teller':
            try:
                with codecs.open(self.teller_file, 'w', encoding='utf8') as outfile:
                    json.dump(self.teller_data, outfile, indent=4, sort_keys=True)
            except Exception as err:
                return self.bot.logger.warn(f'Failed to validate JSON before saving:\n{err}\n{self.teller_data}')
        elif mode == 'settings':
            try:
                with codecs.open(self.settings_file, 'w', encoding='utf8') as outfile:
                    json.dump(self.settings_data, outfile, indent=4, sort_keys=True)
            except Exception as err:
                return self.bot.logger.warn(f'Failed to validate JSON before saving:\n{err}\n{self.settings_data}')


    async def cog_unload(self):
        self.cacher.cancel()
        self.save_json('teller')


def check_folder(bot):
    # pylint: disable=missing-function-docstring
    _f = f'{bot.data_dir}/poeng'
    if not os.path.exists(_f):
        os.makedirs(_f)

def check_files(bot):
    # pylint: disable=missing-function-docstring
    files = [
        {f'{bot.data_dir}/poeng/teller.json': {'meldinger': {}}},
        {f'{bot.data_dir}/poeng/innstilinger.json': {'takk': []}}
    ]
    for i in files:
        for file, default in i.items():
            try:
                with codecs.open(file, 'r', encoding='utf8') as json_file:
                    json.load(json_file)
            except FileNotFoundError:
                with codecs.open(file, 'w', encoding='utf8') as outfile:
                    json.dump(default, outfile)


async def setup(bot):
    # pylint: disable=missing-function-docstring
    check_folder(bot)
    check_files(bot)
    await bot.add_cog(Poeng(bot))
