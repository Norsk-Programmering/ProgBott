import discord
from discord.ext import commands
import sqlite3

from cogs.utils.settings import Settings
from db import DB

settings = Settings(data_dir="data")

class Github(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.group(name="github")
    async def ghGroup(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @ghGroup.command(name="auth")
    async def auth(self, ctx):
        # First - attempt to localize if the user has already registered.
        is_user_registered  = self.check_user_registration(ctx.author.id)

        user_mention = "<@{}>: ".format(ctx.author.id)

        if not is_user_registered:
            try:
                registration_link = "https://github.com/login/oauth/authorize?client_id=8acb1c5ac6cf40da86e6&redirect_uri={}?discord_id={}".format(settings.github_callback_uri, ctx.author.id)
                await ctx.author.send("Hei! For å verifisere GitHub kontoen din, følg denne lenken: {}".format(registration_link))
            except Exception as e:
                return await ctx.send(user_mention + "du har ikke på innstillingen for å motta meldinger.")

            return await ctx.send(user_mention + "sender ny registreringslenke på DM!".format(ctx.author.id))

        return await ctx.send(user_mention + "du er allerede registrert!")
    def check_user_registration(self, discord_id):
        conn = DB().create_connection()

        if conn is None:
            return False

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM github_users WHERE discord_id={}".format(discord_id))

        rows = cursor.fetchone()

        conn.close()
        return rows is not None

def setup(bot):
    bot.add_cog(Github(bot))