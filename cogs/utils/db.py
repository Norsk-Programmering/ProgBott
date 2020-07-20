import sqlite3


class DB():
    def __init__(self, data_dir):
        self.data_dir = data_dir
        try:
            self.connection = sqlite3.connect(f"{data_dir}/db/github.sqlite")
        except Exception:
            raise Exception("Something went wrong connecting to the database. Are you sure github.sqlite exists?")

    _create_github_users = """
    CREATE TABLE IF NOT EXISTS github_users (
        id integer PRIMARY KEY,
        discord_id string NOT NULL,
        auth_token string NOT NULL,
        github_username string NOT NULL
    );
    """

    _create_pending_table = """
    CREATE TABLE IF NOT EXISTS pending_users (
        id integer PRIMARY KEY,
        discord_id string NOT NULL,
        verification string NOT NULL
    )
    """

    def populate_tables(self):
        try:
            c = self.connection.cursor()
            c.execute(self._create_github_users)
            c.execute(self._create_pending_table)
        except Exception:
            raise Exception("Something went wrong populating the database.")

        self.connection.close()
