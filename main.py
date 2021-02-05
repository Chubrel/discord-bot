#! python
# coding=utf-8
"""Chubaka bot"""

import logging
import pickle
import json
import re
from string import Template
from random import choice, sample, randrange, shuffle
from typing import Optional, Union
from datetime import datetime, timedelta

import discord
from discord.ext import commands


# ⛔🚫🛑💯❓❗

DEBUG = True

if DEBUG:
    log = logging.DEBUG
else:
    log = logging.WARN

INTENTS = discord.Intents(messages=True, guilds=True, reactions=True, members=True, emojis=True)

DATA = 'data'
DEFAULT_LANG = 'en_us'
ENCH_TEST_MAX_QUESTIONS_COUNT = 10
BOT_PREFIX = '~'
GAME_VERISON = '1.16'
MAX_STATS_LINE_LENGTH = 12
PARTY_LIFETIME = 3600
_MY_GUILD = 671035889174183941

TRANSLATION_FAILED = "Translation failed on a path {} with lang '{}'"
FILE_NOT_FOUND = "File not found: '{}'"
NO_SUBCOMMAND = 'No subcommand'
CANNOT_READ = "Can't read data from '{}'"
NO_SUCH_ACTIVITY = "Activity is neither 'game' nor 'test'"
NO_SUCH_QUESTION_TYPE = "No such question type '{}'"

msgs = {'hello': 'Дратути!'}

imgs = {'bedy': 'https://cdn.discordapp.com/attachments/800634568356134922/803033539468722206/bedy_s_bashkoj.jpg',
        'analiz': 'https://cdn.discordapp.com/attachments/800634568356134922/800647085904363520/analiz.jpg',
        'ptz': 'https://cdn.discordapp.com/attachments/800634568356134922/800647084180635658/844b6ce22b591e73.jpg',
        'hochesh': 'https://cdn.discordapp.com/attachments/800634568356134922/800647119316189254/chto_hoshesh.jpg',
        'svyaz': 'https://cdn.discordapp.com/attachments/800634568356134922/800647129663799315/do_svyazi.jpg',
        'dlya': 'https://cdn.discordapp.com/attachments/800634568356134922/800647134567071825/eto_dlya_nas.jpg',
        'birth': 'https://cdn.discordapp.com/attachments/800634568356134922/800647144121696276/happy_birthday.jpg',
        'drugoe': 'https://cdn.discordapp.com/attachments/800634568356134922/800647139428007948/eto_drugoe.jpg',
        'micro': 'https://cdn.discordapp.com/attachments/800634568356134922/800647148101435412/k_mikro.jpg',
        'clown': 'https://cdn.discordapp.com/attachments/800634568356134922/800647153377869914/kloun.jpg',
        'minecraft': 'https://cdn.discordapp.com/attachments/800634568356134922/800647156553089054/minecraft.jpg',
        'hunej': 'https://cdn.discordapp.com/attachments/800634568356134922/800647072923123732/ne_polzueshsya.jpg',
        'kacheli': 'https://cdn.discordapp.com/attachments/800634568356134922/800647074429272064/ogo_kacheli.jpg',
        'pisez': 'https://cdn.discordapp.com/attachments/800634568356134922/800647076462460928/pisec.jpg',
        'gde': 'https://cdn.discordapp.com/attachments/800634568356134922/800647081311993876/Z3wmbx0MNpk.jpg',
        'sizhu': 'https://cdn.discordapp.com/attachments/800634568356134922/800647078752550933/sizhu_ahuel.jpg',
        'trezv': 'https://cdn.discordapp.com/attachments/800634568356134922/800647079277625404/ty_trezvyj.jpg',
        'zagruzka': 'https://cdn.discordapp.com/attachments/800634568356134922/800647083232460841/zagruzka.jpg',
        'zasho': 'https://cdn.discordapp.com/attachments/800634568356134922/800647086135705620/za_sho_mne_eto.jpg',
        'house': 'https://cdn.discordapp.com/attachments/802531716085973003/803010693912985630/unknown.png'}

phrase_codes = {'INVITED': 'invited', 'INVITED_BUT_IN_PARTY': 'invited_but_in_party', 'JOINED': 'joined_in_party',
                'INVITED_ALREADY': 'already_invited', 'NO_INVITES': 'no_invites', 'IN_YOUR_PARTY': 'in_your_party',
                'UNCERTAIN': 'ambiguous_invites', 'NO_INVITE_FROM': 'no_invites_from', 'DISBANDED': 'party_disbanded',
                'IN_PARTY': 'in_party', 'LEADER_ALREADY': 'already_leader', 'KICKED': 'kicked_from_party',
                'NEW_LEADER_SET': 'new_leader_set', 'NOT_IN_PARTY': 'not_in_party', 'NOT_MEMBER': 'not_member',
                'LEFT': 'left_from_party'}

snds = {'blya': 'blyat_chto.ogg', 'izv': 'izvinite.ogg', 'bat': 'batyushki.ogg', 'uzh': 'uzhas.ogg',
        'nah': 'poshyol_nahuj.ogg', 'logo': 'bananana.ogg', 'logo1': 'banananana.ogg'}

reactions = ({'look': '👀', 'up': '👍', 'down': '👎', 'check': '✅', 'cross': '❌', 'think': '🤔', 'question': '❔',
              'info': 'ℹ️', 'ok': '🆗', 'speak': '💬', 'warn': '⚠️', '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣',
              '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣', '10': '🔟', 'bs': '🟦'},
             {'vote': ('up', 'down'), 'ivote': ('check', 'cross'), 'blue_square': ('bs',)},
             ('numvote',),
             ('word',))

REACTION_LETTER = ord('🇦') - ord('a')

games = ('codenames',)  # ('guess', 'numb', 'b&c', 'stones')
tests = ('ench',)

game_codes = {'CODENAMES': 'Codenames', 'GUESS': 'GuessCraft'}

test_codes = {'ENCH': 'Enchantment'}

lang_list = ('ru_ru', 'en_us')
stats_line_emojis = ['line_small', 'line_left', 'line_middle', 'line_right']

question_numbers = ('1️⃣', '2️⃣', '3️⃣')
test_options_number = len(question_numbers)
question_changers = ('⬅️', '➡️')


def set_logging(log_type):
    logger = logging.getLogger('discord')
    logger.setLevel(log_type)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def init_guild(guild_id: int) -> None:
    global data, guild_data_dict
    guild = data.guilds.get(guild_id)
    if guild is None:
        data.guilds[guild_id] = GuildData()
    else:
        guild_dict = guild.__dict__
        if guild_dict != guild_data_dict:
            guild.__dict__ = guild_data_dict | guild_dict
            data.guilds[guild_id] = guild


def init_member(guild_id: int, member_id: int) -> None:
    global data, member_data_dict
    guild_members = data.guilds[guild_id].members
    member_data = guild_members.get(member_id)
    if member_data is None:
        guild_members[member_id] = MemberData(guild_id, member_id)
    else:
        member_dict = member_data.__dict__
        if member_dict != member_data_dict:
            member_data.__dict__ = member_data_dict | member_dict
            guild_members[member_id] = member_data


def count_games(guild_id: int) -> int:
    global data
    count = 0
    for member_data in data.guilds[guild_id].members.values():
        count += bool(member_data.games.active)
    return count


def count_tests(guild_id: int) -> int:
    global data
    count = 0
    for member_data in data.guilds[guild_id].members.values():
        count += bool(member_data.tests.active)
    return count


def abort_games(guild_id: int) -> None:
    global data
    member_data = data.guilds[guild_id].members
    for member_id in member_data:
        member_data[member_id].games.game = None
        member_data[member_id].games.active = ''


def abort_tests(guild_id: int) -> None:
    global data
    member_data = data.guilds[guild_id].members
    for member_id in member_data:
        member_data[member_id].tests.test = None
        member_data[member_id].tests.active = ''


def get_options(path: tuple) -> list:
    global lang_dict
    opt = lang_dict[DEFAULT_LANG]
    for el in path:
        opt = opt[el]
    return list(opt.keys())


def lang(guild_id: int):
    global data
    return data.guilds[guild_id].lang


'''
def my_strip(string: str) -> dict:
    d = {}
    directory = []
    key = True
    plain_text = False
    plain_text_char = '"'
    s = ''
    i = 0
    while i < len(string):
        if plain_text:
            if string[i] == plain_text_char:
                plain_text = False
                if directory :
                    pass
            elif string[i] == '\\':
                if string[i + 1] in '\\"\'':
                    s += string[i + 1]
                    i += 1
                elif string[i + 1] == 'n':
                    s += '\n'
                    i += 1
                else:
                    s += string[i]
            else:
                s += string[i]
        elif string[i] in ' ":=()\\':
            if string[i] in '"\'':
                plain_text = True
                plain_text_char = string[i]
        else:
            s += string[i]
        i += 1

    return d


def inner_dict(d: dict, directory: list[int]):
    pass
'''


def inner_list(list_: list[list]) -> list:
    while len(list_) != 0:
        list_ = list_[-1]
    return list_


def translate(lang_name: str, lang_path: tuple, replace_dict: dict = None, rand: bool = False) -> str:
    global lang_dict, data
    phrase = lang_dict[lang_name]
    try:
        for el in lang_path:
            phrase = phrase[el]
    except KeyError:
        raise KeyError(TRANSLATION_FAILED.format(lang_path, lang_name))
    if rand:
        phrase = choice(phrase)
    if replace_dict is not None:
        phrase = Template(phrase).safe_substitute(replace_dict)
    return phrase.replace('\\n', '\n')


def get_stats_line(length: int) -> str:
    global bot, stats_line_emojis
    if length == 1:
        line = str(stats_line_emojis[0])
    else:
        line = str(stats_line_emojis[1]) + (length - 2) * str(stats_line_emojis[2]) + str(stats_line_emojis[3])
    return line


def get_propotional_lines(*weights) -> list:
    total = sum(weights)
    if total != 0:
        lines = []
        for i in weights:
            lines.append(get_stats_line(int(MAX_STATS_LINE_LENGTH * i / total - 0.001) + 1))
        return lines


async def get_stats_line_emojis(guild) -> None:
    global stats_line_emojis
    emojis = await guild.fetch_emojis()
    for i in range(len(stats_line_emojis)):
        for e in emojis:
            if stats_line_emojis[i] == e.name:
                stats_line_emojis[i] = e


async def fill_reactions(message: discord.Message, reactions: iter) -> None:
    await message.clear_reactions()
    for reaction in reactions:
        await message.add_reaction(reaction)


def numvote_list(number: int) -> list:
    global reactions
    if number > 10:
        number = 10
    elif number < 1:
        return []
    return [reactions[0][str(i)] for i in range(1, int(number) + 1)]


def get_home(guild_id: int, member_id: int) -> discord.TextChannel:
    global bot, data
    guild = bot.get_guild(guild_id)
    return guild.get_channel(data.guilds[guild_id].members[member_id].games.home_id)


def get_school(guild_id: int, member_id: int) -> discord.TextChannel:
    global bot, data
    guild = bot.get_guild(guild_id)
    return guild.get_channel(data.guilds[guild_id].members[member_id].tests.school_id)


def get_member(guild_id: int, member_id: int) -> discord.Member:
    global bot
    guild = bot.get_guild(guild_id)
    return guild.get_member(member_id)


async def get_school_message(guild_id: int, member_id: int, message_id: int) -> discord.Message:
    school = get_school(guild_id, member_id)
    return await school.fetch_message(message_id)


async def get_home_message(guild_id: int, member_id: int, message_id: int) -> discord.Message:
    home = get_home(guild_id, member_id)
    return await home.fetch_message(message_id)


async def get_message(*args) -> discord.Message:
    global bot
    if len(args) == 3:
        guild = bot.get_guild(args[0])
        channel = guild.get_channel(args[1])
    else:
        channel = bot.get_channel(args[0])
    return await channel.fetch_message(args[-1])


def get_path_from_message_link(link: str) -> tuple:
    pass


def get_embed_dict_with_placeholders(json_text: str) -> dict:

    r = re.findall('<~.*?>+', json_text)
    for placeholder in r:
        if placeholder[2] == '~':
            json_text = json_text.replace(placeholder, placeholder[:2] + placeholder[3:])
        else:
            placeholder = placeholder.lower()
            p = placeholder[2:-1].split(':', 1)
            if p[0].strip() == 'image':
                image_url = imgs.get(p[1].strip().replace(' ', '_'))
                if image_url is None:
                    raise BadPlaceholder(placeholder)
                json_text = json_text.replace(placeholder, f'"{image_url}"')
            else:
                raise BadPlaceholder(placeholder)

    try:
        embed_dict = json.loads(json_text)
    except json.JSONDecodeError as error:
        raise BadJSON(error.args[0])

    return embed_dict


async def party_lifetime(ctx: commands.Context) -> None:
    global data
    party = data.guilds[ctx.guild.id].members[ctx.author.id].party
    if party.is_group:
        if party.delay - datetime.utcnow() <= timedelta(0):
            party.disband()
        else:
            party.delay_expire()


'''def errors_count(s1: str, s2: str) -> int:
    # Evaluates Damerau-Levenshtein distance
    ls1 = len(s1)
    ls2 = len(s2)
    m = [[0] * (ls2 + 1) for _ in range(ls1 + 1)]
    for i in range(1, ls1 + 1):
        m[i][0] = i
    for j in range(1, ls2 + 1):
        m[0][j] = j
    for i in range(1, ls1 + 1):
        for j in range(1, ls2 + 1):
            cost = int(s1[i - 1] != s2[j - 1])
            m[i][j] = min(m[i - 1][j] + 1,  # deletion
                          m[i][j - 1] + 1,  # insertion
                          m[i - 1][j - 1] + cost)  # substitution
            if i != 1 != j and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                m[i][j] = min(m[i][j], m[i - 2][j - 2] + cost)  # transposition
    return m[ls1][ls2]'''


class PassError(commands.CheckFailure):
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


class PartyInvite:
    def __init__(self, guild_id: int, member_id: int):
        self._guild_id = guild_id
        self._member_id = member_id
        self.inviters: dict[int, datetime] = {}

    def _clear_invites(self) -> None:
        now = datetime.utcnow()
        for inviter_id in self.inviters:
            if now - self.inviters[inviter_id] > timedelta(minutes=5) or get_member(self._guild_id, inviter_id) is None:
                del self.inviters[inviter_id]

    def invited_by(self, inviter_id: int) -> str:
        self._clear_invites()
        invite_time = self.inviters.get(inviter_id)
        if invite_time is None:
            if self.in_party:
                if self.is_inviter_party(inviter_id):
                    return 'IN_YOUR_PARTY'
                else:
                    self.inviters[inviter_id] = datetime.utcnow()
                    return 'INVITED_BUT_IN_PARTY'
            else:
                self.inviters[inviter_id] = datetime.utcnow()
                return 'INVITED'
        else:
            return 'INVITED_ALREADY'

    def try_accept(self, inviter_id: Optional[int] = None) -> str:
        if self.in_party:
            return 'IN_PARTY'
        self._clear_invites()
        invites_count = len(self.inviters)
        if invites_count == 0:
            return 'NO_INVITES'
        elif inviter_id is None:
            if invites_count == 1:
                inviter_id = self.inviters.popitem()[0]
                return self._accept(inviter_id)
            else:
                return 'UNCERTAIN'
        elif inviter_id in self:
            del self.inviters[inviter_id]
            return self._accept(inviter_id)
        else:
            return 'NO_INVITE_FROM'

    def _accept(self, inviter_id: int) -> str:
        global data
        return data.guilds[self._guild_id].members[inviter_id].party.join(self._member_id)

    @property
    def invites_list(self) -> list:
        self._clear_invites()
        return sorted(self.inviters, key=lambda x: self.inviters[x])

    @property
    def in_party(self) -> bool:
        global data
        return data.guilds[self._guild_id].members[self._member_id].party.is_group

    def is_inviter_party(self, inviter_id: int) -> bool:
        global data
        return self is data.guilds[self._guild_id].members[inviter_id].party

    def __contains__(self, item: int):
        return item in self.inviters


class Party:
    def __init__(self, guild_id: int, member_id: int):
        self._guild_id = guild_id
        self.members: list[int] = [member_id]
        self.delay: Optional[datetime] = None

    def join(self, member_id: int) -> str:
        self.members.append(member_id)
        self._join_member(member_id)
        self.delay_expire()
        return 'JOINED'

    def leave(self, member_id: int) -> str:
        if self.one_person_party:
            return 'NOT_IN_PARTY'
        self._kick_member(member_id)
        return 'LEFT'

    def kick(self, member_id: int) -> str:
        if self.one_person_party:
            return 'NOT_IN_PARTY'
        elif not self.in_list(member_id):
            return 'NOT_MEMBER'
        self._kick_member(member_id)
        return 'KICKED'

    def set_leader(self, member_id: int) -> str:
        if self.is_leader(member_id):
            return 'LEADER_ALREADY'
        if member_id not in self:
            return 'NOT_MEMBER'
        self.members.remove(member_id)
        self.members.insert(0, member_id)
        return 'NEW_LEADER_SET'

    def disband(self) -> str:
        if self.one_person_party:
            return 'NOT_IN_PARTY'
        for m in self.members:
            Party.recreate(self._guild_id, m)
        return 'DISBANDED'

    def is_leader(self, member_id: int) -> bool:
        return member_id == self.members[0]

    def in_list(self, member_id: int) -> bool:
        return member_id in self

    @property
    def one_person_party(self) -> bool:
        return len(self.members) == 1

    @property
    def is_group(self) -> bool:
        return len(self.members) > 1

    @property
    def leader(self):
        return self.members[0]

    @classmethod
    def recreate(cls, guild_id: int, member_id: int) -> None:
        global data
        data.guilds[guild_id].members[member_id].party = Party(guild_id, member_id)

    def _join_member(self, member_id) -> None:
        global data
        data.guilds[self._guild_id].members[member_id].party = self

    def _kick_member(self, member_id) -> None:
        global data
        self.members.remove(member_id)
        Party.recreate(self._guild_id, member_id)

    def delay_expire(self):
        self.delay = datetime.utcnow() + timedelta(seconds=PARTY_LIFETIME)

    def __contains__(self, item: int):
        return item in self.members


class EnchTest:
    def __init__(self, guild_id: int, member_id: int, questions_count: int):
        self._guild_id = guild_id
        self._member_id = member_id
        questions = []
        if questions_count != 1:
            for i in range(1, questions_count + 1):
                questions.append(Question(guild_id, i))
        else:
            questions.append(Question(guild_id, 0))
        self.some_questions = questions_count != 1
        self.message_id: Optional[int] = None
        self.index: int = 0
        self.questions_loop: bool = False
        self.questions: list[Question] = questions
        self.right: int = 0
        self.wrong: int = 0
        self.questions_count: int = questions_count

    async def answer_question(self, correct: bool):
        message = await get_school_message(self._guild_id, self._member_id, self.message_id)
        embed = message.embeds[0]
        if correct:
            self.right += 1
            embed.colour = 65_280
            await message.add_reaction('✅')
        else:
            self.wrong += 1
            embed.colour = 16_711_680
            await message.add_reaction('❌')
        await message.edit(embed=embed)
        del self.questions[self.index]
        if len(self.questions) == 0:
            await self.finish_ench()
        else:
            if len(self.questions) == self.index:
                self.index = 0
                self.questions_loop = True
            await self.print_question()

    async def reaction(self, message_id, emoji):
        if message_id == self.message_id:
            if emoji in question_numbers:
                answer_index = question_numbers.index(emoji)
                correctness = answer_index == self.questions[self.index].answer_index
                await self.answer_question(correctness)
            elif emoji in question_changers:
                delta = 2 * question_changers.index(emoji) - 1
                await self.change_question(delta)

    async def finish_ench(self):
        if self.some_questions:
            counts = [self.right, self.wrong]
            unanswered = self.questions_count - sum(counts)
            if unanswered:
                counts.append(unanswered)
            total = self.questions_count
            lines = get_propotional_lines(*counts)
            fields = [{'name': f'✅  {counts[0]}  ({round(100 * counts[0] / total, 1)}%)',
                       'value': lines[0], 'inline': False},
                      {'name': f'❌  {counts[1]}  ({round(100 * counts[1] / total, 1)}%)',
                       'value': lines[1], 'inline': False}]
            if unanswered:
                fields.append({'name': f'❔  {counts[2]}  ({round(100 * counts[2] / total, 1)}%)',
                               'value': lines[2], 'inline': False})
            embed_dict = {'title': translate(lang(self._guild_id), ('tests', 'you_answered')),
                          'color': 16744192, 'fields': fields}
            school = get_school(self._guild_id, self._member_id)
            await school.send(f'<@{self._member_id}>', embed=discord.Embed.from_dict(embed_dict))

    async def resume_ench(self):
        try:
            last_message = await get_school_message(self._guild_id, self._member_id, self.message_id)
            await last_message.delete()
        except (AttributeError, discord.NotFound):
            pass
        await self.print_question()

    async def print_question(self):
        global question_numbers
        school = get_school(self._guild_id, self._member_id)
        embed = discord.Embed.from_dict(self.questions[self.index].embed_dict)
        questions_amount = len(self.questions)
        reactions = list(question_numbers)
        if questions_amount != 1:
            if self.index != 0 or self.questions_loop:
                embed.add_field(name='⬅️', value=translate(lang(self._guild_id),
                                                           ('tests', 'previous_question')), inline=True)
                reactions.insert(0, '⬅️')
            embed.add_field(name='➡️', value=translate(lang(self._guild_id), ('tests', 'next_question')), inline=True)
            reactions.append('➡️')
        #embed.add_field(name=translate(lang(_guild_id), ('tests', 'for')), value=f'<@{_member_id}>', inline=True)
        msg = await school.send(f'<@{self._member_id}>', embed=embed)
        self.message_id = msg.id
        await fill_reactions(msg, reactions)

    async def change_question(self, delta: int):
        global question_numbers, question_changers
        questions_amount = len(self.questions)
        new_question_index = (self.index + delta) % questions_amount
        self.questions_loop = self.questions_loop or (self.index + delta == questions_amount)
        self.index = new_question_index
        embed = discord.Embed.from_dict(self.questions[new_question_index].embed_dict)
        reactions = list(question_numbers + question_changers[1:2])
        if (new_question_index != 0 or self.questions_loop) and questions_amount != 1:
            embed.add_field(name='⬅️', value=translate(lang(self._guild_id),
                                                       ('tests', 'previous_question')), inline=True)
            reactions.insert(0, '⬅️')
        embed.add_field(name='➡️', value=translate(lang(self._guild_id), ('tests', 'next_question')), inline=True)
        embed.add_field(name=translate(lang(self._guild_id), ('tests', 'question_for')),
                        value=f'<@{self._member_id}>', inline=True)
        message = await get_school_message(self._guild_id, self._member_id, self.message_id)
        await message.edit(embed=embed)
        await fill_reactions(message, reactions)


class Vote:

    def __init__(self, message_path: tuple[int], vote_type: str, options_number: int,
                 min_count: int, max_count: int, embed_dict: dict, time_finish: Optional[datetime] = None):
        self._message_path = message_path
        #self.name = name
        self.vote_type = vote_type
        self.options = [0] * options_number
        self.min_count = min_count
        self.max_count = max_count
        self.embed_dict = embed_dict
        self.time_finish = time_finish

    def send(self):
        pass

    def add(self):
        pass

    def update(self):
        pass

    def finish(self):
        pass


class Question:
    """Generates a test question"""

    def __init__(self, guild_id: int, number: int, type_index: Optional[int] = None):
        global ench_tests
        self._guild_id: int = guild_id
        self.number: int = number
        if type_index is None:
            type_ = choice(ench_tests[:4])
        elif 0 <= type_index < 12:
            type_ = ench_tests[type_index]
        else:
            raise TypeError
        self._type: str = type_
        question_data = self.get_question_data()
        self._description_substitution: dict = question_data[0]
        self._answer_options_lang_path: list = question_data[1]
        self.answer_index: int = question_data[2]
        self._random_choice: bool = question_data[3]

    @property
    def embed_dict(self):
        global data, question_numbers
        title = translate(lang(self._guild_id), ('tests', 'question'))
        if self.number != 0:
            title += translate(lang(self._guild_id), ('tests', 'question_number'), {'number': self.number})
        description = translate(lang(self._guild_id), ('ench', 'questions', self._type), self._description_substitution)
        fields = []
        for i in range(test_options_number):
            field = {'name': question_numbers[i], 'inline': True,
                     'value': translate(lang(self._guild_id), self._answer_options_lang_path[i], {},
                                        self._random_choice)}
            fields.append(field)
        embed_dict = {'title': title, 'description': description, 'color': 16_776_960, 'fields': fields}
        return embed_dict

    def get_question_data(self) -> tuple:
        try:
            func = Question.__dict__[self._type]
            return func(self)
        except KeyError:
            raise ValueError(NO_SUCH_QUESTION_TYPE.format(self._type))

    def max_ench_lvl(self) -> tuple:
        global ench_test_data
        ench = choice(list(ench_test_data['enchantments']))
        description_substitution = {'ench': translate(lang(self._guild_id), ('ench', 'enchantments', ench))}
        number = ench_test_data['enchantments'][ench]['max_level']
        numbers = sample(range(1, 6), test_options_number)
        if number not in numbers:
            numbers[0] = number
        numbers.sort()
        answer_index = numbers.index(number)
        answer_options_lang_path = [('roman_numerals', str(i)) for i in numbers]
        return description_substitution, answer_options_lang_path, answer_index, False

    def max_table_ench_lvl(self) -> tuple:
        global ench_test_data
        ench = choice(list(ench_test_data['enchantments']))
        description_substitution = {'ench': translate(lang(self._guild_id), ('ench', 'enchantments', ench))}
        number = ench_test_data['enchantments'][ench]['max_ench_table_level']
        numbers = sample(range(0, 6), test_options_number)
        if number not in numbers:
            numbers[0] = number
        numbers.sort(key=lambda x: x if x != 0 else 100)
        answer_index = numbers.index(number)
        answer_options_lang_path = [('roman_numerals', str(i)) for i in numbers]
        if numbers[-1] == 0:
            answer_options_lang_path[-1] = ('tests', 'impossible')
        return description_substitution, answer_options_lang_path, answer_index, False

    def get_ench_item(self) -> tuple:
        global ench_test_data
        enchs = ench_test_data['enchantments']
        enchantments = list(ench_test_data['enchantments'])
        enchantments.remove('curse_of_vanishing')
        ench = choice(enchantments)
        description_substitution = {'ench': translate(lang(self._guild_id), ('ench', 'enchantments', ench))}
        ench_items = set(enchs[ench]['primary_ench_items']) | set(enchs[ench]['secondary_ench_items'])
        available_items = list(set(ench_test_data['items']) - ench_items)
        items = sample(available_items, 2)
        answer_index = randrange(3)
        items.insert(answer_index, choice(list(ench_items)))
        answer_options_lang_path = [('ench', 'items', str(i)) for i in items]
        return description_substitution, answer_options_lang_path, answer_index, False

    def get_table_ench_item(self) -> tuple:
        global ench_test_data
        enchs = ench_test_data['enchantments']
        ench = choice(list(enchs))
        description_substitution = {'ench': translate(lang(self._guild_id), ('ench', 'enchantments', ench))}
        ench_items = set(enchs[ench]['primary_ench_items'])
        available_items = list(set(ench_test_data['items']) - ench_items)
        item1_index = randrange(len(available_items))
        items = [available_items.pop(item1_index)]
        if ench_items:
            item2 = sample(available_items + [None], 1, counts=[1] * len(available_items) + [8])[0]
            if item2 is None:
                answer_index = randrange(2)
                items.insert(answer_index, choice(list(ench_items)))
                items.append(item2)
            else:
                items.append(item2)
                answer_index = randrange(3)
                items.insert(answer_index, choice(list(ench_items)))
        else:
            items.append(choice(available_items))
            items.append(None)
            answer_index = 2
        answer_options_lang_path = []
        for i in items:
            if i is None:
                answer_options_lang_path.append(('tests', 'no_such_item'))
            else:
                answer_options_lang_path.append(('ench', 'items', str(i)))
        return description_substitution, answer_options_lang_path, answer_index, False


class GuessCraft:
    def __init__(self, guild_id: int, member_ids: set[int]):
        self._guild_id = guild_id
        self.guess = {m: None for m in member_ids}

    def start(self):
        pass

    def guess(self, member_id: int, guess: str):
        pass

    def __contains__(self, item):
        return item in self.guess


class Codenames:
    def __init__(self):
        with open('langs/codenames_ru.txt', encoding='utf-8') as file:
            codenames = file.read().split()
        self.names: list = [i.upper() for i in sample(codenames, 25)]
        red_first = randrange(2)
        self.red_first: bool = bool(red_first)
        self.roles: list = ['🟥'] * (8 + red_first) + ['🟦'] * (9 - red_first) + ['⬜'] * 7 + ['🟫']
        shuffle(self.roles)
        self.player_map: str = self.get_init_map_for_players()
        self.leader_map: str = self.get_init_map_for_leaders()
        self._player_message_paths: set[tuple] = set()
        self._leader_message_paths: set[tuple] = set()

    def get_init_map_for_players(self) -> str:
        play_map = ''
        for i in range(5):
            play_map += '\n\n '
            for j in range(5):
                play_map += self.names[5 * i + j].center(19, ' ')

        return '```\n' + play_map[2:] + '```'

    def get_init_map_for_leaders(self) -> str:
        play_map = ''
        for i in range(5):
            play_map += '\n\n '
            for j in range(5):
                play_map += (self.roles[5 * i + j] + self.names[5 * i + j]).center(18, ' ')

        return '```\n' + play_map[2:] + '```'

    def add_player_message(self, *message_path) -> None:
        self._player_message_paths.add(message_path)

    def add_leader_message(self, *message_path) -> None:
        self._leader_message_paths.add(message_path)

    async def reveal(self, name: str) -> None:
        name = name.upper()
        try:
            index = self.names.index(name)
        except ValueError:
            raise DontUnderstand(name)
        role = self.roles[index]
        role_name = role + name
        if len(name) % 2 == 1:
            name += ' '
        else:
            role_name += ' '
        self.player_map = self.player_map.replace(name, role.center(len(name) - 1, ' '))
        self.leader_map = self.leader_map.replace(role_name, role.center(len(name) - 1, ' '))
        await self.update()

    async def update(self) -> None:

        for i in self._player_message_paths:
            message = await get_message(*i)
            await message.edit(content=self.player_map)

        for i in self._leader_message_paths:
            message = await get_message(*i)
            await message.edit(content=self.leader_map)


class GlobalData:
    def __init__(self):
        self.guilds: dict[int, GuildData] = {}
        self.users: dict[int, UserData] = {}
        self.votes: dict[str, Vote] = {}
        self.stats: StatsData = StatsData()


class UserData:
    def __init__(self):
        self.votes: set[str] = set()
        self.stats: StatsData = StatsData()


class GuildData:
    def __init__(self):
        self.lang: str = DEFAULT_LANG
        self.home_ids: set[int] = set()
        self.school_ids: set[int] = set()
        self.members: dict[int, MemberData] = {}
        self.stats: StatsData = StatsData()


class MemberData:
    def __init__(self, guild_id, member_id):
        self.games: GamesData = GamesData()
        self.tests: TestsData = TestsData()
        self.invites: PartyInvite = PartyInvite(guild_id, member_id)
        self.party: Party = Party(guild_id, member_id)
        self.stats: StatsData = StatsData()


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
    def load_data(cls):
        global data
        try:
            with open(DATA, 'rb') as db:
                data = pickle.load(db)
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            print(CANNOT_READ.format(DATA))
            data = GlobalData()

    @classmethod
    def save_data(cls) -> None:
        try:
            global data
            with open(DATA, 'wb') as db:
                pickle.dump(data, db)
        except TypeError as error:
            print(error)

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


class Checks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def bot_check(self, ctx: commands.Context):
        return not ctx.author.bot

    @classmethod
    def in_guild_home(cls):
        global data

        async def predicate(ctx: commands.Context):
            home_ids = data.guilds[ctx.guild.id].home_ids
            if not home_ids:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'need_home')))
                raise PassError
            elif ctx.channel.id not in home_ids:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'go_home')))
                raise PassError
            return True

        return commands.check(predicate)

    @classmethod
    def in_guild_school(cls):
        global data

        async def predicate(ctx: commands.Context):
            school_ids = data.guilds[ctx.guild.id].school_ids
            if not school_ids:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'need_school')))
                raise PassError
            elif ctx.channel.id not in school_ids:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'go_to_school')))
                raise PassError
            return True

        return commands.check(predicate)

    @classmethod
    def is_playing(cls, game=None):
        global data

        async def predicate(ctx: commands.Context):
            active = data.guilds[ctx.guild.id].members[ctx.author.id].games.active
            if game is None and active == '':
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'not_playing')))
                raise PassError
            elif active != game and game:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'not_that_game'), {'game': game}))
                raise PassError
            elif game == '' != active:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'playing_yet')))
                raise PassError
            return True

        return commands.check(predicate)

    @classmethod
    def is_testing(cls, test=None):
        global data

        async def predicate(ctx: commands.Context):
            active = data.guilds[ctx.guild.id].members[ctx.author.id].tests.active
            if test is None and active != '':
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'not_testing')))
                raise PassError
            elif active != test != '':
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'not_that_test'), {'test': test}))
                raise PassError
            elif test == '' != active:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'testing_yet')))
                raise PassError
            return True

        return commands.check(predicate)

    @classmethod
    def in_party(cls):
        global data

        async def predicate(ctx: commands.Context):
            party = data.guilds[ctx.guild.id].members[ctx.author.id].party
            if party.one_person_party:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'not_in_party')))
                raise PassError
            return True

        return commands.check(predicate)

    @classmethod
    def not_in_party(cls):
        global data

        async def predicate(ctx: commands.Context):
            party = data.guilds[ctx.guild.id].members[ctx.author.id].party
            if party.is_group:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'in_party')))
                raise PassError
            return True

        return commands.check(predicate)

    @classmethod
    def is_party_leader(cls):
        global data

        async def predicate(ctx: commands.Context):
            party = data.guilds[ctx.guild.id].members[ctx.author.id].party
            if not party.is_leader(ctx.author.id):
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'not_leader')))
                raise PassError
            return True

        return commands.check(predicate)


class Main(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{bot.user} is ready!')

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild):
        global data
        init_guild(guild.id)
        if guild.id == _MY_GUILD:
            await get_stats_line_emojis(guild)
        async for member in guild.fetch_members():
            if not member.bot:
                init_member(guild.id, member.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.bot:
            init_member(member.guild.id, member.id)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, PassError):
            pass
        elif isinstance(error, commands.BadArgument):
            await ctx.message.add_reaction('❓')
        elif isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction('❓')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.add_reaction('❓')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.message.add_reaction('❓')
        elif isinstance(error, NothingHere):
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'nothing_here')))
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'not_a_guild')))
        elif isinstance(error, BadJSON):
            error_msg = error.args[0]
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'bad_json'), {'json_error': error_msg}))
        elif isinstance(error, BadPlaceholder):
            error_msg = error.args[0]
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'bad_placeholder'), {'placeholder': error_msg}))
        elif isinstance(error, DontUnderstand):
            error_msg = error.args[0]
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'dont_understand'), {'text': error_msg}))
        elif isinstance(error, PlayersRepeat):
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'players_repeat')))
        elif isinstance(error, PlayerNotInParty):
            error_msg = error.args[0]
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'player_not_in_party'), {'player': error_msg}))
        else:
            raise error

    @commands.command()
    @commands.is_owner()
    async def kill(self, ctx: commands.Context):
        await ctx.send('Какой жестокий мир!\nОтключаюсь...', )
        Loaders.save_data()
        await self.bot.logout()

    @commands.Cog.listener()
    async def on_disconnect(self):
        Loaders.save_data()


class Homes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='home')
    async def home(self, ctx: commands.Context):
        global data
        if ctx.invoked_subcommand is None:
            home_ids = data.guilds[ctx.guild.id].home_ids
            if ctx.channel.id in home_ids:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'home_here')))
            else:
                await self.home_list(ctx)

    @home.command(name='list')
    async def home_list(self, ctx: commands.Context):
        global data
        home_ids = data.guilds[ctx.guild.id].home_ids
        if home_ids:
            homes = ', '.join([f'<#{i}>' for i in home_ids])
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'homes_list'), {'list': homes}))
        else:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_homes')))

    @home.command(name='set')
    @commands.has_permissions(manage_channels=True)
    async def set_home(self, ctx: commands.Context):
        global data
        home_ids = data.guilds[ctx.guild.id].home_ids
        if ctx.channel.id in home_ids:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'home_here_already')))
        else:
            data.guilds[ctx.guild.id].home_ids.add(ctx.channel.id)
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'new_home')))

    @home.command(name='remove')
    @commands.has_permissions(manage_channels=True)
    async def del_home(self, ctx: commands.Context, *, arg: str = ''):
        global data
        guild_id = ctx.guild.id
        home_ids = data.guilds[guild_id].home_ids
        if ctx.channel.id not in home_ids:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_home_here')))
        else:
            games_count = count_games(guild_id)
            if games_count != 0 and arg != 'confirm':
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'delhome_warning'),
                                         {'games_count': games_count}))
            else:
                abort_games(guild_id)
                data.guilds[guild_id].home_ids.remove(ctx.channel.id)
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'home_removed')))


class Schools(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='school')
    async def school(self, ctx: commands.Context):
        global data
        if ctx.invoked_subcommand is None:
            guild_id = ctx.guild.id
            school_ids = data.guilds[guild_id].school_ids
            if ctx.channel.id in school_ids:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'school_here')))
            else:
                await self.school_list(ctx)

    @school.command(name='list')
    async def school_list(self, ctx: commands.Context):
        global data
        school_ids = data.guilds[ctx.guild.id].school_ids
        if school_ids:
            schools = ', '.join([f'<#{i}>' for i in school_ids])
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'schools_list'), {'list': schools}))
        else:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_schools')))

    @school.command(name='set')
    @commands.has_permissions(manage_channels=True)
    async def set_school(self, ctx: commands.Context):
        global data
        school_ids = data.guilds[ctx.guild.id].school_ids
        if ctx.channel.id in school_ids:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'school_here_already')))
        else:
            data.guilds[ctx.guild.id].school_ids.add(ctx.channel.id)
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'new_school')))

    @school.command(name='remove')
    @commands.has_permissions(manage_channels=True)
    async def del_school(self, ctx: commands.Context, *, arg: str = ''):
        global data
        guild_id = ctx.guild.id
        school_ids = data.guilds[guild_id].school_ids
        if ctx.channel.id not in school_ids:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_school_here')))
        else:
            tests_count = count_tests(guild_id)
            if tests_count != 0 and arg != 'confirm':
                await ctx.send(
                    translate(lang(ctx.guild.id), ('messages', 'delschool_warning'), {'tests_count': tests_count}))
            else:
                abort_tests(guild_id)
                data.guilds[guild_id].school_ids.remove(ctx.channel.id)
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'school_removed')))


class Actions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx: commands.Context, *, arg: str = ''):
        if not arg or arg == 'list':
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'messages_list'), dict(list=", ".join(msgs))))
        elif arg in msgs:
            try:
                await ctx.send(msgs[arg])
            except FileNotFoundError:
                print(FILE_NOT_FOUND.format(msgs[arg]))

    @commands.command()
    @commands.has_permissions(attach_files=True, embed_links=True)
    async def image(self, ctx: commands.Context, *, arg: str = ''):
        if not arg or arg == 'list':
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'images_list'), dict(list=", ".join(imgs))))
        elif arg in imgs:
            try:
                await ctx.send(imgs[arg])
            except FileNotFoundError:
                print(FILE_NOT_FOUND.format(imgs[arg]))

    @commands.command()
    @commands.has_permissions(attach_files=True)
    async def sound(self, ctx: commands.Context, *, arg: str = ''):
        if not arg or arg == 'list':
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'sounds_list'), dict(list=", ".join(snds))))
        elif arg in snds:
            try:
                await ctx.send(file=discord.File('sounds/' + snds[arg]))
            except FileNotFoundError:
                print(FILE_NOT_FOUND.format(snds[arg]))

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def send(self, ctx: commands.Context,
                   members_and_channels: commands.Greedy[Union[discord.Member, discord.TextChannel, discord.Role]],
                   *, json_text: str = '{}'):

        k = json_text.find('{')
        not_parsed = json_text[:k].split()
        if not_parsed:
            raise DontUnderstand(not_parsed[0])

        if not members_and_channels:
            raise commands.BadArgument

        embed_dict = get_embed_dict_with_placeholders(json_text)

        if ctx.guild is None:
            url = f'https://discord.com/channels/@me/{ctx.channel.id}/{ctx.message.id}'
        else:
            url = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}'
        embed = discord.Embed.from_dict(embed_dict)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url, url=url)

        for elem in members_and_channels:
            if isinstance(elem, discord.Member):
                await elem.send(embed=embed)
            elif isinstance(elem, discord.TextChannel):
                await elem.send(embed=embed)
            else:
                for member in elem.members:
                    await member.send(embed=embed)

    @commands.command(name='lang')
    @commands.has_permissions(manage_channels=True)
    async def language(self, ctx: commands.Context, *, lang_: str = ''):
        global data, lang_list
        if lang_ and lang_ != 'list':
            if lang_ in lang_list:
                data.guilds[ctx.guild.id].lang = lang_
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'lang_changed')))
            else:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_such_lang')))
        else:
            guild_id = ctx.guild.id
            lang_set = lang(guild_id)
            text = f"{translate(lang_set, ('messages', 'lang_set'))}\n" \
                   f"{translate(lang_set, ('lang',))} [{lang_set}]\n" \
                   f"{translate(lang_set, ('messages', 'available_langs'))}\n"
            for k in lang_list:
                if lang_set != k:
                    text += f"{translate(k, ('lang',))} [{k}]\n"
            await ctx.send(text)

    @commands.command(name='react')
    @commands.has_permissions(manage_messages=True)
    async def reacts(self, ctx: commands.Context, *reacts):
        """For custom reactions"""
        global reactions
        msg_list = await ctx.channel.history(limit=1, before=ctx.message.created_at).flatten()
        msg = msg_list[0]
        reacts_list = []
        try_number = False
        try_word = False
        for i in reacts:
            if try_number:
                try_number = False
                if i.isnumeric():
                    reacts_list.extend(numvote_list(int(i)))
            elif try_word:
                try_word = False
                i = i.lower()
                for c in i:
                    if 'a' <= c <= 'z':
                        reacts_list.append(chr(REACTION_LETTER + ord(c)))
                    elif c == ' ':
                        reacts_list.append(reactions[0]['bs'])
            elif i in reactions[0]:
                reacts_list.append(reactions[0][i])
            elif i in reactions[1]:
                for j in reactions[1][i]:
                    reacts_list.append(reactions[0][j])
            elif i in reactions[2]:
                try_number = True
            elif i in reactions[3]:
                try_word = True

        await fill_reactions(msg, reacts_list)
        await ctx.message.delete()


class Parties(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    async def party(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument(NO_SUBCOMMAND)

    @party.command(name='list')
    @Checks.in_party()
    async def party_list(self, ctx: commands.Context):
        global data
        party_member_ids = data.guilds[ctx.guild.id].members[ctx.author.id].party.members
        party_member_nicks = [ctx.guild.get_member(i).display_name for i in party_member_ids]
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'party_list'),
                                 dict(list=', '.join(party_member_nicks))))

    @party.command(name='invite')
    @Checks.is_party_leader()
    async def party_invite(self, ctx: commands.Context, members: commands.Greedy[discord.Member]):
        global data, bot
        if not members:
            raise commands.BadArgument
        for member in members:
            if member.id == bot.user.id:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'i_invited'), rand=True))
            elif member.bot:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'bot_invited'),
                                         {'bot': member.display_name}, rand=True))
            elif member.id == ctx.author.id:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'self_invite'), rand=True))
            else:
                result = data.guilds[ctx.guild.id].members[member.id].invites.invited_by(ctx.author.id)
                await ctx.send(translate(lang(ctx.guild.id), ('messages', phrase_codes[result]),
                                         {'member': member.display_name}))

    @party.command(name='accept')
    @Checks.not_in_party()
    async def party_accept(self, ctx: commands.Context, member: Optional[discord.Member]):
        global data
        if member is None:
            member_id = None
        else:
            member_id = member.id
        member_data = data.guilds[ctx.guild.id].members[ctx.author.id]
        result = member_data.invites.try_accept(member_id)
        if result == 'AMBIGUOUS':
            inviters = ', '.join([ctx.guild.get_member(i).display_name for i in member_data.invites.invites_list])
            await ctx.send(translate(lang(ctx.guild.id), ('messages', phrase_codes[result]), {'list': inviters}))
        elif result == 'NO_INVITE_FROM':
            await ctx.send(translate(lang(ctx.guild.id), ('messages', phrase_codes[result]),
                                     {'member': ctx.guild.get_member(member_id).display_name}))
        elif result == 'JOINED':
            if member is None:
                member_id = member_data.party.leader
            await ctx.send(translate(lang(ctx.guild.id), ('messages', phrase_codes[result]),
                                     {'member': ctx.guild.get_member(member_id).display_name}))
        elif result == 'NO_INVITES':
            await ctx.send(translate(lang(ctx.guild.id), ('messages', phrase_codes[result])))
        else:
            raise RaiseError

    @party.command(name='join')
    @Checks.not_in_party()
    async def party_join(self, ctx: commands.Context, member: Optional[discord.Member]):
        await self.party_accept(ctx, member)

    @party.command(name='leave')
    @Checks.in_party()
    async def party_leave(self, ctx: commands.Context):
        global data
        result = data.guilds[ctx.guild.id].members[ctx.author.id].party.leave(ctx.author.id)
        await ctx.send(translate(lang(ctx.guild.id), ('messages', phrase_codes[result])))

    @party.command(name='kick')
    @Checks.is_party_leader()
    @Checks.in_party()
    async def party_kick(self, ctx: commands.Context, members: commands.Greedy[discord.Member]):
        global data
        if not members:
            raise commands.BadArgument
        party = data.guilds[ctx.guild.id].members[ctx.author.id].party
        for member in members:
            result = party.kick(member.id)
            await ctx.send(translate(lang(ctx.guild.id), ('messages', phrase_codes[result]),
                                     {'member': member.display_name}))

    @party.command(name='leader')
    @Checks.is_party_leader()
    @Checks.in_party()
    async def party_leader(self, ctx: commands.Context, member: discord.Member):
        result = data.guilds[ctx.guild.id].members[ctx.author.id].party.set_leader(member.id)
        await ctx.send(translate(lang(ctx.guild.id), ('messages', phrase_codes[result]),
                                 {'member': member.display_name}))

    @party.command(name='disband')
    @Checks.is_party_leader()
    @Checks.in_party()
    async def party_disband(self, ctx: commands.Context):
        result = data.guilds[ctx.guild.id].members[ctx.author.id].party.disband()
        await ctx.send(translate(lang(ctx.guild.id), ('messages', phrase_codes[result])))

    async def cog_before_invoke(self, ctx: commands.Context):
        await party_lifetime(ctx)


class Games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @Checks.in_guild_home()
    async def game(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed:
                raise commands.BadArgument(NO_SUBCOMMAND)
            else:
                await self.game_list(ctx)

    @game.command(name='list')
    async def game_list(self, ctx: commands.Context):
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'games_list'), dict(list=", ".join(games))))

    @game.command(name='kick')
    @Checks.is_playing()
    @Checks.in_party()
    async def game_kick(self, ctx: commands.Context, members: commands.Greedy[discord.Member]):
        pass

    @game.command(name='finish')
    @Checks.is_playing()
    async def game_finish(self, ctx: commands.Context):
        players = data.guilds[ctx.guild.id].members[ctx.author.id].games.players
        for member_id in players:
            data.guilds[ctx.guild.id].members[member_id].games.finish()
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'finish_game')))

    @game.command(name='stats')
    async def game_stats(self, ctx: commands.Context):
        raise NothingHere

    @game.group(name='start')
    @Checks.is_party_leader()
    async def game_start(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument(NO_SUBCOMMAND)

    @game_start.command(name='codenames')
    @Checks.in_party()
    async def game_codenames(self, ctx: commands.Context, count: int, players: commands.Greedy[discord.Member]):
        global data
        players_set = set(players)

        if len(players) != len(players_set):
            raise PlayersRepeat

        party = data.guilds[ctx.guild.id].members[ctx.author.id].party
        for member in players_set:
            if member.id not in party:
                raise PlayerNotInParty(member.display_name)

        team1 = players[:count]
        team2 = players[count:]

        codenames = Codenames()
        red_first = codenames.red_first

        leaders = set()
        if team1:
            leaders.add(team1[0])
        if team2:
            leaders.add(team2[0])

        def is_red(member):
            member_team1 = member in team1
            return member_team1 and red_first or not (member_team1 or red_first)

        player_ids_set = set(member.id for member in players_set)
        for member in players_set:
            games_data = data.guilds[ctx.guild.id].members[member.id].games
            games_data.active = 'CODENAMES'
            games_data.home_id = ctx.channel.id
            games_data.game = CodenamesData(codenames, member in leaders, is_red(member))
            games_data.players = player_ids_set

        colors = ('ini', 'css')
        team1_str = '\n'.join([f'[{member.display_name}]' for member in team1])
        team2_str = '\n'.join([f'[{member.display_name}]' for member in team2])
        player_list = ''
        if team1:
            player_list += f'```{colors[red_first]}\n{team1_str}```\n'
        if team2:
            player_list += f'```{colors[1 - red_first]}\n{team2_str}```'
        await ctx.send(player_list)

        message = await ctx.send(codenames.player_map)
        codenames.add_player_message(ctx.guild.id, ctx.channel.id, message.id)

        if team1:
            message1 = await team1[0].send(codenames.leader_map)
            codenames.add_leader_message(message1.channel.id, message1.id)

        if team2:
            message2 = await team2[0].send(codenames.leader_map)
            codenames.add_leader_message(message2.channel.id, message2.id)

    @commands.command()
    @Checks.is_playing('CODENAMES')
    async def show(self, ctx: commands.Context, name: str):
        await data.guilds[ctx.guild.id].members[ctx.author.id].games.game.codenames.reveal(name)

    async def cog_before_invoke(self, ctx: commands.Context):
        await party_lifetime(ctx)


class Tests(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @Checks.in_guild_school()
    async def test(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed:
                raise commands.BadArgument(NO_SUBCOMMAND)
            else:
                await self.test_list(ctx)

    @test.command(name='list')
    async def test_list(self, ctx: commands.Context):
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'tests_list'), dict(list=", ".join(tests))))

    @test.command(name='finish')
    @Checks.is_testing()
    async def test_finish(self, ctx: commands.Context):
        global data
        testers = data.guilds[ctx.guild.id].members[ctx.author.id].tests.testers
        for i in testers:
            tests_data = data.guilds[ctx.guild.id].members[i].tests
            if tests_data.active == 'ENCH':
                await tests_data.test.finish_ench()
            tests_data.finish()

    @test.command(name='resume')
    @Checks.is_testing()
    async def test_resume(self, ctx: commands.Context):
        global data
        await data.guilds[ctx.guild.id].members[ctx.author.id].tests.test.resume_ench()

    @test.command(name='stats')
    async def test_stats(self, ctx: commands.Context):
        raise NothingHere

    @test.group(name='start')
    @Checks.in_guild_school()
    async def test_start(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument(NO_SUBCOMMAND)

    @test_start.command(name='ench')
    @Checks.is_testing('')
    async def start_ench(self, ctx: commands.Context, count: int = 1):
        global data
        if count > ENCH_TEST_MAX_QUESTIONS_COUNT:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'too_many_questions'),
                                     {'count': ENCH_TEST_MAX_QUESTIONS_COUNT}))
        elif count <= 0:
            raise commands.BadArgument
        else:
            tests = data.guilds[ctx.guild.id].members[ctx.author.id].tests
            tests.active = 'ENCH'
            tests.school_id = ctx.channel.id
            ench_test = EnchTest(ctx.guild.id, ctx.author.id, count)
            tests.test = ench_test
            await ench_test.print_question()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        global data
        if not user.bot:
            try:
                tests_data = data.guilds[reaction.message.guild.id].members[user.id].tests
                if tests_data.active == 'ench':
                    await tests_data.test.reaction(reaction.message.id, str(reaction))
            except (KeyError, AttributeError):
                pass

    async def cog_before_invoke(self, ctx: commands.Context):
        await party_lifetime(ctx)


class Votes(commands.Cog):  # todo

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def vote(self, ctx: commands.Context, name: str):
        if ctx.invoked_subcommand is None:
            pass

    @vote.command(name='start')
    async def vote_start(self, ctx: commands.Context, name: str, vote_type: str, votes_count: int,
                         min_vote: int, max_vote: int, json_embed: str, time_finish: Optional[str] = None):
        embed_dict = get_embed_dict_with_placeholders(json_embed)
        message = await ctx.send()
        Vote(ctx.guild.id)

    @vote.command(name='finish')
    async def vote_finish(self, ctx: commands.Context):
        pass

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        pass


if __name__ == '__main__':

    set_logging(log)

    data: GlobalData
    Loaders.load_data()

    ench_test_data = Loaders.load_ench_data()

    guild_data_dict = GuildData().__dict__
    member_data_dict = MemberData(0, 0).__dict__

    lang_dict = {}
    for elem in lang_list:
        lang_dict[elem] = Loaders.load_lang(elem)

    ench_tests = list(lang_dict[DEFAULT_LANG]['ench']['questions'])

    bot = commands.Bot(command_prefix=BOT_PREFIX, intents=INTENTS)

    bot.add_cog(Checks(bot))
    bot.add_cog(Main(bot))
    bot.add_cog(Homes(bot))
    bot.add_cog(Schools(bot))
    bot.add_cog(Actions(bot))
    bot.add_cog(Parties(bot))
    bot.add_cog(Games(bot))
    bot.add_cog(Tests(bot))
    bot.add_cog(Votes(bot))

    with open('token.txt') as token:
        bot.run(token.readline())
