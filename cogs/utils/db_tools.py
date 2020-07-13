from cogs.utils.db import DB


def get_user(self, discord_id):
    conn = DB(data_dir=self.bot.data_dir).connection

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM github_users WHERE discord_id={}".format(discord_id))

    rows = cursor.fetchone()

    return rows
