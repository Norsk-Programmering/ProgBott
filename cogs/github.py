# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.db import DB
from cogs.utils.db_tools import get_user, get_users
from cogs.utils.defaults import easy_embed
from cogs.utils.server import Server

import asyncio
import operator
import os
import random
import string
import threading

import requests


class Github(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        cacher = self.Cacher(self)
        self.bot.loop.create_task(cacher.loop())
        database = DB(data_dir=self.bot.data_dir)
        database.populate_tables()

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @commands.guild_only()
    @commands.group(name="github", aliases=["gh"])
    async def ghGroup(self, ctx):
        """
        Gruppe for Github kommandoer
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @ghGroup.command(name="auth", aliases=["add", "verify", "verifiser", "koble"])
    async def auth(self, ctx):
        """
        Kommando for å koble din Github- til din Discord-bruker
        """
        random_string = self.id_generator()
        is_user_registered = self.is_user_registered(ctx.author.id, random_string)

        if is_user_registered:
            return await ctx.send(ctx.author.mention + " du er allerede registrert!")

        try:
            embed = easy_embed(self, ctx)
            discord_id_and_key = "{}:{}".format(ctx.author.id, random_string)
            registration_link = "https://github.com/login/oauth/authorize" \
                                "?client_id={}&redirect_uri={}?params={}".format(
                                    self.bot.settings.github["client_id"],
                                    self.bot.settings.github["callback_uri"], discord_id_and_key
                                )
            embed.title = "Hei! For å verifisere GitHub kontoen din, følg lenken under"
            embed.description = f"[Verifiser med GitHub]({registration_link})"
            await ctx.author.send(embed=embed)
        except Exception as E:
            self.bot.logger.warn('Error when verifying Github user:\n%s', E)

        await ctx.send(ctx.author.mention + " sender ny registreringslenke på DM!")
        asyncio.sleep(120)  # Assume the user uses less than two minutes to auth
        self._get_users()

    @ghGroup.command(name="remove", aliases=["fjern"])
    async def remove(self, ctx):
        """
        Kommando for å fjerne kobling mellom Github- og Discord-bruker
        """
        conn = DB(data_dir=self.bot.data_dir).connection

        cursor = conn.cursor()

        cursor.execute("DELETE FROM github_users WHERE discord_id={}".format(ctx.author.id))

        conn.commit()

        return await ctx.send(ctx.author.mention + "fjernet Githuben din.")

    @ghGroup.command(name="repos", aliases=["stars", "stjerner"])
    async def show_repos(self, ctx, user: discord.Member = None):
        """
        Viser mest stjernede repoene til brukeren. maks  5
        """
        is_self = False
        if not user:
            user = ctx.author
            is_self = True
        gh_user = get_user(self, user.id)

        if gh_user is None:
            usr = user.name
            if is_self:
                usr = "Du"
            return await ctx.send(f"{usr} har ikke registrert en bruker enda.")

        embed = easy_embed(self, ctx)
        (_id, discord_id, auth_token, github_username) = gh_user

        gh_repos = requests.get(f"https://api.github.com/users/{github_username}/repos", headers={
            'Authorization': "token " + auth_token,
            'Accept': 'application/json'
        }).json()

        if len(gh_repos) == 0:
            return await ctx.send("Denne brukeren har ingen repos")

        stars = {}
        new_obj = {}

        for gh_repo in gh_repos:
            if gh_repo['private']:
                print(gh_repo['name'])
                continue
            stars[gh_repo['id']] = gh_repo['stargazers_count']
            new_obj[gh_repo['id']] = gh_repo

        stars = dict(sorted(stars.items(), key=operator.itemgetter(1), reverse=True))
        stop = 5 if (len(stars) >= 5) else len(stars)
        idrr = list(stars.items())
        embed.title = f"{stop} mest stjernede repoer"

        for n in range(0, stop):
            repo_id, *overflow = idrr[n]
            repo = new_obj[repo_id]
            title = f"{repo['name']} - ⭐:{repo['stargazers_count']}"
            desc = repo['description']
            if not repo['description']:
                desc = "Ingen beskrivelse oppgitt"
            desc += f"\n[Link]({repo['html_url']})"
            embed.add_field(name=title, value=desc, inline=False)

        await ctx.send(embed=embed)

    @ ghGroup.command(name="user", aliases=["meg", "bruker"])
    async def show_user(self, ctx, user: discord.Member = None):
        """
        Kommando som vier et sammendrag fra github brukeren
        """
        is_self = False
        if not user:
            user = ctx.author
            is_self = True
        gh_user = get_user(self, user.id)

        if gh_user is None:
            usr = user.name
            if is_self:
                usr = "Du"
            return await ctx.send(f"{usr} har ikke registrert en bruker enda.")

        (_id, discord_id, auth_token, github_username) = gh_user

        gh_user = requests.get("https://api.github.com/user", headers={
            'Authorization': "token " + auth_token,
            'Accept': 'application/json'
        }).json()

        embed = easy_embed(self, ctx)

        embed.title = gh_user["login"]
        embed.description = gh_user["html_url"]

        embed.set_thumbnail(url=gh_user["avatar_url"])

        embed.add_field(name="Følgere / Følger",
                        value="{} / {}".format(gh_user["followers"], gh_user["following"]), inline=False)
        embed.add_field(name="Biografi", value=gh_user["bio"], inline=False)
        embed.add_field(name="Offentlige repos", value=gh_user["public_repos"], inline=False)

        return await ctx.send(embed=embed)

    @ ghGroup.command(name="combined", aliases=["kombinert"])
    async def combined_stars(self, ctx):
        """
        Kommando som vier de 15 brukerene med mest stjerner totalt
        """
        embed = easy_embed(self, ctx)

        tot_stars = {}

        for repo_ in self.all_repos:
            repo = self.all_repos[repo_]
            try:
                tot_stars[str(repo['discord_user'])] = tot_stars[str(repo['discord_user'])] + repo['stargazers_count']
            except KeyError:
                tot_stars[str(repo['discord_user'])] = repo['stargazers_count']

        tot_stars = dict(sorted(tot_stars.items(), key=operator.itemgetter(1), reverse=True))

        stop = 15 if (len(tot_stars) >= 15) else len(tot_stars)
        idrr = list(tot_stars.items())
        embed.title = f"{stop} mest stjernede brukere"

        for n in range(0, stop):
            discord_user, stars = idrr[n]
            title = f"⭐:{stars}"
            desc = f"{self.bot.get_user(int(discord_user)).mention}"
            embed.add_field(name=title, value=desc, inline=False)

        return await ctx.send(embed=embed)

    @ ghGroup.command(name="users", aliases=["brukere", "total"])
    async def show_users(self, ctx):
        """
        Kommando som vier top 10 stjernede repoer samlet mellom alle registrerte brukere
        """
        embed = easy_embed(self, ctx)

        stop = 10 if (len(self.all_stars) >= 10) else len(self.all_stars)
        idrr = list(self.all_stars.items())
        embed.title = f"{stop} mest stjernede repoer"

        for n in range(0, stop):
            repo_id, *overflow = idrr[n]
            repo = self.all_repos[repo_id]
            title = f"{repo['name']} - ⭐:{repo['stargazers_count']}"
            desc = repo['description']
            if not repo['description']:
                desc = "Ingen beskrivelse oppgitt"
            desc += f"\n[Link]({repo['html_url']}) - {self.bot.get_user(repo['discord_user']).mention}"
            embed.add_field(name=title, value=desc, inline=False)

        return await ctx.send(embed=embed)

    def is_user_registered(self, discord_id, random_string):
        conn = DB(data_dir=self.bot.data_dir).connection

        if conn is None:
            return False

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM github_users WHERE discord_id={}".format(discord_id))

        rows = cursor.fetchone()

        if rows is not None:
            conn.close()
            return True

        cursor.execute("SELECT * FROM pending_users WHERE discord_id={}".format(discord_id))

        row = cursor.fetchone()

        if row is not None:
            cursor.execute("DELETE FROM pending_users WHERE discord_id={}".format(discord_id))

        cursor.execute("INSERT INTO pending_users(discord_id, verification) VALUES(?, ?);", (discord_id, random_string))

        conn.commit()
        conn.close()
        return False

    def _get_users(self):
        self.bot.logger.debug("Running GitHub user fetcher")
        self.all_stars = {}
        self.all_repos = {}
        users = get_users(self)

        members = []
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.id in members:
                    pass
                else:
                    members.append(member.id)

        stars = {}

        for user in users:
            (_id, discord_id, auth_token, github_username) = user

            if discord_id not in members:
                continue

            gh_repos = requests.get(f"https://api.github.com/users/{github_username}/repos", headers={
                'Authorization': "token " + auth_token,
                'Accept': 'application/json'
            }).json()

            if len(gh_repos) == 0:
                continue

            for gh_repo in gh_repos:
                if gh_repo['private']:
                    print(gh_repo['name'])
                    continue
                stars[gh_repo['id']] = gh_repo['stargazers_count']
                self.all_repos[gh_repo['id']] = {'discord_user': discord_id, **gh_repo}
        self.all_stars = dict(sorted(stars.items(), key=operator.itemgetter(1), reverse=True))

    async def remover(self, member):
        try:
            conn = DB(data_dir=self.bot.data_dir).connection
            cursor = conn.cursor()
            cursor.execute("DELETE FROM github_users WHERE discord_id={}".format(member.id))
            conn.commit()
            self.bot.logger.info("%s left, purged from database", member.name)
        except:
            pass

    class Cacher():
        def __init__(self, bot):
            self.bot = bot

        async def loop(self):
            while True:
                self.bot._get_users()
                await asyncio.sleep(60*60*12)


def check_folder(data_dir):
    f = f'{data_dir}/db'
    if not os.path.exists(f):
        os.makedirs(f)


def start_server(bot):
    server = threading.Thread(target=Server, kwargs={'data_dir': bot.data_dir, 'settings': bot.settings.github})
    server.start()


def setup(bot):
    check_folder(bot.data_dir)
    start_server(bot)
    n = Github(bot)
    bot.add_listener(n.remover, "on_member_remove")
    bot.add_cog(n)
