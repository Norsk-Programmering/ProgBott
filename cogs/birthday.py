"""
Modul for bursdagsfunksjonalitet
"""

import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime, time
from zoneinfo import ZoneInfo

NORWEGIAN_TIME = ZoneInfo("Europe/Oslo")
BIRTHDAY_CHECK_TIME = time(hour=17, minute=21, tzinfo=NORWEGIAN_TIME)


class Birthday(commands.Cog):
    """
    Klasse for bursdagsfunksjonalitet
    """

    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1502653422682378242
        self.birthdays_file = bot.data_dir + "/birthday/birthdays.json"
        self.data_cache = self.load_existing_data()
        self.check_todays_birthday.start()

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
            return await interaction.response.send_message(
                "Feil format! Bruk `DD.MM`(f.eks. 24.12)", ephemeral=True
            )

        user = interaction.user
        user_id = str(interaction.user.id)
        data = self.load_existing_data()
        data[user_id] = {"username": interaction.user.name, "birthday": date}
        self.data_cache = data
        self.save_data(data)

        await interaction.response.send_message(
            f"Lagret bursdag for {user.mention}: {date}"
        )

    def load_existing_data(self):
        data = {}
        if os.path.exists(self.birthdays_file):
            with open(self.birthdays_file, "r") as file:
                data = json.load(file)
        return data

    def save_data(self, data):
        os.makedirs(os.path.dirname(self.birthdays_file), exist_ok=True)
        with open(self.birthdays_file, "w") as file:
            json.dump(data, file, indent=4)

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
                    guild = self.bot.guilds[0]
                    member = guild.get_member(int(user_id))

                    if member:
                        matches.append(member.mention)
                    else:
                        matches.append(data["username"])

            except (ValueError, KeyError):
                continue

        if matches:
            birthday_list = "\n".join([f"🎂 {name}" for name in matches])
            embed = discord.Embed(
                title="🎉 Dagens bursdagsbarn! 🎉",
                description=birthday_list,
                color=discord.Color.gold(),
            )
            embed.set_footer(text="Gratulerer med dagen!")
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                await channel.send(embed=embed)

    @check_todays_birthday.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Birthday(bot))
