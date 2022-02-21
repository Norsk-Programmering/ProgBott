# Discord Packages
import nextcord
from nextcord.ext import commands

# Bot Utilities
from cogs.utils.Bot_version import bot_version
from cogs.utils.defaults import easy_embed, features, flags, intents, region_names, statuses, userflags

import operator
import platform
import time
from io import StringIO
from os import listdir, name
from urllib import parse


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo = "https://github.com/Norsk-Programmering/ProgBott"
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
        days, hours, minutes, seconds = self.get_uptime()
        await ctx.reply(f"{days}d {hours}h {minutes}m {seconds}s")

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
              f"\n**Nextcord-versjon:** " \
              f"[{nextcord.__version__}](https://github.com/nextcord/nextcord/releases/tag/v{nextcord.__version__}/)" \
              f"\n**ProgBott-versjon:** {bot_version}"

        intents_list = []

        for intent, val in ctx.bot.intents:
            try:
                if intents[intent]:
                    intents_list.append(intents[intent])
            except KeyError:
                intents_list.append(intent)
                self.bot.logger.debug("feature %s is not translated", intent)

        guilds = len(self.bot.guilds)
        members = len(membercount)
        days, hours, minutes, seconds = self.get_uptime()

        uptimetext = f"{days}d {hours}t {minutes}m {seconds}s"
        embed = nextcord.Embed(color=nextcord.Colour.from_rgb(244, 1, 110), description=desc)
        embed.set_author(url=f"https://github.com/{dev.name}", name=dev.name, icon_url=dev.display_avatar.url)
        embed.set_thumbnail(url=self.ico)

        embed.add_field(name="Tjenere", value=str(guilds))
        embed.add_field(name="Hvor mange?", value=f"{members} brukere")
        embed.add_field(name="Oppetid", value=uptimetext)
        embed.add_field(name="Hvordan?", value=how, inline=False)

        if intents_list:
            embed.add_field(name="Mine Intensjoner:", value=", ".join(intents_list))

        await ctx.reply(embed=embed)

    @commands.command(aliases=["regel3"])
    async def lmgtfy(self, ctx, *, søkeord: str):
        """
        Fordi noen trenger en internett 101 leksjon
        """

        url = "https://lmgtfy.com/?" + parse.urlencode({"q": søkeord})

        embed = nextcord.Embed(color=ctx.me.color, description=f"[Trykk her for løsningen på problemet ditt]({url})")
        embed.set_image(url="http://ecx.images-amazon.com/images/I/51IESUsBdbL._SX258_BO1,204,203,200_.jpg")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["pullrequest", "draforespørsel"], hidden=True)
    async def pr(self, ctx):
        """
        Pwease appwove my puww wequest senpai ^_^ uwu
        """

        await ctx.reply("https://youtu.be/5xooMXyleXM")

    @commands.command(aliases=["topproller"])
    async def toproller(self, ctx, antall: int = None):

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

        try:
            region_name = region_names[str(ctx.guild.region)]
        except KeyError:
            region_name = str(ctx.guild.region).title()

        features_string = ""
        if ctx.guild.features is not []:
            for feature in ctx.guild.features:
                try:
                    if features[feature]:
                        features_string += f"{features[feature]}\n"
                except KeyError:
                    self.bot.logger.debug("feature %s is not translated", feature)
                    features_string += f"{feature}\n"

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

        embed = nextcord.Embed(color=ctx.me.color, description=f"**Verifiseringskrav:** {verification}\n" +
                               f"**Innholdsfilter:** {content}\n" +
                               f"**Boost Tier:** {ctx.guild.premium_tier}\n" +
                               f"**Emoji:** {len(ctx.guild.emojis)}")
        embed.set_author(name=ctx.guild.name)
        if ctx.guild.icon is not None:
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.set_thumbnail(url=ctx.guild.icon.replace(static_format="png").url)
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
            embed.add_field(name=f"Boosts ({ctx.guild.premium_subscription_count})", value=boosters, inline=False)

        if features_string != "":
            embed.add_field(name="Tillegsfunksjoner", value=features_string)

        if photos != {}:
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

            txt_file = nextcord.File(file, "roller.txt")
            await ctx.reply(file=txt_file)

            file.close()

            return

        if roles == "":
            roles = "**Ingen roller**"

        embed = nextcord.Embed(color=ctx.me.color, description=roles)
        embed.set_author(name=f"Roller ({len(ctx.guild.roles) - 1})")
        embed.set_footer(text=ctx.guild.name)
        if ctx.guild.icon is not None:
            embed.set_author(name=f"Roller ({len(ctx.guild.roles) - 1})", icon_url=ctx.guild.icon.url)
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["userinfo", "ui", "brukerinfo", "user"])
    async def bruker(self, ctx, *, bruker: nextcord.Member = None):
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
            color = nextcord.Colour(0x99AAB5)

        status = statuses[str(bruker.status)]

        embed = nextcord.Embed(color=color)
        if bruker.public_flags.all():
            embed.description = f"{bruker.mention}\nID: {bruker.id}\n{status}\n{app} \
                {' '.join(userflags[m] for m, v in bruker.public_flags.all() if m in userflags)}"
        else:
            embed.description = f"{bruker.mention}\nID: {bruker.id}\n{status}\n{app}"
        if bruker.display_name == bruker.name:
            embed.set_author(name=f"{bruker.name}#{bruker.discriminator}", icon_url=bruker.display_avatar.url)
        else:
            embed.set_author(name=f"{bruker.name}#{bruker.discriminator} | {bruker.display_name}",
                             icon_url=bruker.display_avatar.url)
        embed.set_thumbnail(url=bruker.display_avatar.replace(static_format="png").url)
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
        await ctx.reply(embed=embed)

    @commands.command(aliases=["userroles"])
    async def brukerroller(self, ctx, bruker: nextcord.Member = None):
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

            txt_file = nextcord.File(file, "roller.txt")
            await ctx.send(file=txt_file)

            file.close()

            return

        if roles == "":
            roles = "**Ingen roller**"

        if str(bruker.color) != "#000000":
            color = bruker.color
        else:
            color = nextcord.Colour(0x99AAB5)

        embed = nextcord.Embed(color=color, description=roles)
        embed.set_author(name=f"Roller ({len(bruker.roles) - 1})")
        embed.set_footer(text=f"{bruker.name}#{bruker.discriminator}")
        if ctx.guild.icon is not None:
            embed.set_author(name=f"Roller ({len(bruker.roles) - 1})", icon_url=bruker.display_avatar.url)
            embed.set_footer(text=f"{bruker.name}#{bruker.discriminator}", icon_url=bruker.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["roleinfo", "rolleinfo"])
    async def rolle(self, ctx, *, rolle: nextcord.Role):
        """
        Viser info om en rolle
        """

        if rolle.name == "@everyone":
            return await ctx.reply("Skriv inn en annen rolle enn `@everyone`")

        if str(rolle.color) != "#000000":
            color = rolle.color
        else:
            color = nextcord.Colour(0x99AAB5)

        hoisted = "Nei"
        mentionable = "Nei"

        if rolle.hoist:
            hoisted = "Ja"
        if rolle.mentionable:
            mentionable = "Ja"

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

        permissions = ", ".join([permission for permission, value in iter(rolle.permissions) if value is True])

        embed = nextcord.Embed(title=rolle.name, description=f"{rolle.mention}\n**ID:** {rolle.id}", color=color)
        embed.set_author(name=rolle.guild.name)
        if ctx.guild.icon is not None:
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.add_field(name="Fargekode", value=str(rolle.color))
        embed.add_field(name="Opprettet", value=f"{rolle_created_date}\n{since_created_days} " +
                                                f"{since_created_days_string} siden")
        embed.add_field(name="Posisjon", value=rolle.position)
        embed.add_field(name="Nevnbar", value=mentionable)
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

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(hidden=True)
    async def reload(self, ctx, cog):
        """Laster inn spesifisert cog på nytt"""

        cogs = [file[:-3] for file in listdir('cogs') if file.endswith('.py')]
        name_ = cog if cog in cogs else None
        if not name:
            return await ctx.reply(f"{cog} was not found")

        try:
            self.bot.reload_extension(f'cogs.{name_}')
            await ctx.reply(f"{name_} was reloaded")
            self.bot.logger.debug("%s was reloaded", name_)
        except commands.ExtensionNotLoaded:
            return await ctx.reply(f"{name_} was not loaded")


def setup(bot):
    bot.add_cog(Misc(bot))
