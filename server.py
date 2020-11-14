# pylint: disable=no-self-argument
# Discord Packages
# from cogs.utils.db import DB
import discord
from cogs.utils.defaults import embeder

import asyncio
import os
import re
from pprint import pp, pprint

import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from quart import Quart, redirect, render_template, request

load_dotenv()

app = Quart(__name__, static_folder="server/static", template_folder="server/templates")


@app.before_serving
async def before_serving():
    loop = asyncio.get_event_loop()
    app.client = MongoClient('localhost', 27017)
    app.discord_client = DiscordClient()
    app.bot = app.discord_client.bot
    await app.discord_client.bot.login(os.getenv("TOKEN"))
    loop.create_task(app.discord_client.bot.connect())
    app.guild_elem = app.client.progbott.settings.find_one({"_id": "jobbkanal"})
    app.guild = app.bot.get_guild(int(app.guild_elem["guild"]))


@app.route("/")
async def index():
    return await render_template("index.html")


@app.errorhandler(404)
async def page_not_found(e):
    return await render_template("error.html", error=e, code=404), 404


@app.errorhandler(500)
async def internal_server_error(e):
    return await render_template("error.html", error=e, code=500), 500


@app.route("/jobb/send_jobb", methods=["PUT"])
async def test_():
    if (user := request.args.get('bruker')) is None:
        return {"Error": "Ingen bruker oppgitt"}, 400
    if (data := app.client.progbott.jobb.find_one({"bruker": user})) is None:
        return {"Error": "Denne brukeren har ikke oppretet en annonse"}, 400

    channel = app.bot.get_channel(app.guild_elem["channel"])

    if not data.get("id"):
        msg = await channel.send("Genererer anonse")
        data["id"] = msg.id

        embed = embeder(app, ctx=user, data=data)
        content = f"For å ta kontakt med søker, send DM til {app.bot.user.mention} med `.kontakt {msg.id}`"
        await msg.edit(content=content, embed=embed)

        resp = app.client.progbott.jobb.update_one({"bruker": user}, {"$set": data})
        data.pop("_id")
        if not resp.acknowledged:
            return {"Error": "Klarte ikke å skrive til databasen"}, 400
        return {"Ok": str(resp.acknowledged), "data": data}
    if data.get("id"):
        msg = await channel.fetch_message(data["id"])

        embed = embeder(app, ctx=user, data=data)
        content = f"For å ta kontakt med søker, send DM til {app.bot.user.mention} med `.kontakt {msg.id}`"
        await msg.edit(content=content, embed=embed)
        data.pop("_id")
        return {"Ok": "Melding oppdatert", "data": data}
    else:
        data.pop("_id")
        return {"Error": "Noe gikk sikkelig galt", "data": data}, 400


@app.route("/jobb/oppdater_jobb", methods=["PUT"])
async def jobb_put_ny_oppdater_jobb():
    if (user := request.args.get('bruker')) is None:
        return {"Error": "Ingen bruker oppgitt"}, 400
    if (data := app.client.progbott.jobb.find_one({"bruker": user})) is None:
        return {"Error": "Denne brukeren har ikke oppretet en annonse"}, 400

    if (utdanning := request.args.get('utdanning')):
        data["utdanning"] = utdanning
    if (fritekst := request.args.get('fritekst')):
        data["fritekst"] = fritekst
    if (erfaring := request.args.get('erfaring')):
        data["erfaring"] = erfaring
    if (plass := request.args.get('plass')):
        data["plass"] = plass
    if (stilling := request.args.get('stilling')):
        data["stilling"] = stilling

    resp = app.client.progbott.jobb.update_one({"bruker": user}, {"$set": data})
    if not resp.acknowledged:
        return {"Error": "Klarte ikke å skrive til databasen"}, 400
    data.pop("_id")

    return {"Ok": str(resp.acknowledged), "data": data}


@app.route("/jobb/ny_jobb", methods=["POST"])
async def jobb_post_ny_jobb():
    if (user := request.args.get('bruker')) is None:
        return {"Error": "Ingen bruker oppgitt"}, 400
    if (plass := request.args.get('plass')) is None:
        return {"Error": "Ingen plass oppgitt"}, 400
    if (stilling := request.args.get('stilling')) is None:
        return {"Error": "Ingen stilling oppgitt"}, 400
    if (data := app.client.progbott.jobb.find_one({"bruker": user})):
        return {"Error": "Denne brukeren har allerede oppretet en annonse"}, 400
    data = {"bruker": user, "plass": plass.replace("\"", ""), "stilling": stilling.replace("\"", "")}

    resp = app.client.progbott.jobb.insert_one(data)
    if not resp.acknowledged:
        return {"Error": "Klarte ikke å skrive til databasen"}, 400

    return {"Ok": str(resp.acknowledged), "data": data}


@app.route("/jobb/jobber")
async def jobb_get_jobber():
    jobs = list(app.client.progbott.jobb.find({"id": {"$exists": True}}))
    data = {}

    for job in jobs:
        i = job["id"]
        job.pop("_id")
        job.pop("id")
        job.pop("bruker")  # Prevent user leaking over the API
        data[i] = job

    return data


@app.route("/discord/user/<discord_id>")
async def disc_get_usr(discord_id):
    guild = app.client.progbott.settings.find_one({"_id": "jobbkanal"})
    guild = app.bot.get_guild(int(guild["guild"]))
    user = guild.get_member(int(discord_id))

    data = {
        "avatar_url": str(user.avatar_url),
        "color": user.color.value,
        "discriminator": int(user.discriminator),
        "display_name": user.display_name,
        "joined": user.joined_at.timestamp(),
        "roles": {},
    }

    ignored_roles = app.client.progbott.settings.find_one({"_id": "jobbkanal"}).get("ignore_roles")

    for role in user.roles:
        if role.name not in ignored_roles:
            data["roles"][role.name] = {"position": role.position, "color": role.color.value}

    return data

# @app.route("/github/oauth/callback")
# def callback():
#     query_code = request.args.get("code")

#     [discord_id, key] = request.args.get("params").split(":")

#     is_pending = get_is_pending(discord_id, key)

#     settings = app.config["settings"]

#     if not is_pending:
#         return "NOT_OK"

#     params = {
#         "client_id": settings.extra.github["client_id"],
#         "client_secret": settings.extra.github["secret"],
#         "code": query_code
#     }

#     check_key = requests.post("https://github.com/login/oauth/access_token",
#                               params=params, headers={"Accept": "application/json"})

#     check_key_json = check_key.json()

#     if "error" in check_key_json:
#         return "Invalid code passed."

#     access_token = check_key_json["access_token"]

#     user = requests.get("https://api.github.com/user", headers={
#         "Authorization": "token " + access_token,
#         "Accept": "application/json"
#     }).json()

#     inserted_user = insert_user(discord_id, access_token, user["login"])

#     if inserted_user:
#         delete_pending(discord_id)
#         return redirect(f"/github/oauth/complete/{user['login']}")
#     else:
#         return "NOT_OK"

# @app.route("/github/oauth/complete/<name>")
# def oauth_complete(name):
#     return render_template("oauth_complete.html", name=name)

# def insert_user(discord_id, auth_token, github_username):
#     conn = DB(data_dir=app.config["data_dir"]).connection

#     if conn is None:
#         return False

#     cursor = conn.cursor()

#     params = (discord_id, auth_token, github_username)

#     cursor.execute("INSERT OR REPLACE INTO github_users(discord_id, auth_token, github_username) VALUES(?, ?, ?);",
#                    params)
#     conn.commit()

#     conn.close()
#     return True

# def get_is_pending(discord_id, random_string):
#     conn = DB(data_dir=app.config["data_dir"]).connection

#     cursor = conn.cursor()

#     cursor.execute(f"SELECT * FROM pending_users WHERE discord_id={discord_id} AND verification='{random_string}'")

#     row = cursor.fetchone()

#     return row is not None

# def delete_pending(discord_id):
#     conn = DB(data_dir=app.config["data_dir"]).connection

#     cursor = conn.cursor()
#     cursor.execute(f"DELETE FROM pending_users WHERE discord_id={discord_id}")

#     conn.commit()


class DiscordClient:
    def __init__(self):
        self.bot = discord.Client(intents=discord.Intents.all())


app.run(debug=True, host="0.0.0.0")
