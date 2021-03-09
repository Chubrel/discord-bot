#! python
# coding=utf-8


from discord.ext import commands


class TranslationFail(commands.CommandError):

    def __init__(self, lang_name: str, lang_path: str):
        self.lang_name = lang_name
        self.lang_path = lang_path

    def __str__(self):
        return "Translation failed on a path <{}> with lang <{}>".format(self.lang_path, self.lang_name)


class PassCheckError(commands.CheckFailure):
    pass


class PassArgumentError(commands.BadArgument):
    pass


class RaiseError(commands.CommandError):
    pass


class NothingHere(commands.CommandNotFound):
    pass


class BadJSON(commands.BadArgument):
    pass


class BadPlaceholder(commands.BadArgument):
    pass


class DontUnderstand(commands.BadArgument):
    pass


class PlayersRepeat(commands.BadArgument):
    pass


class PlayerNotInParty(commands.BadArgument):
    pass


class BallotNotFound(commands.BadArgument):
    pass
