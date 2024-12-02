# Discord Packages
import discord
from discord.ext import commands, tasks

# Bot Utilities
from cogs.utils.Bot_version import bot_version
from cogs.utils.defaults import easy_embed, features, intents, statuses, userflags

import operator
import platform
import time
from datetime import datetime, timezone
from io import StringIO
from os import listdir, name
from random import choice
from re import IGNORECASE
from re import compile as re_compile
from re import search as re_search
from re import sub

from dateutil.relativedelta import relativedelta

TIMEDELTA_REGEX = (
    r'((?P<years>-?\d+)y)?'
    r'((?P<months>-?\d+)m)?'
    r'((?P<weeks>-?\d+)w)?'
    r'((?P<days>-?\d+)d)?'
    r'((?P<hours>-?\d+)h)?'
)
TIMEDELTA_PATTERN = re_compile(TIMEDELTA_REGEX, IGNORECASE)

presencePool = [
    {
        "name": "Ser etter stjerner",
        "emoji": "🤖"
    },
    {
        "name": "Vokter {stars} stjerner",
        "emoji": "⭐"
    },
]


class Misc(commands.Cog):
    """
    Klasse for diverse komandoer
    """

    def __init__(self, bot):
        self.bot = bot
        self.repo = "https://github.com/Norsk-Programmering/ProgBott"
        self.ico = "https://github.com/Norsk-Programmering/Profilering/raw/master/BotAvatar.gif"

    async def cog_load(self):
        self.presence.start()

    async def cog_unload(self):
        self.presence.cancel()

    def _get_uptime(self):
        now = time.time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        return days, hours, minutes, seconds

    async def parse_delta(self, human: str) -> str:  # gist.github.com/santiagobasulto/698f0ff660968200f873a2f9d1c4113c
        """ Parses a human readable timedelta (3d5h) into a datetime.timedelta.
        Delta includes:
        * Xy years
        * Xm months
        * Xw weeks
        * Xd days
        * Xh hours
        Values can be negative following timedelta's rules. Eg: -2w-5h
        """
        match = TIMEDELTA_PATTERN.match(human)
        if match:
            parts = {k: int(v) for k, v in match.groupdict().items() if v}
            return relativedelta(**parts)
        return None

    @commands.command(name="ping", hidden=True)
    async def _ping(self, ctx):
        """
        Komando for ping
        """
        embed = easy_embed(self, ctx)
        embed.title = "Ping!"
        start = time.perf_counter()
        message = await ctx.reply(embed=embed)
        end = time.perf_counter()
        duration = int((end - start) * 1000)
        embed.description = f"Pong!\nPing: {duration}ms | websocket: {int(self.bot.latency * 1000)}ms"
        await message.edit(embed=embed)

    @commands.command(name="oppetid", aliases=["uptime"], hidden=True)
    async def _uptime(self, ctx):
        """
        Komando for oppetid
        """
        days, hours, minutes, seconds = self._get_uptime()
        await ctx.reply(f"{days}d {hours}h {minutes}m {seconds}s")

    @commands.command(aliases=["farge"])
    async def syntax(self, ctx):
        """
        Guide på hvoran bruke kodeblokker
        """
        embed = easy_embed(self, ctx)
        embed.title = "Hvordan få vakre meldinger når man poster kode"
        embed.description = r"""
        Hei, du kan gjøre koden din mer leselig med å sende koden i kodeblokker.\n\n
        For vanlig kodeblokk skriv:\n\`\`\`\nconst dinKode = "Laget av meg"\nconsole.log(dinKode)\n\`\`\`\n
        Den kommer til å se ut som dette:\n```\nconst dinKode = "Laget av meg"\nconsole.log(dinKode)```\n
        Du kan også definere et språk, for å få syntax highlighting.\n
        For fargerik kodeblokk skriv:\n\`\`\`js\nconst dinKode = "Laget av meg"\nconsole.log(dinKode)\n\`\`\`\n
        Den kommer til å se ut som dette:\n```js\nconst dinKode = "Laget av meg"\nconsole.log(dinKode)```
        """  # noqa: W605
        await ctx.reply(embed=embed)

    @commands.command(name="guilds")
    @commands.is_owner()
    async def _guilds(self, ctx):
        """
        Komando for å liste servere
        """
        embed = easy_embed(self, ctx)
        guilds = ""
        for guild in self.bot.guilds:
            guilds += f"{guild.name}\n"
        embed.description = f"```\n{guilds}\n```"
        embed.title = f"{self.bot.user.name} is in"
        await ctx.reply(embed=embed)

    @commands.command()
    async def info(self, ctx):
        """
        Lister info om botten, og serverrelaterte instillinger
        """
        membercount = []
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.id in membercount:
                    pass
                else:
                    membercount.append(member.id)

        dev = await self.bot.fetch_user(self.bot.appinfo.owner.id)

        desc = f"Discord-programvareagent for Norsk programmering" \
            f"\nForbedringforslag mottas på [GitHub]({self.repo})"

        py_ver = platform.python_version()
        how = "Med Python såklart!" \
              f"\n**Python-versjon:** " \
              f"[{py_ver}](https://python.org/downloads/release/python-{py_ver.replace('.', '')}/)" \
              f"\n**Discord.py-versjon:** " \
              f"[{discord.__version__}](https://github.com/Rapptz/discord.py/releases/tag/v{discord.__version__}/)" \
              f"\n**ProgBott-versjon:** {bot_version}"

        intents_list = []

        for intent, _val in ctx.bot.intents:
            try:
                if intents[intent]:
                    intents_list.append(intents[intent])
            except KeyError:
                intents_list.append(intent)
                self.bot.logger.debug("intent %s is not translated", intent)

        guilds = len(self.bot.guilds)
        members = len(membercount)
        days, hours, minutes, seconds = self._get_uptime()

        uptimetext = f"{days}d {hours}t {minutes}m {seconds}s"
        embed = discord.Embed(color=discord.Colour.from_rgb(244, 1, 110), description=desc)
        embed.set_author(url=f"https://github.com/{dev.name}", name=dev.name, icon_url=dev.display_avatar.url)
        embed.set_thumbnail(url=self.ico)

        embed.add_field(name="Tjenere", value=str(guilds))
        embed.add_field(name="Hvor mange?", value=f"{members} brukere")
        embed.add_field(name="Oppetid", value=uptimetext)
        embed.add_field(name="Hvordan?", value=how, inline=False)

        if intents_list:
            embed.add_field(name="Mine Intensjoner:", value=", ".join(intents_list))

        await ctx.reply(embed=embed)

    @commands.command(aliases=["pullrequest", "draforespørsel", "pr"], hidden=True)
    async def pull_request(self, ctx):
        """
        Pwease appwove my puww wequest senpai ^_^ uwu
        """
        await ctx.message.delete()
        await ctx.send(f"<@{self.bot.appinfo.owner.id}>\nhttps://youtu.be/5xooMXyleXM")

    @commands.command(aliases=["topproller"])
    async def toproller(self, ctx, antall: int = None):
        """
        Kommando for å vise rollene med flest medlemmer
        """

        guild_roles = ctx.guild.roles  # Avoids fetching roles multiple times.

        if len(guild_roles) == 1:
            return await ctx.reply("Serveren har ikke nok roller")

        if antall is not None:  # Had to use "is not" due to 0 being type-casted to False
            if antall > len(guild_roles) - 1 or antall < 1:
                return await ctx.reply(f"Du må gi meg et rolleantall som er mellom 1 og {len(guild_roles) - 1}")

        roles = {}
        for role in guild_roles:
            if role.name != "@everyone":
                roles[role.id] = len(role.members)

        roles = dict(sorted(roles.items(), key=operator.itemgetter(1), reverse=True))
        embed = easy_embed(self, ctx)
        desc = ""
        counter = 0
        _max = antall or 10
        for role, members in roles.items():
            desc += f"{ctx.guild.get_role(role).mention}: {members}\n"
            counter += 1
            if counter == _max:
                break

        embed.description = desc
        embed.title = f"Viser topp {counter} roller"
        embed.set_thumbnail(url=self.ico)

        await ctx.reply(embed=embed)

    @commands.command(aliases=["guildinfo", "server", "serverinfo", "si", "gi"])
    async def guild(self, ctx):
        """
        Viser info om guilden
        """

        total_members = ctx.guild.member_count
        bot_members = 0
        online_members = 0
        idle_members = 0
        dnd_members = 0
        offline_members = 0
        for member in ctx.guild.members:
            if member.bot:
                bot_members += 1
            if str(member.status) == "online":
                online_members += 1
            elif str(member.status) == "idle":
                idle_members += 1
            elif str(member.status) == "dnd":
                dnd_members += 1
            elif str(member.status) == "offline":
                offline_members += 1

        roles = []
        for role in ctx.guild.roles:
            if role.is_premium_subscriber():
                roles.append(role.name + userflags["boost"])
                continue
            if role.name != "@everyone":
                roles.append(role.name)
        roles.reverse()
        roles = ", ".join(roles)
        if len(roles) > 1024:
            roles = "Skriv `.guildroller` for å se rollene"
        if roles == "":
            roles = "**Ingen roller**"

        boosters = []
        premium_subscribers = sorted(
            ctx.guild.premium_subscribers, key=lambda m: m.premium_since)
        for booster in premium_subscribers:
            boosters.append(booster.mention)
        boosters = ", ".join(boosters)
        if len(boosters) > 1024:
            boosters = "For mange boosters for å vise her"
        if boosters == "":
            boosters = "**Ingen boosters**"

        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        categories = len(ctx.guild.categories)
        total_channels = text_channels + voice_channels

        features_list = []
        if ctx.guild.features is not []:
            for feature in ctx.guild.features:
                try:
                    if features[feature]:
                        features_list.append(features[feature])
                except KeyError:
                    self.bot.logger.debug("feature %s is not translated", feature)
                    features_list.append(feature)
        features_list.sort()
        features_string = "\n".join(features_list)

        photos = {}
        if ctx.guild.splash:
            photos["Invitasjonsbilde"] = ctx.guild.splash.replace(static_format="png").url
        if ctx.guild.banner:
            photos["Banner"] = ctx.guild.banner.replace(static_format="png").url

        verification_level = {
            "none": "ingen",
            "low": "e-post",
            "medium": "e-post, registrert i 5 min",
            "high": "e-post, registrert i 5 min, medlem i 10 min",
            "extreme": "telefon"
        }
        verification = verification_level[str(ctx.guild.verification_level)]

        content_filter = {
            "disabled": "nei",
            "no_role": "for alle uten rolle",
            "all_members": "ja"
        }
        content = content_filter[str(ctx.guild.explicit_content_filter)]

        embed = discord.Embed(color=ctx.me.color, description=f"**Verifiseringskrav:** {verification}\n" +
                              f"**Innholdsfilter:** {content}\n" +
                              f"**Boost Tier:** {ctx.guild.premium_tier}\n" +
                              f"**Emoji:** {len(ctx.guild.emojis)}")
        embed.set_author(name=ctx.guild.name)
        if ctx.guild.icon is not None:
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.set_thumbnail(url=ctx.guild.icon.replace(static_format="png").url)
        embed.add_field(name="ID", value=ctx.guild.id)
        embed.add_field(name="Eier", value=ctx.guild.owner.mention)
        embed.add_field(name="Opprettet", value=f"{discord.utils.format_dt(ctx.guild.created_at)}\n" +
                        f"{discord.utils.format_dt(ctx.guild.created_at, style='R')}", inline=False)
        embed.add_field(name=f"Kanaler ({total_channels})", value=f"💬 Tekst: **{text_channels}**\n" +
                        f"🔊 Tale: **{voice_channels}**\n" +
                        f"🗃️ Kategorier: **{categories}**")
        embed.add_field(name=f"Medlemmer ({total_members})",
                        value=f"👤 Mennesker: **{int(total_members) - int(bot_members)}**\n" +
                        f"🤖 Båtter: **{bot_members}**\n" +
                        f"<:online:743471541169291335>{online_members} " +
                        f"<:idle:743471541127348255>{idle_members} " +
                        f"<:dnd:743471541093662840>{dnd_members} " +
                        f"<:offline:743471543543136266>{offline_members}")
        embed.add_field(name=f"Roller ({len(ctx.guild.roles) - 1})", value=roles, inline=False)
        if ctx.guild.premium_tier != 0:
            embed.add_field(name=f"Boosts ({ctx.guild.premium_subscription_count})", value=boosters, inline=False)

        if features_string != "":
            embed.add_field(name="Tillegsfunksjoner", value=features_string)

        if photos:
            photos_string = ""
            for key, value in photos.items():
                photos_string += f"[{key}]({value})\n"
            embed.add_field(name="Bilder", value=photos_string)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["serverroller", "guildroles", "serverroles"])
    async def guildroller(self, ctx):
        """
        Viser rollene i en guild
        """

        roles = []
        for role in ctx.guild.roles:
            if role.is_premium_subscriber():
                roles.append(role.name + userflags["boost"])
                continue
            if role.name != "@everyone":
                roles.append(role.name)
        if roles is []:
            roles = ["**Ingen Roller**"]
        roles.reverse()
        roles = ", ".join(roles)

        roles = roles.replace(", --", "\n--")
        roles = roles.replace("--, ", "--\n")

        if len(roles) > 2048:
            file = StringIO(roles)

            txt_file = discord.File(file, "roller.txt")
            await ctx.reply(file=txt_file)

            file.close()

            return

        if roles == "":
            roles = "**Ingen roller**"

        embed = discord.Embed(color=ctx.me.color, description=roles)
        embed.set_author(name=f"Roller ({len(ctx.guild.roles) - 1})")
        embed.set_footer(text=ctx.guild.name)
        if ctx.guild.icon is not None:
            embed.set_author(name=f"Roller ({len(ctx.guild.roles) - 1})", icon_url=ctx.guild.icon.url)
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["userinfo", "ui", "brukerinfo", "user"])
    async def bruker(self, ctx, *, bruker: discord.Member = None):
        """
        Viser info om en bruker
        """

        if not bruker:
            bruker = ctx.author

        app = ""
        if str(bruker.mobile_status) != "offline":
            app += "📱 "
        if str(bruker.web_status) != "offline":
            app += "🌐 "
        if str(bruker.desktop_status) != "offline":
            app += "💻"

        join_index = sorted(ctx.guild.members, key=lambda m: m.joined_at).index(bruker) + 1
        creation_index = sorted(ctx.guild.members, key=lambda m: m.created_at).index(bruker) + 1
        if bruker.premium_since:
            premium_index = sorted(ctx.guild.premium_subscribers, key=lambda m: m.premium_since).index(bruker) + 1

        bruker_joined_date = discord.utils.format_dt(bruker.joined_at, style="R")
        bruker_created_date = discord.utils.format_dt(bruker.created_at, style="R")

        ansatt = None
        roles = []
        for role in bruker.roles:
            if role.name != "@everyone":
                if role.name.endswith("-ansatt"):
                    ansatt = role.name
                roles.append(role.name)
        roles.reverse()
        roles = ", ".join(roles)

        if len(roles) > 1024:
            roles = "Skriv `.brukerroller` for å se rollene"
        if roles == "":
            roles = "**Ingen roller**"

        if str(bruker.color) != "#000000":
            color = bruker.color
        else:
            color = discord.Colour(0x99AAB5)

        status = statuses[str(bruker.status)]

        embed = discord.Embed(color=color)
        if bruker.public_flags.all():
            embed.description = f"{bruker.mention}\nID: {bruker.id}\n{status}\n{app} \
                {' '.join(userflags[m] if m in userflags else f':{m}:' for m, v in bruker.public_flags.all())}"
        else:
            embed.description = f"{bruker.mention}\nID: {bruker.id}\n{status}\n{app}"
        if bruker.display_name == bruker.name:
            embed.set_author(name=f"{bruker.display_name}", icon_url=bruker.display_avatar.url)
        else:
            embed.set_author(name=f"{bruker.global_name} | {bruker.display_name}",
                             icon_url=bruker.display_avatar.url)
        embed.set_thumbnail(url=bruker.display_avatar.replace(static_format="png").url)
        embed.add_field(name="Opprettet", value=bruker_created_date)
        embed.add_field(name="Ble med i serveren", value=bruker_joined_date)
        if bruker.premium_since:
            premium_since = discord.utils.format_dt(bruker.premium_since, style="R")
            embed.add_field(name="Boost", value=f"{premium_since}\n" +
                            f"Booster #{premium_index} av serveren", inline=False)
        embed.add_field(name=f"Roller ({len(bruker.roles) - 1})", value=roles, inline=False)
        embed.set_footer(text=f"#{join_index} Medlem av serveren | #{creation_index} Eldste brukeren på serveren")

        if ansatt:
            embed.add_field(name="Arbeidsplass", value=ansatt.replace("-ansatt", ""), inline=False)

        if bruker.activities:
            games = []
            for activity in bruker.activities:
                if not activity.name or activity.name == "Custom Status":
                    continue

                if type(activity) is discord.Spotify:
                    games.append(f"Viber til {activity.title} av {activity.artist} på Spotify")
                if type(activity) is discord.Game:
                    if activity.platform:
                        games.append(f"Spiller {activity.name} på {activity.platform}")
                    else:
                        games.append(f"Spiller {activity.name}")
                if type(activity) is discord.Streaming:
                    baseText = f"Stømmer {activity.game}"
                    if activity.platform:
                        baseText += (f" på {activity.platform}")
                    if activity.url:
                        baseText += (f"[{activity.name}]({activity.url})")
                    games.append(baseText)
                else:
                    games.append(activity.name)

            if games:
                games.sort()
                games = "\n".join(games)
                embed.add_field(name="Aktivitet", value=games, inline=False)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["userroles"])
    async def brukerroller(self, ctx, bruker: discord.Member = None):
        """
        Viser rollene til en bruker
        """

        if not bruker:
            bruker = ctx.author

        roles = []
        for role in bruker.roles:
            if role.is_premium_subscriber():
                roles.append(role.name + userflags["boost"])
                continue
            if role.name != "@everyone":
                roles.append(role.name)
        roles.reverse()
        roles = ", ".join(roles)

        if len(roles) > 2048:
            file = StringIO(roles)

            txt_file = discord.File(file, "roller.txt")
            await ctx.send(file=txt_file)

            file.close()

            return

        if roles == "":
            roles = "**Ingen roller**"

        if str(bruker.color) != "#000000":
            color = bruker.color
        else:
            color = discord.Colour(0x99AAB5)

        embed = discord.Embed(color=color, description=roles)
        embed.set_author(name=f"Roller ({len(bruker.roles) - 1})")
        embed.set_footer(text=bruker.display_name)
        if ctx.guild.icon is not None:
            embed.set_author(name=f"Roller ({len(bruker.roles) - 1})", icon_url=bruker.display_avatar.url)
            embed.set_footer(text=bruker.display_name, icon_url=bruker.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["roleinfo", "rolleinfo"])
    async def rolle(self, ctx, *, rolle: discord.Role):
        """
        Viser info om en rolle
        """

        if rolle.name == "@everyone":
            return await ctx.reply("Skriv inn en annen rolle enn `@everyone`")

        if str(rolle.color) != "#000000":
            color = rolle.color
        else:
            color = discord.Colour(0x99AAB5)

        hoisted = "Ja" if rolle.hoist else "Nei"
        mentionable = "Ja" if rolle.mentionable else "Nei"

        members = []
        for member in rolle.members:
            members.append(member.display_name)
        members = ", ".join(members)

        if len(members) > 1024:
            members = "For mange medlemmer for å vise her"
        if len(members) == 0:
            members = "**Ingen**"

        permissions = ", ".join([permission for permission, value in iter(rolle.permissions) if value is True])

        embed = discord.Embed(title=rolle.name, description=f"{rolle.mention}\n**ID:** {rolle.id}", color=color)
        embed.set_author(name=rolle.guild.name)
        if ctx.guild.icon is not None:
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.add_field(name="Fargekode", value=str(rolle.color))
        embed.add_field(name="Opprettet", value=discord.utils.format_dt(rolle.created_at, style="R"))
        embed.add_field(name="Posisjon", value=rolle.position)
        embed.add_field(name="Nevnbar", value=mentionable)
        if rolle.display_icon:
            embed.set_image(url=rolle.display_icon.url)
        if rolle.is_bot_managed():
            embed.add_field(name="Bot-håndert", value="Ja")
        if rolle.is_integration():
            embed.add_field(name="Integrasjon", value="Ja")
        if rolle.is_premium_subscriber():
            embed.add_field(name="Boost", value="Ja")
        embed.add_field(name="Vises separat i medlemsliste", value=hoisted)
        if permissions:
            embed.add_field(name="Tillatelser", value=permissions, inline=False)
        embed.add_field(name=f"Brukere med rollen ({len(rolle.members)})", value=members, inline=False)
        await ctx.reply(embed=embed)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def reload(self, ctx, cog):
        """Laster inn spesifisert cog på nytt"""

        cogs = [file[:-3] for file in listdir('cogs') if file.endswith('.py')]
        name_ = cog if cog in cogs else None
        if not name:
            return await ctx.reply(f"{cog} was not found")

        try:
            await self.bot.reload_extension(f'cogs.{name_}')
            await ctx.reply(f"{name_} was reloaded")
            self.bot.logger.debug("%s was reloaded", name_)
        except commands.ExtensionNotLoaded:
            return await ctx.reply(f"{name_} was not loaded")

    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_emojis=True))
    @commands.command(hidden=True)
    async def smekk(self, ctx, member: discord.Member = None):
        """
        Drar fram fluesmekkeren
        """
        if not member:
            await ctx.message.delete()
            return
        emote_dict = {511934458304397312: 773307285073428540, 386655733107785738: 472225917197090816}
        try:
            emote_str = self.bot.get_emoji(emote_dict[ctx.guild.id])
        except KeyError:
            emote_str = ":hand_splayed:"
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            self.bot.logger.warn('Missing permission to remove message (manage_messages)')
        await ctx.send(f"Smekk - ka farsken! {member.mention} {emote_str}{emote_str}{emote_str}")

    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.command(aliases=['owoify', 'uwu'])
    async def owo(self, ctx, *, tekst: str = None):  # https://github.com/LBlend/MornBot/blob/master/cogs/Misc.py#L149-L170
        """Oversetter tekst til owo"""

        context = ctx.message
        content = tekst

        if ctx.message.reference:
            context = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            content = context.content
            await ctx.message.delete(delay=3)

        owo_rules = {
            'r': 'w',
            'l': 'w',
            'R': 'W',
            'L': 'W',
            'n': 'ny',
            'N': 'Ny',
            'ove': 'uv'
        }
        for key, value in owo_rules.items():
            content = sub(key, value, content)

        if not content or len(content) >= 1000:
            return

        embed = discord.Embed(color=ctx.me.color, description=content, title="UwUet")
        await context.reply(embed=embed)

    @commands.command(alises=["brukeresiden"])
    async def brukere_siden(self, ctx, *, tid: str):
        """
        Viser medlemmer som har blitt med i løpet av en spesifisert tidsperiode
        Relativ (1d, 2w, 3m, 4y) eller absolutt (2020-01-01)
        """

        if not ctx.guild.chunked:
            await ctx.guild.chunk(cache=True)

        stamp = None

        if tid.endswith(("h", "d", "w", "m", "y")):
            try:
                delta = await self.parse_delta(tid)
            except ValueError:
                return await ctx.reply("Ugyldig tidsperiode")

            if delta is None:
                return await ctx.reply("Ugyldig tidsperiode")

            stamp = discord.utils.utcnow() - delta
        elif re_search(r"^\d{4}-\d{2}-\d{2}$", tid):
            try:
                stamp = datetime.strptime(tid, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                return await ctx.reply("Ugyldig tidsperiode")

        if stamp is None:
            return await ctx.reply("Ugyldig tidsperiode")

        joined = []
        for member in ctx.guild.members:
            if member.joined_at > stamp:
                joined.append(member)

        discord_since = discord.utils.format_dt(stamp, style="f")

        if len(joined) == 0:
            return await ctx.reply(f"Ingen medlemmer har blitt med i siden {discord_since}")

        joined_string = f"Det har blitt med {len(joined)} medlemmer siden {discord_since}"

        embed = discord.Embed(color=ctx.me.color, description=joined_string)
        embed.set_author(name=f"Medlemmer som har blitt med siden {tid}")
        await ctx.reply(embed=embed)

    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.command(hidden=True)
    async def fysj(self, ctx):
        await ctx.send("https://imgur.com/BoNcn2Y")

    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.command(hidden=True)
    async def lei(self, ctx):
        await ctx.send("https://imgur.com/LDf6oLB")

    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.command(hidden=True)
    async def edb(self, ctx):
        await ctx.send("https://imgur.com/4QulGQs")

    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.command(hidden=True)
    async def morson(self, ctx):
        await ctx.send("https://imgur.com/PayXhjj")

    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.command(hidden=True, aliases=["slåned"])
    async def jada(self, ctx):
        await ctx.send("https://imgur.com/LDf6oLB")

    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.command(hidden=True, aliases=["sjalottlauk"])
    async def lom(self, ctx):
        await ctx.send("https://imgur.com/RN3a1AX")

    @tasks.loop(minutes=30)
    async def presence(self):
        """
        Endrer statusen til botten
        """

        if not self.bot.is_ready():
            return

        activity = choice(presencePool)
        self.bot.logger.debug(f"Changing presence {activity.get("name")}")

        await self.bot.change_presence(
            activity=discord.CustomActivity(
                name=activity.get("name").format(stars=self.bot.cache_overview["stars"]),
                emoji=activity.get("emoji", None)
            ),
            status=discord.Status.online
        )


async def setup(bot):
    # pylint: disable=missing-function-docstring
    await bot.add_cog(Misc(bot))
