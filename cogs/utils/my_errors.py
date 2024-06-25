# pylint: disable=missing-class-docstring,missing-module-docstring
# Discord Packages
from discord.ext.commands.errors import CommandError


class NoDM(CommandError):
    pass


class NoToken(Exception):
    pass


class NoWorplace(Exception):
    pass


class MultipleWorplaces(Exception):
    pass

class NoUnion(Exception):
    pass


class MultipleUnions(Exception):
    pass