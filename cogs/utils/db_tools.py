"""
Hjelpeklasse for databaseoperasjoner
"""
# pylint: disable=missing-function-docstring

# Bot Utilities
from cogs.utils.db import DB


def get_user(self, discord_id):
    conn = DB(data_dir=self.bot.data_dir).connection

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM github_users WHERE discord_id={discord_id}")

    row = cursor.fetchone()

    return row


def get_discord_user(self, gh_username):
    conn = DB(data_dir=self.bot.data_dir).connection

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM github_users WHERE github_username='%s'" % gh_username)

    row = cursor.fetchone()

    return row


def get_users(self):
    conn = DB(data_dir=self.bot.data_dir).connection

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM github_users")

    rows = cursor.fetchall()

    return rows
