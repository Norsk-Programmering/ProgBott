# Discord Packages
from os import name
import discord
from cogs.utils.defaults import embeder
from discord import embeds
from discord import message
from discord.ext import commands
import asyncio
from typing import Optional, List
import pprint


class Jobb(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.client.progbott.jobb
        self.settings = bot.client.progbott.settings

    @commands.command(name="kontakt")
    async def kontakt(self, ctx, message: discord.Message, *, tekst=None):
        """
        Kommando til å ta kontakt med jobbsøker
        """
        data = self.db.find_one({"id": message.id})
        bruker = await self.bot.fetch_user(data['bruker'])
        msg = f"{ctx.author.mention} ønsker å ta kontakt med deg, angående din jobbsøker-annonse"
        if tekst:
            msg += f". Hen har dette å si:\n\n```{tekst}```"
        await bruker.send(msg)
        await ctx.send("Bruker kontaktet")

    @commands.guild_only()
    @commands.is_owner()
    @commands.group(name="sok_adm")
    async def sok_adm(self, ctx):
        """
        Kategori for å håntere jobbsøker-annonse
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @sok_adm.command(name="kanal")
    async def adm_kanal(self, ctx, channel: Optional[discord.TextChannel] = None):
        """
        Kommando for å sette kanal for jobbsøker-annonse
        """
        if not channel:
            channel = ctx.channel
        data = {"_id": "jobbkanal", "guild": ctx.guild.id, "channel": channel.id}
        if not self.settings.find_one({"_id": "jobbkanal"}):
            self.settings.insert_one(data)
        else:
            self.db.update_one({"_id": "jobbkanal"}, {"$set": data})
        await ctx.send("Annonse kanal satt til: " + channel.mention)

    @sok_adm.group(name="rolle")
    async def adm_rolle(self, ctx):
        """
        Kategori for å håntere roller til annonse
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @adm_rolle.command(name="+")
    async def rolle_add(self, ctx, role: discord.Role):
        data = self.settings.find_one({"_id": "jobbkanal"})
        if not data:
            return await ctx.send(f"Ingen kanal er satt, bruk `{ctx.prefix}sok_adm kanal` for å sette kanal")

        data["ignore_roles"] = data["ignore_roles"].append(role.name) if data.get("ignore_roles") else [role.name]
        self.settings.update_one({"_id": "jobbkanal"}, {"$set": data})
        await ctx.send(f"La til {role.name} i lista")

    @commands.dm_only()
    @commands.group(name="sok")
    async def sok(self, ctx):
        """
        Kategori for å generere jobbsøker-annonse
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @sok.command()
    async def reg(self, ctx, plass: str, stilling: str):
        """Kommando for å registrere jobbsøker-annonse"""
        if self.db.find_one({"bruker": ctx.author.id}):
            return await ctx.send("Allerede registert")
        data = {"bruker": ctx.author.id, "plass": plass.replace("\"", ""), "stilling": stilling.replace("\"", "")}
        try:
            embed = embeder(self, ctx, data=data)
            await ctx.send(embed=embed, content="Din annonse ser nå slik ut, du kan fortsette med å utype annonsen "
                           f"med `{ctx.prefix}sok nokkelord`")
            self.db.insert_one(data)
        except Exception as e:
            self.bot.logger.error("%s", e)
            return await ctx.send("Noe gikk galt, vennligst fortell <@120970603556503552>")

    @sok.command()
    async def nokkelord(self, ctx):
        """Kommando for å sette nøkkelord bassert på roller"""
        data = self.db.find_one({"bruker": ctx.author.id})
        if not data:
            return await ctx.send("Du har ikke registrert deg")

        try:
            ignored_roles = self.settings.find_one({"_id": "jobbkanal"}).get("ignore_roles")
        except KeyError:
            return await ctx.send("Denne botten er ikke satt opp til jobbanonser enda")

        guild_id = self.settings.find_one({"_id": "jobbkanal"})
        guild = self.bot.get_guild(int(guild_id["guild"]))
        g_user = guild.get_member(ctx.author.id)

        roles = [role.name for role in g_user.roles if role.name not in ignored_roles]

        await ctx.send(f"Du har disse rollene på serveren:\n```{', '.join(roles)}```\n"
                       "Svar med 3 av disse du vil utheve, komma-sepparert")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.message.channel

        try:
            message = await self.bot.wait_for('message', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Ingen svar mottat, lukker menyen")
        else:
            nokkel = [role for role in roles if role.lower() in [m.strip()
                                                                 for m in message.clean_content.lower().split(",")]][:3]
            if not nokkel:
                return await ctx.send("Jeg klarte ikke å hente ut noen roller fra listen du ga meg, prøv på nytt")
            data["nokkelord"] = nokkel
            self.db.update_one({"bruker": ctx.author.id}, {"$set": data})

            embed = embeder(self, ctx, data=data)
            await ctx.send(embed=embed, content="Din annonse ser nå slik ut, du kan fortsette med å utype annonsen "
                           f"med `{ctx.prefix}sok utdanning`")
        await self.updater(ctx=ctx, data=data)

    @sok.command()
    async def utdanning(self, ctx, *, tekst):
        """Kommando for å sette utdanning"""
        data = self.db.find_one({"bruker": ctx.author.id})
        if not data:
            return await ctx.send("Du har ikke registrert deg")

        data["utdanning"] = tekst
        self.db.update_one({"bruker": ctx.author.id}, {"$set": data})

        embed = embeder(self, ctx, data=data)
        await ctx.send(embed=embed, content="Din annonse ser nå slik ut, du kan fortsette med å utype annonsen med "
                       f"`{ctx.prefix}sok erfaring`")
        await self.updater(ctx=ctx, data=data)

    @sok.command(name="om_meg")
    async def fritekst(self, ctx, *, tekst):
        """Kommando for å sette utdanning"""
        data = self.db.find_one({"bruker": ctx.author.id})
        if not data:
            return await ctx.send("Du har ikke registrert deg")

        data["fritekst"] = tekst
        self.db.update_one({"bruker": ctx.author.id}, {"$set": data})

        embed = embeder(self, ctx, data=data)
        await ctx.send(embed=embed, content="Din annonse ser nå slik ut, du kan fortsette med å utype annonsen med "
                       f"`{ctx.prefix}sok erfaring`")
        await self.updater(ctx=ctx, data=data)

    @sok.command()
    async def erfaring(self, ctx, *, tekst):
        """Kommando for å sette erfaring"""
        data = self.db.find_one({"bruker": ctx.author.id})
        if not data:
            return await ctx.send("Du har ikke registrert deg")

        data["erfaring"] = tekst
        self.db.update_one({"bruker": ctx.author.id}, {"$set": data})

        embed = embeder(self, ctx, data=data)
        await ctx.send(embed=embed, content="Din annonse ser nå slik ut, du kan fortsette med å utype annonsen med "
                       f"`{ctx.prefix}sok om_meg`")
        await self.updater(ctx=ctx, data=data)

    @sok.command()
    async def post(self, ctx):
        """Kommando som for å poste annonse"""
        data = self.db.find_one({"bruker": ctx.author.id})
        if not data:
            return await ctx.send("Du har ikke registrert deg")
        elif data.get("id"):
            return await ctx.send("Du har allerede postet en søknad")

        kanal = self.settings.find_one({"_id": "jobbkanal"})
        channel = self.bot.get_channel(kanal["channel"])

        msg = await channel.send("Genererer anonse")
        data["id"] = msg.id
        self.db.update_one({"bruker": ctx.author.id}, {"$set": data})
        await self.updater(ctx=ctx, data=data, do_check=False)

        await ctx.send(f"Søknadden er nå opprettet, du kan se den her {msg.jump_url}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.bot.logger.info("%s left, purged from database", member.name)
        data = self.db.find_one({"bruker": member.id})
        self.bot.db.delete_one({"bruker": member.id})
        await member.guild.fetch_message(data.get("id")).delete()

    async def updater(self, ctx, data, do_check=True):
        if not data.get("id"):
            return

        if do_check:
            msg = await ctx.send('Du har allerede sendt en post, oppdatere?')
            await msg.add_reaction('👍')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == '👍'

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                return await ctx.send('OK! oppdaterer ikke')
            else:
                pass

        kanal = self.settings.find_one({"_id": "jobbkanal"})
        channel = self.bot.get_channel(kanal["channel"])

        msg = await channel.fetch_message(data["id"])

        embed = embeder(self, ctx=ctx, data=data)
        content = f"For å ta kontakt med søker, send DM til {ctx.me.mention} med `{ctx.prefix}kontakt {msg.id}`"
        await msg.edit(content=content, embed=embed)
        await ctx.send("Melding oppdatert!")


def setup(bot):
    bot.add_cog(Jobb(bot))
