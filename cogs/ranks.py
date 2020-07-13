# Discord Packages
import discord
from discord.ext import commands, tasks

# Bot Utilities
from cogs.utils.defaults import easy_embed, timed_question, random_hex_color

import codecs
import json
import os
import time


class Ranks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.whitelist_data = {}
        self.whitelist_file = bot.data_dir + '/ranks/whitelist.json'
        self.load_json('whitelist')

    @commands.guild_only()
    @commands.group(name="rank", invoke_without_command=True)
    async def rGroup(self, ctx, *, args = None):
        """Kategori for styring av ranks"""
        if ctx.invoked_subcommand:
            pass
        elif args is None:
            await ctx.send_help(ctx.command)
        else:
            await self.use(ctx, rank=args)

    @rGroup.command(name="use")
    async def use(self, ctx, *, rank):
        self.load_json('whitelist')
        embed = easy_embed(self, ctx)
        role = discord.utils.find(lambda r: r.name.lower() == rank.lower(), ctx.guild.roles)
        if role is None:
            embed.title = f"Fant ikke rollen: {rank}!"
            embed.description = f"Rollen {rank} finnes ikke i denne serveren.\n"
            embed.description += "Hvis du vil legge til rollen i serveren, kontakt en server moderator."
            return await ctx.send(embed=embed)

        embed.colour = role.colour
        if role.id not in self.whitelist_data['whitelist']:
            embed.title = f"Denne rollen er utilgjengelig!"
            embed.description = f"Denne rollen er utilgjengelig for deg. Du kan ikke få den igjennom denne kommandoen."
            return await ctx.send(embed=embed)
        
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            embed.title = f"Fjernet rollen: {rank}!"
            return await ctx.send(embed = embed)

        await ctx.author.add_roles(role)
        embed.title = f"La til rollen: {rank}!"
        await ctx.send(embed = embed)

    @commands.has_permissions(manage_roles=True)
    @rGroup.command(name="whitelist")
    async def whitelist(self, ctx, *, rank):
        self.load_json('whitelist')
        embed = easy_embed(self, ctx)
        role = discord.utils.find(lambda r: r.name.lower() == rank.lower(), ctx.guild.roles)
        if role is None:
            # Rollen finnes ikke
            create_role_embed = easy_embed(self, ctx)
            create_role_embed.title = "Rollen finnes ikke. Lager rollen nå."
            await ctx.send(embed=create_role_embed)

            # Lag rollen
            role = await ctx.guild.create_role(name=rank, colour=discord.Colour(random_hex_color()), mentionable=True)        
        self.whitelist_data['whitelist'].append(role.id)
        self.save_json('whitelist')
        embed.title = "Rollen er nå tilgjengelig!"
        embed.description = "Du kan nå få tak i rollen igjennom botten."
        embed.colour = role.colour
        await ctx.send(embed=embed)

    @rGroup.command(name="list")
    async def list(self, ctx):
        self.load_json('whitelist')
        embed = easy_embed(self, ctx)
        embed.title = "Tilgjengelige roller"
        embed.description = ""
        for roleID in self.whitelist_data['whitelist']:
            role = ctx.guild.get_role(roleID)
            embed.description += role.name + "\n"
        await ctx.send(embed=embed)


    def load_json(self, mode):
        if mode == 'whitelist':
            with codecs.open(self.whitelist_file, 'r', encoding='utf8') as json_file:
                self.whitelist_data = json.load(json_file)

    def save_json(self, mode):
        if mode == 'whitelist':
            try:
                with codecs.open(self.whitelist_file, 'w', encoding='utf8') as outfile:
                    json.dump(self.whitelist_data, outfile, indent=4, sort_keys=True)
            except Exception as e:
                return self.bot.logger.warn('Failed to validate JSON before saving:\n%s\n%s' % (e, self.whitelist_data))


def check_folder(data_dir):
    f = f'{data_dir}/ranks'
    if not os.path.exists(f):
        os.makedirs(f)


def check_files(data_dir):
    files = [
        {f'{data_dir}/ranks/whitelist.json': {"whitelist":{}}},
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
    bot.add_cog(Ranks(bot))


