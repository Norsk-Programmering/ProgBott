# Discord Packages
import discord
from discord.ext import commands

# Bot Utilities
from cogs.utils.logging import Logger
from cogs.utils.settings import Settings

from server import Server

import os
import time
import traceback
from argparse import ArgumentParser, RawTextHelpFormatter
import threading

import aiohttp


def _get_prefix(bot, message):
    if not message.guild:
        prefixes = settings.prefix
        return commands.when_mentioned_or(*prefixes)(bot, message)
    prefixes = settings.prefix
    return commands.when_mentioned_or(*prefixes)(bot, message)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_get_prefix)
        self.logger = logger
        self.logger.debug("Logging level: %s" % level.upper())
        self.data_dir = data_dir

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = time.time()
        if not hasattr(self, 'appinfo'):
            self.appinfo = await self.application_info()

        print(f'Logged in as: {self.user.name} in {len(self.guilds)} servers.')
        print(f'Version: {discord.__version__}')
        self.logger.debug("Bot Ready")

        extensions = ['cogs.misc', 'cogs.poeng', 'cogs.errors', 'cogs.github']
        for extension in extensions:
            try:
                self.logger.debug("Loading extension %s" % extension)
                self.load_extension(extension)
            except Exception:
                self.logger.exception("Loading of extension %s failed" % extension)

    def run(self):
        try:
            super().run(settings.token)
        except Exception as e:
            tb = e.__traceback__
            logger.error(traceback.extract_tb(tb))
            print(e)


if __name__ == '__main__':
    parser = ArgumentParser(prog="Roxedus' ProgBott",
                            description='Programmerings bot',
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-D", "--debug", action='store_true', help='Sets debug to true')
    parser.add_argument("-l", "--level", help='Sets debug level',
                        choices=["critical", "error", "warning", "info", "debug"], default="warning")
    parser.add_argument("-d", "--data-directory", help='Define an alternate data directory location', default="data")
    parser.add_argument("-f", "--log-to-file", action='store_true', help='Save log to file', default=True)

    args = parser.parse_args()

    level = args.level
    data_dir = args.data_directory

    if args.debug or os.environ.get('debug'):
        level = "debug"

    if args.data_directory:
        data_dir = str(args.data_directory)

    logger = Logger(location=data_dir, level=level, to_file=args.log_to_file).logger
    logger.debug("Data folder: %s" % data_dir)
    settings = Settings(data_dir=data_dir)

    server = threading.Thread(target=Server)
    server.start()

    Bot().run()
