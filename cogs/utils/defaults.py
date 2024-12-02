# Discord Packages
import discord

# Bot Utilities
from cogs.utils.my_errors import MultipleWorplaces, NoWorplace

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

# https://discord.com/developers/docs/resources/guild#guild-object-guild-features
features = {
    "ACTIVITY_FEED_DISABLED_BY_USER": "Aktivitetsfeed deaktivert",
    "ANIMATED_BANNER": "Annimert banner",
    "ANIMATED_ICON": "Animert ikon",
    "APPLICATION_COMMAND_PERMISSIONS_V2": "Moderne kommandopermisjoner",
    "AUTO_MODERATION": "Automatisk moderasjon",
    "BANNER": "Banner",
    "CHANNEL_BANNER": "Kannalbanner",
    "CHANNEL_ICON_EMOJIS_GENERATED": "Autogenererte kanal-emojis",
    "COMMERCE": "Butikkanaler",
    "COMMUNITY": "Sammfunsguild",
    "CREATOR_MONETIZABLE_PROVISIONAL": "Innholdskaper monetisering",
    "CREATOR_STORE_PAGE": "Innholdskaper butikk",
    "DEVELOPER_SUPPORT_SERVER": "Utviklerstøtteguild",
    "DISCOVERABLE": "Fremhevet",
    "ENABLED_DISCOVERABLE_BEFORE": False,
    "FEATURABLE": "Kan fremheves",
    "GUILD_WEB_PAGE_VANITY_URL": "Egen URL til nettsted",
    "INVITE_SPLASH": "Invitasjonsbilde",
    "INVITES_DISABLED": "Invitasjoner deaktivert",
    "MEMBER_PROFILES": "Medlemsprofiler",
    "MEMBER_VERIFICATION_GATE_ENABLED": "Medlemsverifisering",
    "MORE_EMOJI": "Ekstra emoji",
    "MORE_STICKERS": "Ekstra stickers",
    "NEW_THREAD_PERMISSIONS": "Nye tråder",
    "NEWS": "Nyhetskanaler",
    "PARTNERED": "Discord Partner",
    "PREVIEW_ENABLED": "Forhåndstesting",
    "PRIVATE_THREADS": "Private tråder",
    "PUBLIC_DISABLED": "Ikke offentlig",
    "PUBLIC": "Offentlig guild",
    "RAID_ALERTS_DISABLED": "Raidvarsler deaktivert",
    "ROLE_ICONS": "Rolleikoner",
    "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE": "Rolleabonnement til salgs",
    "ROLE_SUBSCRIPTIONS_ENABLED": "Rolleabonnement",
    "SEVEN_DAY_THREAD_ARCHIVE": "Ukeslang trådarkiv",
    "SOUNDBOARD": "Lydbrett",
    "TEXT_IN_VOICE_ENABLED": "Tekst i stemmekanaler",
    "THREADS_ENABLED": "Tåder",
    "THREE_DAY_THREAD_ARCHIVE": "Tredagers trådarkiv",
    "TICKETED_EVENTS_ENABLED": "Billettarrangementer",
    "VANITY_URL": "Egen URL",
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
    "active_developer": "<:active_developer:1115589805741457428>",
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
    "auto_moderation_configuration": "automatisk-moderasjon-konfigurasjon",
    "auto_moderation_execution": "automatisk-moderasjon-utførelse",
    "auto_moderation": "automatisk-moderasjon",
    "bans": "bans",
    "dm_messages": "dm-meldinger",
    "dm_polls": "dm-avstemninger",
    "dm_reactions": "dm-reaksjoner",
    "dm_typing": "dm-skrivestatus",
    "emojis_and_stickers": "emojis-og-stickers",
    "emojis": "emojis",
    "guild_messages": "guild-meldinger",
    "guild_reactions": "guild-reaksjoner",
    "guild_scheduled_events": "planlagte-server-hendelser",
    "guild_typing": "guild-skrivestatus",
    "guilds": "guilds",
    "integrations": "integrasjoner",
    "invites": "invitasjoner",
    "members": "medlemmer",
    "message_content": "meldingsinnhold",
    "messages": "meldinger",
    "moderation": "moderasjon",
    "polls": "avstemninger",
    "presences": "tilstedeværelse",
    "reactions": "reaksjoner",
    "scheduled_events": "planlagte-hendelser",
    "typing": "skrivestatus",
    "voice_states": "stemme-tilstander",
    "webhooks": "internettkroker"
}


def easy_embed(self, ctx, big_embed: bool = False) -> discord.Embed:
    """
    Hjelpefunksjon for universiell embed
    """

    avatar = self.bot.user.display_avatar.replace(static_format="png", size=1024).url
    embed = discord.Embed(colour=ctx.author.colour)
    embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
    if big_embed:
        embed.set_thumbnail(url=avatar)
    return embed


async def list_workplaces(guild: discord.Guild) -> dict:
    """
    Hjelpefunkjson for å liste alle registrerte bedrifter
    """
    return {int(x.id): x.name for x in guild.roles if x.name.endswith("-ansatt")}


async def get_workplace(user: discord.Member) -> int:
    """
    Hjelpefunkson for henting av brukers arbeidsplass
    """
    roles = [int(x.id) for x in user.roles if x.name.endswith("-ansatt")]
    if len(roles) == 1:
        return int(roles[0])
    elif len(roles) > 1:
        raise MultipleWorplaces("Multiple workplaces was found")
    elif len(roles) == 0:
        raise NoWorplace("No workplace was found")
    else:
        raise Exception("Unknown error while determining workplace")
