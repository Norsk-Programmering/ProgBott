# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.defaults import easy_embed

import asyncio
import codecs
import json
import os
import time


class GitHub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.brukere_data = {}
        self.settings_file = bot.data_dir + '/github/innstilinger.json'
        self.brukere_file = bot.data_dir + '/github/brukere.json'
        self.load_json('settings')
        self.load_json('brukere')

    @commands.guild_only()
    @commands.group(name="github")
    async def ghGroup(self, ctx):
        """Kategori for styring av github brukere"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @ghGroup.command(name="bind")
    async def bind(self, ctx, githubURL):
        self.load_json('brukere')
        self.brukere_data[ctx.author.id] = githubURL
        self.save_json('brukere')
        embed = easy_embed(self, ctx)
        embed.title = "Du har nå bundet din github bruker!"
        await ctx.send(embed=embed)

    @ghGroup.command(name="hent")
    async def hent(self, ctx, user: discord.Member = None):
        self.load_json('brukere')
        embed = easy_embed(self, ctx)
        if not str(user.id) in self.brukere_data:
            embed.title = "Fant ikke bruker!"
            embed.colour = 0xEB4034
            embed.description = f"{user.display_name} har ikke bundet sin GitHub bruker til ProgBott."
        else:
            embed.title = f"{user.display_name} sin GitHub"
            embed.url = self.brukere_data[str(user.id)]
        await ctx.send(embed=embed)

    def load_json(self, mode):
        if mode == 'brukere':
            with codecs.open(self.brukere_file, 'r', encoding='utf8') as json_file:
                self.brukere_data = json.load(json_file)
        elif mode == 'settings':
            with codecs.open(self.settings_file, 'r', encoding='utf8') as json_file:
                self.settings_data = json.load(json_file)

    def save_json(self, mode):
        if mode == 'brukere':
            try:
                with codecs.open(self.brukere_file, 'w', encoding='utf8') as outfile:
                    json.dump(self.brukere_data, outfile, indent=4, sort_keys=True)
            except Exception as e:
                return self.bot.logger.warn('Failed to validate JSON before saving:\n%s\n%s' % (e, self.teller_data))
        elif mode == 'settings':
            try:
                with codecs.open(self.settings_file, 'w', encoding='utf8') as outfile:
                    json.dump(self.settings_data, outfile, indent=4, sort_keys=True)
            except Exception as e:
                return self.bot.logger.warn('Failed to validate JSON before saving:\n%s\n\n%s' % (e, self.settings_data))


def check_folder(data_dir):
    f = f'{data_dir}/github'
    if not os.path.exists(f):
        os.makedirs(f)


def check_files(data_dir):
    files = [
        {f'{data_dir}/github/brukere.json': {}},
        {f'{data_dir}/github/innstilinger.json': {}}
    ]
    for i in files:
        for file, default in i.items():
            try:
                with codecs.open(file, 'r', encoding='utf8') as json_file:
                    json.load(json_file)
            except FileNotFoundError:
                with codecs.open(file, 'w', encoding='utf8') as outfile:
                    json.dump(default, outfile)


def setup(bot):
    check_folder(bot.data_dir)
    check_files(bot.data_dir)
    bot.add_cog(GitHub(bot))