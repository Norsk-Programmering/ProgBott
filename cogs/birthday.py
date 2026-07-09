"""
Modul for bursdagsfunksjonalitet
"""

# Discord Packages
import discord
from discord.ext import commands, tasks

import json
import os
from datetime import datetime, time
from zoneinfo import ZoneInfo

NORWEGIAN_TIME = ZoneInfo("Europe/Oslo")
BIRTHDAY_CHECK_TIME = time(hour=8, minute=00, tzinfo=NORWEGIAN_TIME)
BIRTHDAY_ROLE_TIME = time(hour=23, minute=59, tzinfo=NORWEGIAN_TIME)


class Birthday(commands.Cog):
    """
    Klasse for bursdagsfunksjonalitet
    """

    def __init__(self, bot):
        self.bot = bot
        self.settings_file = bot.data_dir + "/birthday/innstilinger.json"
        self.birthdays_file = bot.data_dir + "/birthday/birthdays.json"
        self.settings = self.load_settings()
        self.data_cache = self.load_existing_data()
        self.check_todays_birthday.start()
        self.remove_birthday_roles.start()

    @discord.app_commands.command(name="bursdag", description="Legg til bursdag")
    @discord.app_commands.describe(date="Bursdag i format DD.MM")
    async def add_birthday(self, interaction: discord.Interaction, date: str):
        """
        Funksjon som lagrer bursdag
        """
        try:
            day, month = date.split(".")
            day = int(day)
            month = int(month)

            if not (1 <= day <= 31 and 1 <= month <= 12):
                raise ValueError

        except (ValueError, IndexError):
            return await interaction.response.send_message("Feil format! Bruk `DD.MM`(f.eks. 24.12)", ephemeral=True)

        user = interaction.user
        today = datetime.now()
        data = self.load_existing_data()
        user_id = str(interaction.user.id)

        try:
            if user_id not in data:
                data[user_id] = {"username": interaction.user.name, "birthday": date, "updated": today.isoformat()}
                self.data_cache = data
                self.save_data(data)
            else:
                last_updated_str = data[user_id].get("updated")
                if last_updated_str:
                    last_updated = datetime.fromisoformat(last_updated_str)
                    if (today - last_updated).days < 180:
                        return await interaction.response.send_message(
                            "Du kan bare endre bursdagen din hver 6 måned. Prøv igjen senere.", ephemeral=True
                        )
                data[user_id] = {"username": interaction.user.name, "birthday": date, "updated": today.isoformat()}
                self.data_cache = data
                self.save_data(data)

            await interaction.response.send_message(
                f"Lagret bursdag for {user.mention}: {date} \nDette blir slettet når serveren forlates."
            )
        except Exception as e:
            self.bot.logger.error(f"Error in add_birthday: {e}")
            await interaction.response.send_message("En feil oppstod. Prøv igjen senere.", ephemeral=True)

    def load_existing_data(self):
        data = {}
        if os.path.exists(self.birthdays_file):
            with open(self.birthdays_file, "r") as file:
                data = json.load(file)
        return data

    def get_guild_from_settings(self):
        return self.bot.get_guild(self.settings.get("guild"))

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                return json.load(file)
        return {}

    def save_settings(self, setting):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

        try:
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}

        settings.update(setting)

        with open(self.settings_file, "w") as file:
            json.dump(settings, file, indent=4)

    def save_data(self, data):
        os.makedirs(os.path.dirname(self.birthdays_file), exist_ok=True)
        with open(self.birthdays_file, "w") as file:
            json.dump(data, file, indent=4)

    @commands.guild_only()
    @commands.group(name="bursdag")
    async def birthday_group(self, ctx):
        """
        Kategori for styring av bursdagsfunksjonalitet
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @commands.is_owner()
    @birthday_group.group()
    async def admin(self, ctx):
        """
        Kategori for innstillinger
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @admin.command(name="guild")
    async def set_guild(self, ctx, guild_id):
        """
        Kommando for å sette guild_id i innstillinger
        """
        try:
            self.settings["guild"] = int(guild_id)
            await ctx.send(f"La til guild med guild id {guild_id} i lista")
        except KeyError:
            self.settings["guild"] = ""
            self.settings["guild"] = int(guild_id)
        except Exception:
            return self.bot.logger.error(f"Failed to set guild_id: {guild_id}")
        self.save_settings(self.settings)
        self.load_settings()

    @admin.command(name="channel")
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """
        Kommando for å sette channel_id i innstillinger
        """
        try:
            self.settings["channel_id"] = int(channel.id)
            await ctx.send(f"Satt kanal med kanal id {channel.id} som bursdagskanal")
        except Exception:
            return self.bot.logger.error(f"Failed to set channel_id: {channel.id}")
        self.save_settings(self.settings)
        self.load_settings()

    @admin.command(name="role")
    async def set_role(self, ctx, role: discord.Role):
        """
        Kommando for å sette bursdagsrolle i innstillinger
        """
        try:
            self.settings["birthday_role_id"] = int(role.id)
            await ctx.send(f"Satt rolle med id {role.id} som bursdagsrolle")
        except Exception:
            return self.bot.logger.error(f"Failed to set birthday_role_id: {role.id}")
        self.save_settings(self.settings)
        self.load_settings()

    @tasks.loop(time=BIRTHDAY_CHECK_TIME)
    async def check_todays_birthday(self):
        """
        Funksjon som sjekker om noen har bursdag en gang om dagen på et bestemt tidspunkt
        """

        today = datetime.now()
        day = today.day
        month = today.month

        matches = []

        for user_id, data in self.data_cache.items():
            try:
                b_day, b_month = map(int, data["birthday"].split("."))

                if b_day == day and b_month == month:
                    try:
                        guild = self.get_guild_from_settings()
                    except AttributeError:
                        self.bot.logger.error("Guild not found")
                        return

                    member = guild.get_member(int(user_id))

                    if member:
                        matches.append(member.mention)
                        role = discord.utils.get(guild.roles, id=self.settings.get("birthday_role_id"))
                        if role:
                            await member.add_roles(role)
                    else:
                        matches.append(data["username"])

            except (ValueError, KeyError):
                self.bot.logger.error(f"Invalid birthday format for user {user_id}: {data.get('birthday')}")

        if matches:
            birthday_list = "\n".join([f"🎂 {name}" for name in matches])
            embed = discord.Embed(
                title="🎉 Dagens bursdagsbarn! 🎉",
                description=birthday_list,
                color=discord.Color.gold(),
            )
            embed.set_footer(text="Gratulerer med dagen!")
            channel = self.bot.get_channel(self.settings.get("channel_id"))
            if channel:
                await channel.send(embed=embed)

    @tasks.loop(time=BIRTHDAY_ROLE_TIME)
    async def remove_birthday_roles(self):
        """
        Fjerner bursdagsrollen fra alle brukere hver dag ved midnatt
        """
        guild = self.get_guild_from_settings()
        role = discord.utils.get(guild.roles, id=self.settings.get("birthday_role_id"))
        if not role:
            return

        for user_id in self.data_cache:
            member = guild.get_member(int(user_id))
            if member and role in member.roles:
                try:
                    await member.remove_roles(role)
                except discord.Forbidden as e:
                    self.bot.logger.error(f"Failed to remove 'årsdag' role from {member.name}: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Fjerner bursdagsdata når en bruker forlater serveren
        """
        user_id = str(member.id)

        if user_id in self.data_cache:
            del self.data_cache[user_id]
            self.save_data(self.data_cache)
            self.bot.logger.debug(f"Birthday from {member.name} deleted")

    @check_todays_birthday.before_loop
    @remove_birthday_roles.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()


def check_files(bot):
    files = [
        {
            f"{bot.data_dir}/birthday/innstilinger.json": {
                "guild": "",
                "channel_id": "",
                "birthday_role_id": "",
            }
        },
        {f"{bot.data_dir}/birthday/birthdays.json": {}},
    ]

    folder = f"{bot.data_dir}/birthday"
    if not os.path.exists(folder):
        os.makedirs(folder)

    for i in files:
        for file, default in i.items():
            if not os.path.exists(file):
                with open(file, "w", encoding="utf8") as outfile:
                    json.dump(default, outfile)


async def setup(bot):
    check_files(bot)
    await bot.add_cog(Birthday(bot))
