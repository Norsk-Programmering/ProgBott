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

    def get_uptime(self):
        now = time.time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        return days, hours, minutes, seconds

    @commands.command(name='ping', hidden=True)
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
        edit = f'Pong!\nPing: {duration}ms | websocket: {int(self.bot.latency * 1000)}ms'
        embed.description = edit
        await message.edit(embed=embed)

    @commands.command(name='oppetid', aliases=["uptime"], hidden=True)
    async def _uptime(self, ctx):
        """
        Komando for oppetid
        """
        days, hours, minutes, seconds = self.get_uptime()
        await ctx.send(f'{days}d {hours}h {minutes}m {seconds}s')

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

    @commands.command(name='guilds')
    @commands.is_owner()
    async def _guilds(self, ctx):
        """
        Komando for å liste servere
        """
        embed = easy_embed(self, ctx)
        guilds = ""
        for guild in self.bot.guilds:
            guilds += f"{guild.name}\n"
        embed.description = f'```\n{guilds}\n```'
        embed.title = f'{self.bot.user.name} is in'
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
        how = f"**Python-versjon:** " \
              f"[{py_ver}](https://python.org/downloads/release/python-{py_ver.replace('.', '')}/)" \
              f"\n**Discord.py-versjon:** " \
              f"[{discord.__version__}](https://github.com/Rapptz/discord.py/releases/tag/v{discord.__version__}/)" \
              f"\n**ProgBott-versjon:** {bot_version}"

        guilds = len(self.bot.guilds)
        members = len(membercount)
        days, hours, minutes, seconds = self.get_uptime()
        avatar = self.bot.user.avatar_url_as(format=None, static_format='png', size=1024)

        uptimetext = f'{days}d {hours}t {minutes}m {seconds}s'
        embed = discord.Embed(color=discord.Colour.from_rgb(245, 151, 47), description=desc)
        embed.set_author(name=dev.name, icon_url=dev.avatar_url)
        embed.set_thumbnail(url=avatar)

        embed.add_field(name="Tjenere", value=str(guilds))
        embed.add_field(name="Hvor mange?", value=f'{members} brukere')
        embed.add_field(name="Oppetid", value=uptimetext)
        embed.add_field(name="Hvordan?", value=how, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['regel3'])
    async def lmgtfy(self, ctx, *, søkeord: str):
        """Fordi noen trenger en internett 101 leksjon"""

        url = 'https://lmgtfy.com/?' + parse.urlencode({'q': søkeord})

        embed = discord.Embed(color=ctx.me.color, description=f'[Trykk her for løsningen på problemet ditt]({url})')
        embed.set_image(url='http://ecx.images-amazon.com/images/I/51IESUsBdbL._SX258_BO1,204,203,200_.jpg')
        await ctx.send(embed=embed)

    @commands.command()
    async def toproller(self, ctx, antall: int = None):
        roles = {}
        for role in ctx.guild.roles:
            if role.name != '@everyone':
                roles[role.id] = len(role.members)

        roles = dict(sorted(roles.items(), key=operator.itemgetter(1), reverse=True))
        embed = easy_embed(self, ctx)
        desc = ""
        counter = 0
        _max = antall or 10
        for role, members in roles.items():
            desc += f'{ctx.guild.get_role(role).mention}: {members}\n'
            counter += 1
            if counter == _max:
                break

        embed.description = desc
        embed.title = f"Viser top {counter} roller"

        await ctx.send(embed=embed)

    @commands.command(aliases=['serverroller', 'guildroles', 'serverroles'])
    async def guildroller(self, ctx):
        """Viser rollene i en guild"""

        roles = []
        for role in ctx.guild.roles:
            if role.name != '@everyone':
                roles.append(role.name)
        if roles is []:
            roles = ['**Ingen Roller**']
        roles.reverse()
        roles = ', '.join(roles)

        roles = roles.replace(", --", "\n--")
        roles = roles.replace("--, ", "--\n")

        if len(roles) > 2048:
            file = StringIO(roles)

            txt_file = discord.File(file, "roller.txt")
            await ctx.send(file=txt_file)

            file.close()

            return

        if roles == '':
            roles = '**Ingen roller**'

        embed = discord.Embed(color=ctx.me.color, description=roles)
        embed.set_author(name=f'Roller ({len(ctx.guild.roles) - 1})', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['userinfo', 'ui', 'brukerinfo', 'user'])
    async def bruker(self, ctx, *, bruker: discord.Member = None):
        """Viser info om en bruker"""

        if not bruker:
            bruker = ctx.author

        app = ''
        if str(bruker.mobile_status) != 'offline':
            app += '📱 '
        if str(bruker.web_status) != 'offline':
            app += '🌐 '
        if str(bruker.desktop_status) != 'offline':
            app += '💻'

        join_index = sorted(ctx.guild.members, key=lambda m: m.joined_at).index(bruker) + 1
        creation_index = sorted(ctx.guild.members, key=lambda m: m.created_at).index(bruker) + 1
        if bruker.premium_since:
            premium_index = sorted(ctx.guild.premium_subscribers, key=lambda m: m.premium_since).index(bruker) + 1

        bruker_joined_date = bruker.joined_at.strftime('%d. %b. %Y - %H:%M')
        bruker_created_date = bruker.created_at.strftime('%d. %b. %Y - %H:%M')
        since_joined_days = (ctx.message.created_at - bruker.joined_at).days
        since_created_days = (ctx.message.created_at - bruker.created_at).days
        if since_created_days == 1:
            since_created_days_string = 'dag'
        else:
            since_created_days_string = 'dager'
        if since_joined_days == 1:
            since_joined_days_string = 'dag'
        else:
            since_joined_days_string = 'dager'

        if bruker.premium_since:
            premium_since = bruker.premium_since.strftime('%d. %b. %Y - %H:%M')
            premium_since_days = (ctx.message.created_at - bruker.premium_since).days
            if since_joined_days == 1:
                premium_since_days_string = 'dag'
            else:
                premium_since_days_string = 'dager'

        roles = []
        for role in bruker.roles:
            if role.name != '@everyone':
                roles.append(role.name)
        roles.reverse()
        roles = ', '.join(roles)

        if len(roles) > 1024:
            roles = f'Skriv `{self.bot.prefix}{ctx.command}` for å se rollene'
        if roles == '':
            roles = '**Ingen roller**'

        if str(bruker.color) != '#000000':
            color = bruker.color
        else:
            color = discord.Colour(0x99AAB5)

        statuses = {
            'online': '🟢 Pålogget',
            'idle': '🟡 Inaktiv',
            'dnd': '🔴 Ikke forstyrr',
            'offline': '⚫ Frakoblet'
        }
        status = statuses[str(bruker.status)]

        embed = discord.Embed(color=color, description=f'{bruker.mention}\nID: {bruker.id}\n{status}\n{app}')
        if bruker.display_name == bruker.name:
            embed.set_author(name=f'{bruker.name}#{bruker.discriminator}', icon_url=bruker.avatar_url)
        else:
            embed.set_author(name=f'{bruker.name}#{bruker.discriminator} | {bruker.display_name}',
                             icon_url=bruker.avatar_url)
        embed.set_thumbnail(url=bruker.avatar_url_as(static_format='png'))
        embed.add_field(name='Opprettet', value=f'{bruker_created_date}\n{since_created_days} ' +
                                                f'{since_created_days_string} siden')
        embed.add_field(name='Ble med i serveren', value=f'{bruker_joined_date}\n{since_joined_days} ' +
                                                         f'{since_joined_days_string} siden')
        if bruker.premium_since:
            embed.add_field(name='Boost', value=f'{premium_since}\n{premium_since_days} ' +
                                                f'{premium_since_days_string} siden\n' +
                                                f'Booster #{premium_index} av serveren', inline=False)
        embed.add_field(name=f'Roller ({len(bruker.roles) - 1})', value=roles, inline=False)
        embed.set_footer(text=f'#{join_index} Medlem av serveren | #{creation_index} Eldste brukeren på serveren')

        if bruker.activities:
            games = ''
            for activity in bruker.activities:
                if not activity.name:
                    continue
                games += f'{activity.name}\n'
            if games:
                embed.add_field(name='Spiller', value=games, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['userroles'])
    async def brukerroller(self, ctx, bruker: discord.Member = None):
        """Viser rollene til en bruker"""

        if not bruker:
            bruker = ctx.author

        roles = []
        for role in bruker.roles:
            if role.name != '@everyone':
                roles.append(role.name)
        roles.reverse()
        roles = ', '.join(roles)

        if len(roles) > 2048:
            file = StringIO(roles)

            txt_file = discord.File(file, "roller.txt")
            await ctx.send(file=txt_file)

            file.close()

            return

        if roles == '':
            roles = '**Ingen roller**'

        if str(bruker.color) != '#000000':
            color = bruker.color
        else:
            color = discord.Colour(0x99AAB5)

        embed = discord.Embed(color=color, description=roles)
        embed.set_author(name=f'Roller ({len(bruker.roles) - 1})', icon_url=bruker.avatar_url)
        embed.set_footer(text=f'{bruker.name}#{bruker.discriminator}', icon_url=bruker.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['roleinfo', 'rolleinfo'])
    async def rolle(self, ctx, *, rolle: discord.Role):
        """Viser info om en rolle"""

        if rolle.name == '@everyone':
            return await ctx.send('Skriv inn en annen rolle enn `@everyone`')

        if str(rolle.color) != '#000000':
            color = rolle.color
        else:
            color = discord.Colour(0x99AAB5)

        if rolle.mentionable:
            mentionable = 'Ja'
        else:
            mentionable = 'Nei'

        if rolle.hoist:
            hoisted = 'Ja'
        else:
            hoisted = 'Nei'

        rolle_created_date = rolle.created_at.strftime('%d. %b. %Y - %H:%M')
        since_created_days = (ctx.message.created_at - rolle.created_at).days

        if since_created_days == 1:
            since_created_days_string = 'dag'
        else:
            since_created_days_string = 'dager'

        members = []
        for member in rolle.members:
            members.append(f'{member.name}#{member.discriminator}')
        members = ', '.join(members)

        if len(members) > 1024:
            members = 'For mange medlemmer for å vise her'
        if len(members) == 0:
            members = '**Ingen**'

        permissions = sub('\D', '', str(rolle.permissions))

        embed = discord.Embed(title=rolle.name, description=f'{rolle.mention}\n**ID:** {rolle.id}', color=color)
        embed.set_author(name=rolle.guild.name, icon_url=rolle.guild.icon_url)
        embed.add_field(name='Fargekode', value=str(rolle.color))
        embed.add_field(name='Opprettet', value=f'{rolle_created_date}\n{since_created_days} ' +
                                                f'{since_created_days_string} siden')
        embed.add_field(name='Tillatelser', value=permissions)
        embed.add_field(name='Posisjon', value=rolle.position)
        embed.add_field(name='Nevnbar', value=mentionable)
        embed.add_field(name='Vises separat i medlemsliste', value=hoisted)
        embed.add_field(name=f'Brukere med rollen ({len(rolle.members)})', value=members, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
