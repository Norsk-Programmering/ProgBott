# pylint: disable=missing-class-docstring,missing-module-docstring
# Discord Packages
from nextcord.ext.commands.errors import CommandError


class NoDM(CommandError):
    pass


class NoToken(Exception):
    pass
