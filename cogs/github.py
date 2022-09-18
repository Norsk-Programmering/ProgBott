"""
Cog for githbhub komandoer
"""

# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.db import DB
from cogs.utils.db_tools import get_discord_user, get_user, get_users
from cogs.utils.defaults import easy_embed
from cogs.utils.my_errors import NoDM
from cogs.utils.server import Server

import asyncio
import operator
import os
import random
import string
import threading

import requests


class Github(commands.Cog):
    """
    Diverse github kommandoer
    """

    def __init__(self, bot):
        self.bot = bot
        cacher = self.Cacher(self)
        self.bot.loop.create_task(cacher.loop())
        database = DB(data_dir=self.bot.data_dir)
        database.populate_tables()

    def _id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return "".join(random.choice(chars) for _ in range(size))

    @commands.guild_only()
    @commands.group(name="github", aliases=["gh"])
    async def gh_group(self, ctx):
        """
        Gruppe for Github kommandoer
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @gh_group.command(name="auth", aliases=["add", "verify", "verifiser", "koble"])
    async def auth(self, ctx):
        """
        Kommando for å koble din Github- til din Discord-bruker
        """
        random_string = self._id_generator()
        _is_user_registered = self._is_user_registered(ctx.author.id, random_string)

        if _is_user_registered:
            return await ctx.reply(ctx.author.mention + " du er allerede registrert!")

        try:
            embed = easy_embed(self, ctx)
            discord_id_and_key = f"{ctx.author.id}:{random_string}"
            callback = f"{self.bot.settings.github['callback_uri']}" \
                       f"?params={discord_id_and_key}"
            registration_link = "https://github.com/login/oauth/authorize" \
                                f"?client_id={self.bot.settings.github['client_id']}" \
                                f"&redirect_uri={callback}"
            embed.title = "Hei! For å verifisere GitHub kontoen din, følg lenken under"
            embed.description = f"[Verifiser med GitHub]({registration_link})"
            await ctx.author.send(embed=embed)

            await ctx.reply(ctx.author.mention + " sender ny registreringslenke på DM!")
            await asyncio.sleep(120)  # Assume the user uses less than two minutes to auth
            self._get_users()
        except discord.Forbidden:
            raise NoDM
        except Exception as err:
            self.bot.logger.warn(f'Error when verifying Github user:\n{err}')

    @gh_group.command(name="remove", aliases=["fjern"])
    async def remove(self, ctx):
        """
        Kommando for å fjerne kobling mellom Github- og Discord-bruker
        """
        conn = DB(data_dir=self.bot.data_dir).connection

        cursor = conn.cursor()

        cursor.execute(f"DELETE FROM github_users WHERE discord_id={ctx.author.id}")

        conn.commit()

        return await ctx.reply(ctx.author.mention + "fjernet Githuben din.")

    @gh_group.command(name="repos", aliases=["stars", "stjerner"])
    async def show_repos(self, ctx, user: discord.Member = None):
        """
        Viser mest stjernede repoene til brukeren. maks  5 repoer
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
            return await ctx.reply(f"{usr} har ikke registrert en bruker enda.")

        embed = easy_embed(self, ctx)
        embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.display_avatar.url)
        (_id, _discord_id, auth_token, github_username) = gh_user

        gh_repos = self._get_repos(github_username, auth_token)

        if len(gh_repos) == 0:
            return await ctx.reply("Denne brukeren har ingen repos")

        stars = {}
        new_obj = {}

        for gh_repo in gh_repos:
            if gh_repo["private"]:
                continue
            stars[gh_repo["id"]] = gh_repo["stargazers_count"]
            new_obj[gh_repo["id"]] = gh_repo

        stars = dict(sorted(stars.items(), key=operator.itemgetter(1), reverse=True))
        stop = 5 if (len(stars) >= 5) else len(stars)
        idrr = list(stars.items())
        embed.title = f"{stop} mest stjernede repoer"

        for i in range(0, stop):
            repo_id, *_overflow = idrr[i]
            repo = new_obj[repo_id]
            title = f"{repo['name']} - ⭐:{repo['stargazers_count']}"
            desc = repo["description"]
            if not repo["description"]:
                desc = "Ingen beskrivelse oppgitt"
            desc += f"\n[Link]({repo['html_url']})"
            embed.add_field(name=title, value=desc, inline=False)

        await ctx.reply(embed=embed)

    @gh_group.command(name="user", aliases=["meg", "bruker"])
    async def show_user(self, ctx, user: discord.Member = None):
        """
        Kommando som viser et sammendrag fra github brukeren
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
            return await ctx.reply(f"{usr} har ikke registrert en bruker enda.")

        (_id, _discord_id, auth_token, _github_username) = gh_user

        gh_user = requests.get("https://api.github.com/user", timeout=10, headers={
            "Authorization": "token " + auth_token,
            "Accept": "application/json"
        }).json()

        embed = easy_embed(self, ctx)

        embed.title = gh_user["login"]
        embed.description = gh_user["html_url"]

        embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=gh_user["avatar_url"])

        embed.add_field(name="Følgere / Følger",
                        value=f"{gh_user['followers']} / {gh_user['following']}", inline=False)
        embed.add_field(name="Biografi", value=gh_user["bio"], inline=False)
        embed.add_field(name="Offentlige repos", value=gh_user["public_repos"], inline=False)

        return await ctx.reply(embed=embed)

    @gh_group.command(name="discord", aliases=["discordbruker"])
    async def show_discord_user(self, ctx, username):
        """
        Kommando som viser hvilken Discord-bruker som eier en GitHub-konto
        """
        discord_user = get_discord_user(self, username)
        if discord_user is None:
            return await ctx.reply("GitHub-brukeren har ikke knyttet en konto til sin Discord-bruker")

        (_id, discord_id, _auth_token, github_username) = discord_user

        user = self.bot.get_user(discord_id)

        embed = easy_embed(self, ctx)
        embed.description = f"Discord-brukeren til `{github_username}` er {user.mention}"
        return await ctx.reply(embed=embed)

    @gh_group.command(name="combined", aliases=["kombinert"])
    async def combined_stars(self, ctx):
        """
        Kommando som viser de 15 brukerene med mest stjerner totalt
        """
        embed = easy_embed(self, ctx)

        tot_stars = {}

        for repo_ in self.all_repos:
            repo = self.all_repos[repo_]
            try:
                tot_stars[str(repo["discord_user"])] = tot_stars[str(repo["discord_user"])] + repo["stargazers_count"]
            except KeyError:
                tot_stars[str(repo["discord_user"])] = repo["stargazers_count"]

        tot_stars = dict(sorted(tot_stars.items(), key=operator.itemgetter(1), reverse=True))

        stop = 15 if (len(tot_stars) >= 15) else len(tot_stars)
        idrr = list(tot_stars.items())
        embed.title = f"{stop} mest stjernede brukere"

        for i in range(0, stop):
            discord_user, stars = idrr[i]
            title = f"⭐:{stars}"
            desc = f"{self.bot.get_user(int(discord_user)).mention}"
            embed.add_field(name=title, value=desc, inline=False)

        return await ctx.reply(embed=embed)

    @gh_group.command(name="users", aliases=["brukere", "total"])
    async def show_users(self, ctx):
        """
        Kommando som viser top 10 stjernede repoer samlet mellom alle registrerte brukere
        """
        embed = easy_embed(self, ctx)

        stop = 10 if (len(self.all_stars) >= 10) else len(self.all_stars)
        idrr = list(self.all_stars.items())
        embed.title = f"{stop} mest stjernede repoer"

        for i in range(0, stop):
            repo_id, *_overflow = idrr[i]
            repo = self.all_repos[repo_id]
            title = f"{repo['name']} - ⭐:{repo['stargazers_count']}"
            desc = repo["description"]
            if not repo["description"]:
                desc = "Ingen beskrivelse oppgitt"
            desc += f"\n[Link]({repo['html_url']}) - {self.bot.get_user(repo['discord_user']).mention}"
            embed.add_field(name=title, value=desc, inline=False)

        return await ctx.reply(embed=embed)

    def _is_user_registered(self, discord_id, random_string):
        conn = DB(data_dir=self.bot.data_dir).connection

        if conn is None:
            return False

        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM github_users WHERE discord_id={discord_id}")

        rows = cursor.fetchone()

        if rows is not None:
            conn.close()
            return True

        cursor.execute(f"SELECT * FROM pending_users WHERE discord_id={discord_id}")

        row = cursor.fetchone()

        if row is not None:
            cursor.execute(f"DELETE FROM pending_users WHERE discord_id={discord_id}")

        cursor.execute("INSERT INTO pending_users(discord_id, verification) VALUES(?, ?);", (discord_id, random_string))

        conn.commit()
        conn.close()
        return False

    def _get_repos(self, user, token):
        headers = {
            "Authorization": "token " + token,
            "Accept": "application/json"
        }

        url = f"https://api.github.com/users/{user}/repos"
        res = requests.get(url, timeout=10, headers=headers, params={"per_page": 100, "page": 1})

        gh_repos = res.json()
        if isinstance(gh_repos, dict):
            return []
        while "next" in res.links.keys():
            res = requests.get(res.links["next"]["url"], timeout=10, headers=headers)
            gh_repos.extend(res.json())

        return gh_repos

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

            gh_repos = self._get_repos(github_username, auth_token)

            if len(gh_repos) == 0:
                continue

            for gh_repo in gh_repos:
                if gh_repo["private"]:
                    continue
                stars[gh_repo["id"]] = gh_repo["stargazers_count"]
                self.all_repos[gh_repo["id"]] = {"discord_user": discord_id, **gh_repo}
        self.all_stars = dict(sorted(stars.items(), key=operator.itemgetter(1), reverse=True))

    async def _remover(self, member):
        try:
            conn = DB(data_dir=self.bot.data_dir).connection
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM github_users WHERE discord_id={member.id}")
            conn.commit()
            self.bot.logger.info("%s left, purged from database", member.name)
        except Exception:
            pass

    class Cacher():
        """
        Klasse for mellomlagring
        """

        def __init__(self, bot):
            self.bot = bot

        async def loop(self):
            # pylint: disable=missing-function-docstring
            while True:
                self.bot._get_users()
                await asyncio.sleep(int(60*60*12))


def _check_folder(data_dir):
    _f = f"{data_dir}/db"
    if not os.path.exists(_f):
        os.makedirs(_f)


def _start_server(bot):
    server = threading.Thread(target=Server, kwargs={"data_dir": bot.data_dir, "settings": bot.settings.github})
    server.start()


async def setup(bot):
    # pylint: disable=missing-function-docstring
    _check_folder(bot.data_dir)
    _start_server(bot)
    _n = Github(bot)
    bot.add_listener(_n._remover, "on_member_remove")
    await bot.add_cog(_n)
