#! python
# coding=utf-8


import json
import logging
import pickle
from typing import Optional, Union

import discord
from discord.ext import commands


BOT_PREFIX = '~'
DEFAULT_LANG = 'en_us'
DATA = 'data'
GAME_VERISON = '1.16'

CANNOT_READ = "Can't read data from '{}'"
FILE_NOT_FOUND = "File not found: '{}'"

LANG_LIST = ('ru_ru', 'en_us')

INTENTS = discord.Intents(messages=True, guilds=True, reactions=True, members=True, emojis=True)


class GlobalBallotData:
    pass


class PartyInvite:
    def __init__(self, *args):
        pass


class Party:
    def __init__(self, *args):
        pass


class EnchTest:
    pass


class Codenames:
    pass


class GuessCraft:
    pass


class GlobalData:
    def __init__(self):
        self.guilds: dict[int, GuildData] = {}
        self.users: dict[int, UserData] = {}
        self.ballots: GlobalBallotData = GlobalBallotData()
        self.stats: StatsData = StatsData()


class UserData:
    def __init__(self):
        self.lang: str = DEFAULT_LANG
        self.ballots: set[int] = set()
        self.reactions: UserReactions = UserReactions()
        self.stats: StatsData = StatsData()


class GuildData:
    def __init__(self):
        self.lang: str = DEFAULT_LANG
        self.home_ids: set[int] = set()
        self.school_ids: set[int] = set()
        self.members: dict[int, Union[BotMemberData, MemberData]] = {}
        self.stats: StatsData = StatsData()
        self.ballots: set[int] = set()


class BotMemberData:
    def __init__(self):
        self.reactions: UserReactions = UserReactions()
        self.stats: StatsData = StatsData()


class MemberData(BotMemberData):
    def __init__(self, guild_id, member_id):
        super().__init__()
        self.games: GamesData = GamesData()
        self.tests: TestsData = TestsData()
        self.invites: PartyInvite = PartyInvite(guild_id, member_id)
        self.party: Party = Party(guild_id, member_id)


class GamesData:
    def __init__(self):
        self.active: str = ''
        self.home_id: Optional[int] = None
        self.game: Union[GuessData, CodenamesData, None] = None
        self.players: set[int] = set()
        self.stats: StatsData = StatsData()

    def finish(self):
        self.active = ''
        self.home_id = None
        self.game = None
        self.players = set()


class TestsData:
    def __init__(self):
        self.active: str = ''
        self.school_id: Optional[int] = None
        self.test: Union[EnchTest, None] = None
        self.testers: set[int] = set()
        self.stats: StatsData = StatsData()

    def finish(self):
        self.active = ''
        self.school_id = None
        self.test = None
        self.testers = set()


class StatsData:
    def __init__(self):
        pass


class UserReactions:
    def __init__(self):
        self.reactions: list = []

    def set(self, reactions):
        self.reactions = reactions

    def __bool__(self):
        return bool(self.reactions)

    def __iter__(self):
        self.k = 0
        return self

    def __next__(self):
        if self.k != len(self.reactions):
            k = self.k
            self.k += 1
            return self.reactions[k]
        else:
            raise StopIteration


class GuessData:
    def __init__(self):
        self.guess: Optional[GuessCraft] = None
        self.stats: Optional[StatsData] = None


class CodenamesData:
    def __init__(self, codenames: Codenames, leader: bool, red: bool):
        self.codenames = codenames
        self.leader: bool = leader
        self.red: bool = red
        self.stats: Optional[StatsData] = None


class Loaders:

    @classmethod
    def set_logging(cls, *, debug: bool):
        if debug:
            log = logging.DEBUG
        else:
            log = logging.WARN

        logger = logging.getLogger('discord')
        logger.setLevel(log)
        handler = logging.FileHandler(filename='utils/discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)

    @classmethod
    def load_data(cls) -> GlobalData:
        try:
            with open(DATA, 'rb') as db:
                data = pickle.load(db)
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            print(CANNOT_READ.format(DATA))
            data = GlobalData()
        return data

    @classmethod
    def save_data(cls, data) -> None:
        try:
            with open(DATA, 'wb') as db:
                pickle.dump(data, db)
        except TypeError as error:
            print(error)

    @classmethod
    def read_file(cls, file_name: str) -> str:
        with open(file_name, 'r', encoding='UTF-8') as file:
            return file.read()

    @classmethod
    def load_json(cls, path: str) -> dict:
        try:
            with open(path + '.json', encoding='utf-8') as lang_file:
                return json.load(lang_file)
        except (FileNotFoundError, json.JSONDecodeError):
            raise ValueError(CANNOT_READ.format(f'langs/{path}.json'))

    @classmethod
    def load_lang(cls, name: str) -> dict:
        return Loaders.load_json('langs/' + name)

    @classmethod
    def load_ench_data(cls) -> dict:
        return Loaders.load_json('activities/ench/' + GAME_VERISON)

    @classmethod
    def load_guess_data(cls) -> dict:
        return Loaders.load_json('activities/guess/' + GAME_VERISON)

    @classmethod
    def load_langs(cls) -> dict:
        lang_dict = {}
        for elem in LANG_LIST:
            lang_dict[elem] = Loaders.load_lang(elem)
        return lang_dict


data = Loaders.load_data()
lang_dict = Loaders.load_langs()

guild_data_dict = GuildData().__dict__
member_data_dict = MemberData(0, 0).__dict__
bot_member_data_dict = BotMemberData().__dict__
user_data_dict = UserData().__dict__

ench_tests = list(lang_dict[DEFAULT_LANG]['ench']['questions'])

ench_test_data = Loaders.load_ench_data()

discord_emojis = Loaders.read_file('utils/emojis.txt').split()

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=INTENTS)
