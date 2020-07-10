import sqlite3

class DB():
    def __init__(self):
        self.create_github_users = """
        CREATE TABLE IF NOT EXISTS github_users (
            id integer PRIMARY KEY,
            discord_id string NOT NULL,
            auth_token string NOT NULL,
            github_username string NOT NULL
        );
        """

    def populate_tables(self):
        conn = self.create_connection()

        try:
            c = conn.cursor()
            c.execute(self.create_github_users)
        except Exception as e:
            raise Exception("Something went wrong populating the database.")

        conn.close()

    def create_connection(self):
        conn = None

        try:
            conn = sqlite3.connect("./db/github.sqlite")
            return conn
        except:
            raise Exception("Something went wrong connecting to the database. Are you sure github.sqlite exists?")

        return conn

