# Discord Packages
import nextcord

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
    "Deprecated": "Utfaset",
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
    "ANIMATED_BANNER": "Annimert banner",
    "ANIMATED_ICON": "Animert ikon",
    "BANNER": "Banner",
    "CHANNEL_BANNER": "Kannalbanner",
    "COMMERCE": "Butikkanaler",
    "COMMUNITY": "Sammfunsguild",
    "DISCOVERABLE": "Fremhevet",
    "ENABLED_DISCOVERABLE_BEFORE": False,
    "FEATURABLE": "Kan fremheves",
    "INVITE_SPLASH": "Invitasjonsbilde",
    "MEMBER_PROFILES": "Medlemsprofiler",
    "MORE_EMOJI": "Ekstra emoji",
    "NEW_THREAD_PERMISSIONS": "Nye tråder",
    "NEWS": "Nyhetskanaler",
    "PARTNERED": "Discord Partner",
    "PRIVATE_THREADS": "Private tråder",
    "PUBLIC_DISABLED": "Ikke offentlig",
    "PUBLIC": "Offentlig guild",
    "ROLE_ICONS": "Rolle ikoner",
    "SEVEN_DAY_THREAD_ARCHIVE": "Ukeslang trådarkiv",
    "THREADS_ENABLED": "Tåder",
    "THREE_DAY_THREAD_ARCHIVE": "Tredagers trådarkiv",
    "VANITY_URL": "Egen URL",
    "PREVIEW_ENABLED": "Forhåndstesting",
    "VERIFIED": "Verifisert",
    "VIP_REGIONS": "VIP",
    "WELCOME_SCREEN_ENABLED": "Velkomstvindu"
}

statuses = {
    "online": "<:online:743471541169291335> Pålogget",
    "idle": "<:idle:743471541127348255> Inaktiv",
    "dnd": "<:dnd:743471541093662840> Ikke forstyrr",
    "offline": "<:offline:743471543543136266> Frakoblet"
}

userflags = {
    "boost": "<:boost:791038860825198672>",
    "bug_hunter_level_2": "<:bug_hunter_level_2:791038860887851038>",
    "bug_hunter": "<:bug_hunter:791038860984713317>",
    "early_supporter": "<:early_supporter:791038860606832701>",
    "early_verified_bot_developer": "<:early_verified_bot_developer:791038860884836383>",
    "hypesquad_balance": "<:hypesquad_balance:791038861018398720>",
    "hypesquad_bravery": "<:hypesquad_bravery:791038860889030747>",
    "hypesquad_brilliance": "<:hypesquad_brilliance:791038860892700702>",
    "hypesquad": "<:hypesquad:791038860817596427>",
    "partner": "<:partner:791038861114736681>",
    "staff": "<:staff:791038860787712031>",
    "verified_bot_developer": "<:early_verified_bot_developer:791038860884836383>"
}

intents = {
    "bans": "bans",
    "dm_messages": "dm-meldinger",
    "dm_reactions": "dm-reaksjoner",
    "dm_typing": "dm-skrivestatus",
    "emojis": "emojis",
    "guild_messages": "guild-meldinger",
    "guild_reactions": "guild-reaksjoner",
    "guild_typing": "guild-skrivestatus",
    "guilds": "guilds",
    "integrations": "integrasjoner",
    "invites": "invitasjoner",
    "members": "medlemmer",
    "messages": "meldinger",
    "presences": "tilstedeværelse",
    "reactions": "reaksjoner",
    "scheduled_events": "planlagte-hendelser",
    "typing": "skrivestatus",
    "voice_states": "stemme-tilstander",
    "webhooks": "internettkroker"
}


def easy_embed(self, ctx, big_embed: bool = False):
    """
    Hjelpefunksjon for universiell embed
    """

    avatar = self.bot.user.display_avatar.replace(static_format="png", size=1024).url
    embed = nextcord.Embed(colour=ctx.author.colour)
    embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
    if big_embed:
        embed.set_thumbnail(url=avatar)
    return embed
