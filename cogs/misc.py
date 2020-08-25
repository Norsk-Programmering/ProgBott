# Discord Packages
import discord
from discord import embeds
from discord.ext import commands

# Bot Utilities
from cogs.utils.Bot_version import bot_version
from cogs.utils.defaults import easy_embed

import operator
import platform
import time
from io import StringIO
from itertools import count
from operator import le
from re import sub
from urllib import parse


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo = "https://github.com/Roxedus/ProgBott"
        self.ico = "https://github.com/Norsk-Programmering/Profilering/raw/master/BotAvatar.gif"

    def get_uptime(self):
        now = time.time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        return days, hours, minutes, seconds

    @commands.command(name="ping", hidden=True)
    async def _ping(self, ctx):
        """
        Komando for ping
        """
        embed = easy_embed(self, ctx)
        embed.title = "Ping!"
        start = time.perf_counter()
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        duration = int((end - start) * 1000)
        edit = f"Pong!\nPing: {duration}ms | websocket: {int(self.bot.latency * 1000)}ms"
        embed.description = edit
        await message.edit(embed=embed)

    @commands.command(name="oppetid", aliases=["uptime"], hidden=True)
    async def _uptime(self, ctx):
        """
        Komando for oppetid
        """
        days, hours, minutes, seconds = self.get_uptime()
        await ctx.send(f"{days}d {hours}h {minutes}m {seconds}s")

    @commands.command(aliases=["farge"])
    async def syntax(self, ctx):
        """
        Guide på hvoran bruke kodeblokker
        """
        embed = easy_embed(self, ctx)
        embed.title = "Hvordan få vakre meldinger når man poster kode"
        embed.description = """
        Hei, du kan gjøre koden din mer leselig med å sende koden i kodeblokker.\n\n
        For vanlig kodeblokk skriv:\n\`\`\`\nconst dinKode = "Laget av meg"\nconsole.log(dinKode)\n\`\`\`\n
        Den kommer til å se ut som dette:\n```\nconst dinKode = "Laget av meg"\nconsole.log(dinKode)```\n
        Du kan også definere et språk, for å få syntax highlighting.\n
        For fargerik kodeblokk skriv:\n\`\`\`js\nconst dinKode = "Laget av meg"\nconsole.log(dinKode)\n\`\`\`\n
        Den kommer til å se ut som dette:\n```js\nconst dinKode = "Laget av meg"\nconsole.log(dinKode)```
        """  # noqa: W605
        await ctx.send(embed=embed)

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
        await ctx.send(embed=embed)

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

        guilds = len(self.bot.guilds)
        members = len(membercount)
        days, hours, minutes, seconds = self.get_uptime()

        uptimetext = f"{days}d {hours}t {minutes}m {seconds}s"
        embed = discord.Embed(color=discord.Colour.from_rgb(244, 1, 110), description=desc)
        embed.set_author(name=dev.name, icon_url=dev.avatar_url)
        embed.set_thumbnail(url=self.ico)

        embed.add_field(name="Tjenere", value=str(guilds))
        embed.add_field(name="Hvor mange?", value=f"{members} brukere")
        embed.add_field(name="Oppetid", value=uptimetext)
        embed.add_field(name="Hvordan?", value=how, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["regel3"])
    async def lmgtfy(self, ctx, *, søkeord: str):
        """
        Fordi noen trenger en internett 101 leksjon
        """

        url = "https://lmgtfy.com/?" + parse.urlencode({"q": søkeord})

        embed = discord.Embed(color=ctx.me.color, description=f"[Trykk her for løsningen på problemet ditt]({url})")
        embed.set_image(url="http://ecx.images-amazon.com/images/I/51IESUsBdbL._SX258_BO1,204,203,200_.jpg")
        await ctx.send(embed=embed)

    @commands.command()
    async def toproller(self, ctx, antall: int = None):
        roles = {}
        for role in ctx.guild.roles:
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
        embed.title = f"Viser top {counter} roller"
        embed.set_thumbnail(url=self.ico)

        await ctx.send(embed=embed)

    @commands.command(aliases=["guildinfo", "server", "serverinfo", "si", "gi"])
    async def guild(self, ctx):
        """
        Viser info om guilden
        """

        guild_created_date = ctx.guild.created_at.strftime("%d. %b. %Y - %H:%M")
        since_created_days = (ctx.message.created_at - ctx.guild.created_at).days

        if since_created_days == 1:
            since_created_days_string = "dag"
        else:
            since_created_days_string = "dager"

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
            boosters.append(f"{booster.name}#{booster.discriminator}")
        boosters = ", ".join(boosters)
        if len(boosters) > 1024:
            boosters = "For mange boosters for å vise her"
        if boosters == "":
            boosters = "**Ingen boosters**"

        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        categories = len(ctx.guild.categories)
        total_channels = text_channels + voice_channels

        flags = {
            "us": ":flag_us:",
            "eu": ":flag_eu:",
            "singapore": ":flag_sg:",
            "london": ":flag_gb:",
            "sydney": ":flag_au:",
            "amsterdam": ":flag_nl:",
            "frankfurt": ":flag_de:",
            "brazil": ":flag_br:",
            "dubai": ":flag_ae:",
            "japan": ":flag_jp:",
            "russia": ":flag_ru:",
            "southafrica": ":flag_za:",
            "hongkong": ":flag_hk:",
            "india": ":flag_in:"
        }
        region = str(ctx.guild.region)
        if region.startswith("us"):
            region = "us"
        elif region.startswith("eu"):
            region = "eu"
        elif region.startswith("amsterdam"):
            region = "amsterdam"
        try:
            flag = flags[region]
        except KeyError:
            flag = ":question:"

        region_names = {
            "eu-central": "Sentral-Europa",
            "eu-west": "Vest-Europa",
            "europe": "Europa",
            "hongkong": "Hong Kong",
            "russia": "Russland",
            "southafrica": "Sør-Afrika",
            "us-central": "Midt-USA",
            "us-east": "New Jersey",
            "us-south": "Sør-USA",
            "us-west": "California",
            "vip-amsterdam": "Amsterdam (VIP)",
            "vip-us-east": "Øst-USA (VIP)",
            "vip-us-west": "Vest-USA (VIP)",
        }
        try:
            region_name = region_names[str(ctx.guild.region)]
        except KeyError:
            region_name = str(ctx.guild.region).title()

        features_string = ""
        if ctx.guild.features is not []:
            features = {
                "VIP_REGIONS": "VIP",
                "VANITY_URL": "Egen URL",
                "INVITE_SPLASH": "Invitasjonsbilde",
                "VERIFIED": "Verifisert",
                "PARTNERED": "Discord Partner",
                "MORE_EMOJI": "Ekstra emoji",
                "DISCOVERABLE": "Fremhevet",
                "FEATURABLE": "Kan fremheves",
                "COMMERCE": "Butikkanaler",
                "PUBLIC": "Offentlig guild",
                "NEWS": "Nyhetskanaler",
                "BANNER": "Banner",
                "ANIMATED_ICON": "Animert ikon",
                "PUBLIC_DISABLED": "Ikke offentlig",
                "WELCOME_SCREEN_ENABLED": "Velkomstvindu"
            }
            for feature in ctx.guild.features:
                features_string += f"{features[feature]}\n"

        photos = {}
        if ctx.guild.splash_url:
            photos["Invitasjonsbilde"] = ctx.guild.splash_url_as(format="png")
        if ctx.guild.banner_url:
            photos["Banner"] = ctx.guild.banner_url_as(format="png")

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
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_thumbnail(url=ctx.guild.icon_url_as(static_format="png"))
        embed.add_field(name="ID", value=ctx.guild.id)
        embed.add_field(name="Eier", value=ctx.guild.owner.mention)
        embed.add_field(name="Region", value=f"{flag} {region_name}")
        embed.add_field(name="Opprettet", value=f"{guild_created_date}\n{since_created_days} " +
                                                f"{since_created_days_string} siden")
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
            embed.add_field(name=f"Boosters ({ctx.guild.premium_subscription_count})", value=boosters, inline=False)

        if features_string != "":
            embed.add_field(name="Tillegsfunksjoner", value=features_string)

        if photos != {}:
            photos_string = ""
            for key, value in photos.items():
                photos_string += f"[{key}]({value})\n"
            embed.add_field(name="Bilder", value=photos_string)
        await ctx.send(embed=embed)

    @commands.command(aliases=["serverroller", "guildroles", "serverroles"])
    async def guildroller(self, ctx):
        """
        Viser rollene i en guild
        """

        roles = []
        for role in ctx.guild.roles:
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
            await ctx.send(file=txt_file)

            file.close()

            return

        if roles == "":
            roles = "**Ingen roller**"

        embed = discord.Embed(color=ctx.me.color, description=roles)
        embed.set_author(name=f"Roller ({len(ctx.guild.roles) - 1})", icon_url=ctx.guild.icon_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

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

        bruker_joined_date = bruker.joined_at.strftime("%d. %b. %Y - %H:%M")
        bruker_created_date = bruker.created_at.strftime("%d. %b. %Y - %H:%M")
        since_joined_days = (ctx.message.created_at - bruker.joined_at).days
        since_created_days = (ctx.message.created_at - bruker.created_at).days
        if since_created_days == 1:
            since_created_days_string = "dag"
        else:
            since_created_days_string = "dager"
        if since_joined_days == 1:
            since_joined_days_string = "dag"
        else:
            since_joined_days_string = "dager"

        if bruker.premium_since:
            premium_since = bruker.premium_since.strftime("%d. %b. %Y - %H:%M")
            premium_since_days = (ctx.message.created_at - bruker.premium_since).days
            if since_joined_days == 1:
                premium_since_days_string = "dag"
            else:
                premium_since_days_string = "dager"

        roles = []
        for role in bruker.roles:
            if role.name != "@everyone":
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

        statuses = {
            "online": "<:online:743471541169291335> Pålogget",
            "idle": "<:idle:743471541127348255> Inaktiv",
            "dnd": "<:dnd:743471541093662840> Ikke forstyrr",
            "offline": "<:offline:743471543543136266> Frakoblet"
        }
        status = statuses[str(bruker.status)]

        embed = discord.Embed(color=color, description=f"{bruker.mention}\nID: {bruker.id}\n{status}\n{app}")
        if bruker.display_name == bruker.name:
            embed.set_author(name=f"{bruker.name}#{bruker.discriminator}", icon_url=bruker.avatar_url)
        else:
            embed.set_author(name=f"{bruker.name}#{bruker.discriminator} | {bruker.display_name}",
                             icon_url=bruker.avatar_url)
        embed.set_thumbnail(url=bruker.avatar_url_as(static_format="png"))
        embed.add_field(name="Opprettet", value=f"{bruker_created_date}\n{since_created_days} " +
                                                f"{since_created_days_string} siden")
        embed.add_field(name="Ble med i serveren", value=f"{bruker_joined_date}\n{since_joined_days} " +
                                                         f"{since_joined_days_string} siden")
        if bruker.premium_since:
            embed.add_field(name="Boost", value=f"{premium_since}\n{premium_since_days} " +
                                                f"{premium_since_days_string} siden\n" +
                                                f"Booster #{premium_index} av serveren", inline=False)
        embed.add_field(name=f"Roller ({len(bruker.roles) - 1})", value=roles, inline=False)
        embed.set_footer(text=f"#{join_index} Medlem av serveren | #{creation_index} Eldste brukeren på serveren")

        if bruker.activities:
            games = ""
            for activity in bruker.activities:
                if not activity.name:
                    continue
                games += f"{activity.name}\n"
            if games:
                embed.add_field(name="Spiller", value=games, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["userroles"])
    async def brukerroller(self, ctx, bruker: discord.Member = None):
        """
        Viser rollene til en bruker
        """

        if not bruker:
            bruker = ctx.author

        roles = []
        for role in bruker.roles:
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
        embed.set_author(name=f"Roller ({len(bruker.roles) - 1})", icon_url=bruker.avatar_url)
        embed.set_footer(text=f"{bruker.name}#{bruker.discriminator}", icon_url=bruker.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["roleinfo", "rolleinfo"])
    async def rolle(self, ctx, *, rolle: discord.Role):
        """
        Viser info om en rolle
        """

        if rolle.name == "@everyone":
            return await ctx.send("Skriv inn en annen rolle enn `@everyone`")

        if str(rolle.color) != "#000000":
            color = rolle.color
        else:
            color = discord.Colour(0x99AAB5)

        if rolle.mentionable:
            mentionable = "Ja"
        else:
            mentionable = "Nei"

        if rolle.hoist:
            hoisted = "Ja"
        else:
            hoisted = "Nei"

        rolle_created_date = rolle.created_at.strftime("%d. %b. %Y - %H:%M")
        since_created_days = (ctx.message.created_at - rolle.created_at).days

        if since_created_days == 1:
            since_created_days_string = "dag"
        else:
            since_created_days_string = "dager"

        members = []
        for member in rolle.members:
            members.append(f"{member.name}#{member.discriminator}")
        members = ", ".join(members)

        if len(members) > 1024:
            members = "For mange medlemmer for å vise her"
        if len(members) == 0:
            members = "**Ingen**"

        permissions = sub("\D", "", str(rolle.permissions))

        embed = discord.Embed(title=rolle.name, description=f"{rolle.mention}\n**ID:** {rolle.id}", color=color)
        embed.set_author(name=rolle.guild.name, icon_url=rolle.guild.icon_url)
        embed.add_field(name="Fargekode", value=str(rolle.color))
        embed.add_field(name="Opprettet", value=f"{rolle_created_date}\n{since_created_days} " +
                                                f"{since_created_days_string} siden")
        embed.add_field(name="Tillatelser", value=permissions)
        embed.add_field(name="Posisjon", value=rolle.position)
        embed.add_field(name="Nevnbar", value=mentionable)
        embed.add_field(name="Vises separat i medlemsliste", value=hoisted)
        embed.add_field(name=f"Brukere med rollen ({len(rolle.members)})", value=members, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
