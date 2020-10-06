# Discord Packages
import discord

booler = {
    True: ":white_check_mark:",
    False: ":x:"
}

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

features = {
    "VIP_REGIONS": "VIP",
    "VANITY_URL": "Egen URL",
    "INVITE_SPLASH": "Invitasjonsbilde",
    "VERIFIED": "Verifisert",
    "PARTNERED": "Discord Partner",
    "MORE_EMOJI": "Ekstra emoji",
    "DISCOVERABLE": "Fremhevet",
    "FEATURABLE": "Kan fremheves",
    "COMMUNITY": "Sammfunsguild",
    "COMMERCE": "Butikkanaler",
    "PUBLIC": "Offentlig guild",
    "NEWS": "Nyhetskanaler",
    "BANNER": "Banner",
    "ANIMATED_ICON": "Animert ikon",
    "PUBLIC_DISABLED": "Ikke offentlig",
    "WELCOME_SCREEN_ENABLED": "Velkomstvindu"
}

statuses = {
    "online": "<:online:743471541169291335> Pålogget",
    "idle": "<:idle:743471541127348255> Inaktiv",
    "dnd": "<:dnd:743471541093662840> Ikke forstyrr",
    "offline": "<:offline:743471543543136266> Frakoblet"
}

intents = {
    "guilds": "guilds",
    "members": "medlemmer",
    "bans": "bans",
    "emojis": "emojis",
    "integrations": "integrasjoner",
    "webhooks": "internettkroker",
    "invites": "invitasjoner",
    "voice_states": "stemme-tilstander",
    "presences": "tilstedeværelse",
    "messages": "meldinger",
    "guild_messages": "guild-meldinger",
    "dm_messages": "dm-meldinger",
    "reactions": "reaksjoner",
    "guild_reactions": "guild-reaksjoner",
    "dm_reactions": "dm-reaksjoner",
    "typing": "skrivestatus",
    "guild_typing": "guild-skrivestatus",
    "dm_typing": "dm-skrivestatus"
}


def easy_embed(self, ctx, big_embed: bool = False):
    avatar = self.bot.user.avatar_url_as(format=None, static_format="png", size=1024)
    embed = discord.Embed(colour=ctx.author.colour)
    embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url)
    if big_embed:
        embed.set_thumbnail(url=avatar)
    return embed
