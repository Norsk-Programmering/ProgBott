"""
Modul for den innebyde webserveren
"""

# Bot Utilities
from cogs.utils.db import DB

import requests
from flask import Flask, redirect, render_template, request
from markupsafe import Markup

app = Flask(__name__, static_folder="../../static", template_folder="../../templates")


class Server:
    """
    Klasse for initalisering av Flask
    """

    def __init__(self, debug=False, **kwargs):
        for key, value in kwargs.items():
            app.config[key] = value
        app.run(debug=debug, host="0.0.0.0")


@app.route("/")
def _index():
    return render_template("index.html")


@app.route("/tos")
@app.route("/terms-of-service")
@app.route("/terms")
def _tos():
    with open("terms-of-service.md") as f:
        file_content = f.read()

    return render_template("markdown.html", markdown=Markup(file_content))


@app.route("/privacy")
@app.route("/privacy-policy")
def _privacy():
    with open("privacy-policy.md") as f:
        file_content = f.read()

    return render_template("markdown.html", markdown=Markup(file_content))


@app.errorhandler(404)
def _page_not_found(e):
    return render_template("error.html", error=e, code=404), 404


@app.errorhandler(500)
def _internal_server_error(e):
    return render_template("error.html", error=e, code=500), 500


@app.route("/github/oauth/callback")
def callback():
    """
    Rute som håndterer callback fra Github Oauth
    """

    query_code = request.args.get("code")

    [discord_id, key] = request.args.get("params").split(":")

    is_pending = _get_is_pending(discord_id, key)

    settings = app.config["settings"]

    if not is_pending:
        return "NOT_OK"

    params = {
        "client_id": settings["client_id"],
        "client_secret": settings["secret"],
        "code": query_code
    }

    check_key = requests.post("https://github.com/login/oauth/access_token",
                              params=params, headers={"Accept": "application/json"})

    check_key_json = check_key.json()

    if "error" in check_key_json:
        return "Invalid code passed."

    access_token = check_key_json["access_token"]

    user = requests.get("https://api.github.com/user", headers={
        "Authorization": "token " + access_token,
        "Accept": "application/json"
    }).json()

    inserted_user = _insert_user(discord_id, access_token, user["login"])

    if inserted_user:
        _delete_pending(discord_id)
        return redirect(f"/github/oauth/complete/{user['login']}")
    else:
        return "NOT_OK"


@app.route("/github/oauth/complete/<name>")
def _oauth_complete(name):
    return render_template("oauth_complete.html", name=name)


def _insert_user(discord_id, auth_token, github_username):
    conn = DB(data_dir=app.config["data_dir"]).connection

    if conn is None:
        return False

    cursor = conn.cursor()

    params = (discord_id, auth_token, github_username)

    cursor.execute("INSERT OR REPLACE INTO github_users(discord_id, auth_token, github_username) VALUES(?, ?, ?);",
                   params)
    conn.commit()

    conn.close()
    return True


def _get_is_pending(discord_id, random_string):
    conn = DB(data_dir=app.config["data_dir"]).connection

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM pending_users WHERE discord_id={discord_id} AND verification='{random_string}'")

    row = cursor.fetchone()

    return row is not None


def _delete_pending(discord_id):
    conn = DB(data_dir=app.config["data_dir"]).connection

    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM pending_users WHERE discord_id={discord_id}")

    conn.commit()
