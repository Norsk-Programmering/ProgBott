from flask import Flask, request, render_template, redirect
import requests
import json
from cogs.utils.settings import Settings

from db import DB

settings = Settings(data_dir="data")

app = Flask(__name__)

class Server:
    def __init__(self):
        app.run(debug=False)

@app.route("/")
def index():
    return "Hello, world!"

@app.route("/github/oauth/callback")
def callback():
    query_code = request.args.get("code")
    discord_id = request.args.get("discord_id")

    params = {
        'client_id': settings.github_client_id,
        'client_secret': settings.github_secret,
        "code": query_code
    }

    check_key = requests.post('https://github.com/login/oauth/access_token',
       params=params,
       headers={
           'Accept': 'application/json'
       }
    )

    check_key_json = check_key.json()

    if "error" in check_key_json:
        return "Invalid code passed."

    access_token = check_key_json["access_token"]

    user = requests.get("https://api.github.com/user", headers={
        'Authorization': "token " + access_token,
        'Accept': 'application/json'
    }).json()

    inserted_user = insert_user(discord_id, access_token, user["login"])

    if inserted_user:
        return redirect("/github/oauth/complete/{}".format(user["login"]))
    else:
        return "NOT_OK"



@app.route("/github/oauth/complete/<name>")
def oauth_complete(name):
    return render_template("oauth_complete.html", name=name)


def insert_user(discord_id, auth_token, github_username):
    conn = DB().create_connection()

    if conn is None:
        return False

    cursor = conn.cursor()

    params = (discord_id, auth_token, github_username)

    cursor.execute("INSERT OR REPLACE INTO github_users(discord_id, auth_token, github_username) VALUES(?, ?, ?);", params)
    conn.commit()

    conn.close()
    return True




