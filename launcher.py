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

import asyncio
import time
import traceback
from argparse import ArgumentParser, RawTextHelpFormatter

from aiohttp.client_exceptions import ClientConnectorDNSError
from aiohttp.connector import TCPConnector


def _get_prefix(bot, message):
    if not message.guild:
        prefixes = settings.prefix
        return commands.when_mentioned_or(*prefixes)(bot, message)
    prefixes = settings.prefix
    return commands.when_mentioned_or(*prefixes)(bot, message)


class RetryDNSConnector(TCPConnector):
    retry_count = 5
    retry_delay = 1
    retry_exponent = 1.5

    async def _create_direct_connection(self, *args, **kwargs):
        for retry in range(self.retry_count):
            try:
                return await super()._create_direct_connection(*args, **kwargs)
            except ClientConnectorDNSError as e:
                sleep_delay = (self.retry_delay + self.retry)**self.retry_exponent
                logger.warning("DNS error occurred: %s. Retrying in %.2f seconds (attempt %d/%d)",
                               e, sleep_delay, retry + 1, self.retry_count)
                await asyncio.sleep(sleep_delay)
                continue


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
        super().__init__(
            allowed_mentions=mentions,
            command_prefix=_get_prefix,
            connector=RetryDNSConnector(),
            intents=intents,
        )
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


async def main(token):

    discord.utils.setup_logging(root=False)

    async with Bot() as bot:
        await bot.start(token)

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
        asyncio.run(main(settings.token))
    except Exception as _e:
        _tb = _e.__traceback__
        logger.error(traceback.extract_tb(_tb))
        print(_e)
