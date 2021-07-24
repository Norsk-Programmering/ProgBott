# Discord Packages
import discord
from discord.ext import commands
from discord.ui import View

# Bot Utilities
from cogs.utils.defaults import easy_embed

import asyncio
import codecs
import json
import os
import time


# Define a simple View that gives us a confirmation menu
class Confirm(View):
    def __init__(self, parent: discord.Message):
        super().__init__()
        self.value = None
        self.parent = parent

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id in [self.parent.author.id, 120970603556503552]:
            return True
        else:
            await interaction.response.send_message("Dette er ikke din melding", ephemeral=True)

    @discord.ui.button(label="Ja", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label="Nei", style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()


class Poeng(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.teller_data = {}
        self.cache_time = time.time()
        self.settings_file = bot.data_dir + "/poeng/innstilinger.json"
        self.teller_file = bot.data_dir + "/poeng/teller.json"
        self.load_json("settings")
        self.load_json("teller")
        self.bot.loop.create_task(self.cache_loop())

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.author.id == user.id:
            pass
        elif not str(reaction.message.id) in self.teller_data["meldinger"] and reaction.emoji == "🏅":
            if not reaction.message.author.bot:
                return await self.confirm_star(message=reaction.message, giver=user.id,
                                               hjelper=[reaction.message.author.id], dudes=None)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and message.mentions:
            await self._filter(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        try:
            if not after.author.bot and after.mentions \
                    and (after.edited_at.timestamp() - before.created_at.timestamp()) < 60:
                await self._filter(after, before=before)
        except AttributeError:
            pass

# TODO: halvstjerner?

    async def _filter(self, message, before=None, **kwarg):
        def check(message):
            for word in self.settings_data["takk"]:
                word_ = word.lower()
                content_ = message.content.lower()
                if (
                    word_ in content_ and
                        (
                            "hjelp" in
                            (
                                message.channel.name or
                                message.channel.category.name).lower()
                        )
                    ) or (
                        content_.startswith(word_) or
                        content_.endswith(word_) or
                        content_[:-1].endswith(word_)
                ):
                    return True
        if not before:
            if check(message):
                return await self.confirm_star(message)
        elif before:
            if check(before):
                return
            if check(message):
                return await self.confirm_star(message)

    async def confirm_star(self, message, dudes={"id": [], "mention": []}, **kwarg):
        for dude in message.mentions:
            if dude is self.bot.user:
                continue
            if dude is message.author:
                continue
            dudes["id"].append(dude.id)
            dudes["mention"].append(dude.mention)
        msg_data = {
            "hjelper": kwarg.get("hjelper") or dudes["id"],
            "giver": kwarg.get("giver") or message.author.id,
            "link": message.jump_url
        }
        conf_view = Confirm(parent=message)
        reply = await message.reply("Registrer stjerne?", view=conf_view)
        await message.channel.trigger_typing()
        await conf_view.wait()
        if conf_view.value is None:
            return await reply.delete()
        elif conf_view.value:
            menn = [self.bot.get_user(person).mention for person in msg_data["hjelper"]]
            embed = easy_embed(self, message)
            embed.title = "Ny stjerne tildelt!"
            embed.description = f'<@{msg_data["giver"]}> ga {", ".join(menn)} en stjerne!'
            self.teller_data["meldinger"][str(message.id)] = msg_data
            self.cacher()
            await reply.edit(content=None, embed=embed, view=[])
        else:
            return await reply.delete()

    @commands.guild_only()
    @commands.group(name="stjerne")
    async def pGroup(self, ctx):
        """
        Kategori for styring av poeng
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @pGroup.command(name="sjekk")
    async def check(self, ctx, user: discord.Member = None):
        """
        Komanndo for å sjekke stjerner
        """
        if not user:
            user = ctx.author
        embed = easy_embed(self, ctx)
        counter = 0
        for msg in self.teller_data["meldinger"]:
            for helper in self.teller_data["meldinger"][msg]["hjelper"]:
                if helper == user.id:
                    counter += 1
                    if counter <= 5:
                        fyr = "Ukjent bruker"
                        try:
                            fyr = self.bot.get_user(self.teller_data["meldinger"][msg]["giver"]).name
                        except AttributeError:
                            pass
                        embed.add_field(
                            name=f"Hjalp {fyr} her:",
                            value=f'[Link]({self.teller_data["meldinger"][msg]["link"]})',
                            inline=False
                        )
        embed.title = "Boken"
        desc = f"{user.mention} har {counter} stjerner i boka."
        if counter == 1:
            desc = f"{user.mention} har {counter} stjerne i boka"
        if 5 <= counter:
            desc = f"{user.mention} har {counter} stjerner i boka"
        if 10 <= counter:
            desc = f"{user.mention} har jobbet bra, her er det {counter} stjerner i boka!"
        if 15 <= counter:
            desc = f"{user.mention} har lagt inn en fantastisk jobb, {counter} stjerner i boka!"
        if embed.fields:
            desc += f"\n\nViser de {len(embed.fields)} første:"
        embed.description = desc
        await ctx.send(embed=embed)

    @commands.is_owner()
    @pGroup.group()
    async def admin(self, ctx):
        """
        Kategori for instillinger
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @admin.command(name="takk")
    async def set_thanks(self, ctx, thanks_phrase):
        """
        Kommando for å sette takkeord
        """
        try:
            self.settings_data["takk"].append(thanks_phrase)
            await ctx.send(f"La til {thanks_phrase} i lista")
        except KeyError:
            self.settings_data["takk"] = []
            self.settings_data["takk"].append(thanks_phrase)
        except Exception:
            return self.bot.logger.error("Failed to set thanks_phrase: %s" % thanks_phrase)
        self.save_json("settings")
        self.load_json("settings")

    async def cache_loop(self):
        while True:
            self.cacher()
            await asyncio.sleep(60*60*5)

    def cacher(self):
        if time.time() - 120 > float(self.cache_time):
            self.save_json("teller")
            self.load_json("teller")
            self.bot.logger.debug("Reloaded data cache")
            self.cache_time = time.time()

    def load_json(self, mode):
        if mode == "teller":
            with codecs.open(self.teller_file, "r", encoding="utf8") as json_file:
                self.teller_data = json.load(json_file)
        elif mode == "settings":
            with codecs.open(self.settings_file, "r", encoding="utf8") as json_file:
                self.settings_data = json.load(json_file)

    def save_json(self, mode):
        if mode == "teller":
            try:
                with codecs.open(self.teller_file, "w", encoding="utf8") as outfile:
                    json.dump(self.teller_data, outfile, indent=4, sort_keys=True)
            except Exception as e:
                return self.bot.logger.warn("Failed to validate JSON before saving:\n%s\n%s" % (e, self.teller_data))
        elif mode == "settings":
            try:
                with codecs.open(self.settings_file, "w", encoding="utf8") as outfile:
                    json.dump(self.settings_data, outfile, indent=4, sort_keys=True)
            except Exception as e:
                return self.bot.logger.warn("Failed to validate JSON before saving:\n%s\n%s" % (e, self.settings_data))


def check_folder(data_dir):
    f = f"{data_dir}/poeng"
    if not os.path.exists(f):
        os.makedirs(f)


def check_files(data_dir):
    files = [
        {f"{data_dir}/poeng/teller.json": {"meldinger": {}}},
        {f"{data_dir}/poeng/innstilinger.json": {"takk": []}}
    ]
    for i in files:
        for file, default in i.items():
            try:
                with codecs.open(file, "r", encoding="utf8") as json_file:
                    json.load(json_file)
            except FileNotFoundError:
                with codecs.open(file, "w", encoding="utf8") as outfile:
                    json.dump(default, outfile)


def setup(bot):
    check_folder(bot.data_dir)
    check_files(bot.data_dir)
    bot.add_cog(Poeng(bot))


# TODO: make it save on unload
# def teardown(bot):
#     obj = Poeng(bot)
#     obj.save_json("teller")
#     print("I am being unloaded!")
