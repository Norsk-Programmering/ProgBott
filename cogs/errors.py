# Discord Packages
from discord.ext import commands

import traceback


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        try:
            self.bot.get_command(f"{ctx.command}").reset_cooldown(ctx)
        except AttributeError:
            pass

        if hasattr(ctx.command, "on_error"):
            return

        ignored = (commands.CommandNotFound)
        send_help = (commands.MissingRequiredArgument,
                     commands.TooManyArguments,
                     commands.BadArgument)

        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, send_help):
            self.bot.get_command(f"{ctx.command}").reset_cooldown(ctx)
            return await ctx.send_help(ctx.command)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(f"`{ctx.command}` kan ikke brukes i DMs")
            except Exception:
                pass

        elif isinstance(error, commands.CheckFailure):
            return

        else:
            await ctx.send("En ukjent feil oppstod. Be båtteier om å sjekke feilen")
            tb = error.__traceback__
            traceback.print_tb(tb)
            print(error)
            self.bot.logger.error(f"Error running command: {ctx.command}\nError: {error}\nTraceback: {tb}")


def setup(bot):
    bot.add_cog(Errors(bot))
