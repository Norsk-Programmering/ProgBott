import discord
from discord.ext import commands
import sqlite3

from cogs.utils.settings import Settings
from db import DB

import string
import random
import requests
import json

from cogs.utils.defaults import easy_embed

settings = Settings(data_dir="data")

class Github(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @commands.guild_only()
    @commands.group(name="github")
    async def ghGroup(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @ghGroup.command(name="auth")
    async def auth(self, ctx):
        # First - attempt to localize if the user has already registered.
        random_string = self.id_generator()
        is_user_registered  = self.is_user_registered(ctx.author.id, random_string)

        user_mention = "<@{}>: ".format(ctx.author.id)

        if is_user_registered:
            return await ctx.send(user_mention + "du er allerede registrert!")

        try:
            discord_id_and_key = "{}:{}".format(ctx.author.id, random_string)
            registration_link = "https://github.com/login/oauth/authorize?client_id=8acb1c5ac6cf40da86e6&redirect_uri={}?params={}".format(settings.github_callback_uri, discord_id_and_key)
            await ctx.author.send("Hei! For å verifisere GitHub kontoen din, følg denne lenken: {}.".format(registration_link))
        except Exception as e:
            return await ctx.send(user_mention + "du har ikke på innstillingen for å motta meldinger.")

        return await ctx.send(user_mention + "sender ny registreringslenke på DM!".format(ctx.author.id))

    @ghGroup.command(name="remove")
    async def remove(self, ctx):
        user_mention = "<@{}>: ".format(ctx.author.id)
        conn = DB().create_connection()

        cursor = conn.cursor()

        cursor.execute("DELETE FROM github_users WHERE discord_id={}".format(ctx.author.id))

        conn.commit()

        return await ctx.send(user_mention + "fjernet Githuben din.")

    @ghGroup.command(name="me")
    async def me(self, ctx):
        user = self.get_user(ctx.author.id)

        if user is None:
            return await ctx.send("Du har ikke registrert en bruker enda.")

        (_id, discord_id, auth_token, github_username) = user

        user = requests.get("https://api.github.com/user", headers={
            'Authorization': "token " + auth_token,
            'Accept': 'application/json'
        }).json()


        embed = easy_embed(self, ctx)

        embed.title = user["login"]
        embed.description = user["html_url"]

        embed.set_thumbnail(url=user["avatar_url"])

        embed.add_field(name="Følgere / Følger", value="{} / {}".format(user["followers"], user["following"], inline=False))
        embed.add_field(name="Biografi", value=user["bio"], inline=False)
        embed.add_field(name="Offentlige repos", value=user["public_repos"], inline=False)

        return await ctx.send(embed=embed)

    def get_user(self, discord_id):
        conn = DB().create_connection()

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM github_users WHERE discord_id={}".format(discord_id))

        rows = cursor.fetchone()

        return rows


    def is_user_registered(self, discord_id, random_string):
        conn = DB().create_connection()

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

def setup(bot):
    bot.add_cog(Github(bot))