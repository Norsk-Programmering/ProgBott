# pylint: disable=W0201
# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.logging import Logger
from cogs.utils.settings import Settings

import time
import traceback
from argparse import ArgumentParser, RawTextHelpFormatter

intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.emojis = True
intents.presences = True
intents.messages = True
intents.guild_reactions = True
intents.guild_typing = True

mentions = discord.AllowedMentions(
    everyone=False,
    replied_user=False
)


def _get_prefix(bot, message):
    if not message.guild:
        prefixes = settings.prefix
        return commands.when_mentioned_or(*prefixes)(bot, message)
    prefixes = settings.prefix
    return commands.when_mentioned_or(*prefixes)(bot, message)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_get_prefix, intents=intents, allowed_mentions=mentions)
        self.logger = logger
        self.data_dir = data_dir
        self.settings = settings.extra

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

        extensions = ["cogs.misc", "cogs.poeng", "cogs.errors", "cogs.github", "cogs.broder"]
        for extension in extensions:
            try:
                self.logger.debug("Loading extension %s", extension)
                self.load_extension(extension)
            except Exception as e:
                self.logger.exception("Loading of extension %s failed: %s", extension, e)

    def run(self):
        try:
            super().run(settings.token)
        except Exception as e:
            tb = e.__traceback__
            self.logger.error(traceback.extract_tb(tb))
            print(e)


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

    level = args.level
    data_dir = args.data_directory

    if args.debug:
        level = "DEBUG"

    settings = Settings(data_dir=data_dir, log_level=level, log_to_file=args.log_to_file)

    logger = Logger(location=settings.data_dir, level=settings.log_level, to_file=settings.log_to_file).logger
    logger.debug("Data folder: %s", settings.data_dir)

    Bot().run()
