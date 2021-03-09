#! python
# coding=utf-8


from typing import Optional, Union

import discord
from discord.ext import commands

from utils import *


BOT_PREFIX = '~'
DEFAULT_LANG = 'en_us'
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


data = Loaders.load_data()
lang_dict = Loaders.load_langs()

guild_data_dict = GuildData().__dict__
member_data_dict = MemberData(0, 0).__dict__
bot_member_data_dict = BotMemberData().__dict__
user_data_dict = UserData().__dict__

ench_tests = list(lang_dict[DEFAULT_LANG]['ench']['questions'])

discord_emojis = Loaders.read_file('utils/emojis.txt').split()

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=INTENTS)
