"""
Hovedmodul for botten
"""
# pylint: disable=W0201
# pylint: disable=missing-function-docstring

# Discord Packages
import nextcord
from nextcord.ext import commands

# Bot Utilities
from cogs.utils.logging import Logger
from cogs.utils.settings import Settings

import time
import traceback
from argparse import ArgumentParser, RawTextHelpFormatter

Intents = nextcord.Intents().none()
Intents.guilds = True
Intents.members = True
Intents.emojis = True
Intents.presences = True
Intents.messages = True
Intents.guild_reactions = True
Intents.guild_typing = True

mentions = nextcord.AllowedMentions(
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
    """
    Hovedklasse for botten
    """

    def __init__(self):
        super().__init__(command_prefix=_get_prefix, intents=Intents, allowed_mentions=mentions)
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
        self.logger.info("Nextcord: %s", nextcord.__version__)
        self.logger.debug("Bot Ready;Prefixes: %s", ", ".join(settings.prefix))

        extensions = ["cogs.misc", "cogs.poeng", "cogs.bokmerker", "cogs.errors", "cogs.github", "cogs.broder"]
        for extension in extensions:
            try:
                self.logger.debug("Loading extension %s", extension)
                self.load_extension(extension)
            except Exception as _e:
                self.logger.exception("Loading of extension %s failed: %s", extension, _e)

    def run(self):
        # pylint: disable=arguments-differ
        try:
            super().run(settings.token)
        except Exception as _e:
            _tb = _e.__traceback__
            self.logger.error(traceback.extract_tb(_tb))
            print(_e)


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

    LEVEL = args.level
    data_dir = args.data_directory

    if args.debug:
        LEVEL = "DEBUG"

    settings = Settings(data_dir=data_dir, log_level=LEVEL, log_to_file=args.log_to_file)

    logger = Logger(location=settings.data_dir, level=settings.log_level, to_file=settings.log_to_file).logger
    logger.debug("Data folder: %s", settings.data_dir)

    Bot().run()
