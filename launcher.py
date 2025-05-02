"""
Hovedmodul for botten
"""
# pylint: disable=W0201
# pylint: disable=missing-function-docstring

# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.logger import Logger
from cogs.utils.settings import Settings

import time
import traceback
from argparse import ArgumentParser, RawTextHelpFormatter


def _get_prefix(bot, message):
    if not message.guild:
        prefixes = settings.prefix
        return commands.when_mentioned_or(*prefixes)(bot, message)
    prefixes = settings.prefix
    return commands.when_mentioned_or(*prefixes)(bot, message)


class Bot(commands.Bot):
    """
    Hovedklasse for botten
    """

    def __init__(self):
        intents = discord.Intents(
            emojis=True,
            guild_reactions=True,
            guild_typing=True,
            guilds=True,
            members=True,
            messages=True,
            message_content=True,
            presences=True
        )
        mentions = discord.AllowedMentions(
            everyone=False,
            replied_user=False
        )
        super().__init__(command_prefix=_get_prefix, intents=intents, allowed_mentions=mentions)
        self.logger = logger
        self.data_dir = data_dir
        self.settings = settings.extra
        self.cache_overview = {"stars": 0}

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = time.time()
        if not hasattr(self, "appinfo"):
            self.appinfo = await self.application_info()

        self.logger.info("Logged in as: %s in %s servers.", self.user.name, len(self.guilds))
        self.logger.info("DiscordPY: %s", discord.__version__)
        self.logger.debug("Bot Ready;Prefixes: %s", ", ".join(settings.prefix))

    async def setup_hook(self):
        extensions = ["cogs.norprog", "cogs.misc", "cogs.poeng", "cogs.bokmerker",
                      "cogs.errors", "cogs.github", "cogs.broder", "cogs.workplace"]
        for extension in extensions:
            try:
                self.logger.debug("Loading extension %s", extension)
                await self.load_extension(extension)
            except Exception as _e:
                self.logger.exception("Loading of extension %s failed: %s", extension, _e)

    async def close(self):
        self.logger.info("Logging out")
        await super().close()


if __name__ == "__main__":
    parser = ArgumentParser(prog="Roxedus' ProgBott",
                            description="Programmeringsbot for Norsk programmering",
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-D", "--debug", action="store_true", help="Sets debug to true")
    parser.add_argument("-l", "--level", help="Sets debug level",
                        choices=["critical", "error", "warning", "info", "debug"], default="warning")
    parser.add_argument("-d", "--data-directory",
                        help="Define an alternate data directory location", default="data", type=str)
    parser.add_argument("-f", "--log-to-file", action="store_true", help="Save log to file", default=True)

    args = parser.parse_args()

    LEVEL = args.level.upper()
    data_dir = args.data_directory

    if args.debug:
        LEVEL = "DEBUG"

    settings = Settings(data_dir=data_dir, log_level=LEVEL, log_to_file=args.log_to_file)

    logger = Logger(location=settings.data_dir, level=settings.log_level, to_file=settings.log_to_file).logger
    logger.debug("Data folder: %s", settings.data_dir)

    # pylint: disable=arguments-differ
    try:
        Bot().run(settings.token)
    except Exception as _e:
        _tb = _e.__traceback__
        logger.error(traceback.extract_tb(_tb))
        print(_e)
