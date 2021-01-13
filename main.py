#! python
# coding=utf-8
"""Chubaka bot"""

import logging
import pickle
import json
from string import Template
from random import choice, sample, randrange
from typing import Optional

import discord
from discord.ext import commands


# ⛔🚫🛑💯⬅️➡️❓❗

DEBUG = True

if DEBUG:
    log = logging.DEBUG
else:
    log = logging.WARN

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, emojis=True)

DEFAULT_LANG = 'en_us'
ENCH_TEST_MAX_QUESTIONS_COUNT = 10
BOT_PREFIX = '~'
ENCH_VERSION = '1.16'
MAX_STATS_LINE_LENGTH = 12
_MY_GUILD = 671035889174183941

TRANSLATION_FAILED = "Translation failed on a path {} with lang '{}'"
FILE_NOT_FOUND = "File not found: '{}'"
NO_SUBCOMMAND = 'No subcommand'
CANNOT_READ = "Can't read data from '{}'"
NO_SUCH_ACTIVITY = "Activity is neither 'game' nor 'test'"
NO_SUCH_QUESTION_TYPE = "No such question type '{}'"

msgs = {'hello': 'Дратути!'}
imgs = {'bedy': 'bedy_s_bashkoj.jpg'}
snds = {'blya': 'blyat_chto.ogg', 'izv': 'izvinite.ogg', 'bat': 'batyushki.ogg', 'uzh': 'uzhas.ogg',
        'nah': 'poshyol_nahuj.ogg', 'logo': 'bananana.ogg', 'logo1': 'banananana.ogg'}
reactions = ({'look': '👀', 'up': '👍', 'down': '👎', 'check': '✅', 'cross': '❌', 'think': '🤔', 'q': '❔', 'i': 'ℹ️',
              'ok': '🆗', 's': '💬', 'w': '⚠️', '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣',
              '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣', '10': '🔟'},
             {'vote': ('up', 'down'), 'ivote': ('check', 'cross')},
             {'numvote': ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')})
games = ('numb', 'b&c', 'stones')
tests = ('ench',)
lang_list = ('ru_ru', 'en_us')
stats_line_emojis = ['line_small', 'line_left', 'line_middle', 'line_right']

question_numbers = ('1️⃣', '2️⃣', '3️⃣')
test_options_number = len(question_numbers)
question_changers = ('⬅️', '➡️')


class GlobalData:
    def __init__(self):
        self.guilds: dict[int, GuildData] = {}
        self.users: dict[int, UserData] = {}


class UserData:
    def __init__(self):
        pass


class GuildData:
    def __init__(self):
        self.lang: str = DEFAULT_LANG
        self.home_id: Optional[int] = None
        self.school_id: Optional[int] = None
        self.members: dict[int, MemberData] = {}
        self.stats: StatsData = StatsData()


class MemberData:
    def __init__(self):
        self.games: GamesData = GamesData()
        self.tests: TestsData = TestsData()
        self.stats: StatsData = StatsData()


class GamesData:
    def __init__(self):
        self.active: bool = False


class TestsData:
    def __init__(self):
        self.active: bool = False
        self.ench: EnchData = EnchData()


class EnchData:
    def __init__(self):
        self.message_id: Optional[int] = None
        self.index: int = 0
        self.questions_loop: bool = False
        self.some_questions: bool = False
        self.questions: list[Question] = []
        self.stats: Optional[EnchStatsData] = None


class StatsData:
    def __init__(self):
        pass


class EnchStatsData:
    def __init__(self, questions_count: int):
        self.right: int = 0
        self.wrong: int = 0
        self.questions_count: int = questions_count


def set_logging(log_type):
    logger = logging.getLogger('discord')
    logger.setLevel(log_type)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def load_data(file_name: str) -> GlobalData:
    try:
        with open(file_name, 'rb') as db:
            data_ = pickle.load(db)
    except (FileNotFoundError, pickle.UnpicklingError):
        print(CANNOT_READ.format(file_name))
        data_ = GlobalData()
    return data_


def save_data(data_: GlobalData) -> None:
    with open('data', 'wb') as db:
        pickle.dump(data_, db)


def load_json(path: str) -> dict:
    try:
        with open(path + '.json', encoding='utf-8') as lang_file:
            return json.load(lang_file)
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError(CANNOT_READ.format(f'langs/{path}.json'))


def load_lang(name: str) -> dict:
    return load_json('langs/' + name)


def load_ench_data() -> dict:
    return load_json('activities/ench/' + ENCH_VERSION)


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
        guild_members[member_id] = MemberData()
    else:
        member_dict = member_data.__dict__
        if member_dict != member_data_dict:
            member_data.__dict__ = member_data_dict | member_dict
            guild_members[member_id] = member_data


def count_games(guild_id: int) -> int:
    global data
    count = 0
    for member_data in data.guilds[guild_id].members.values():
        count += member_data.games.active
    return count


def count_tests(guild_id: int) -> int:
    global data
    count = 0
    for member_data in data.guilds[guild_id].members.values():
        count += member_data.tests.active
    return count


def abort_games(guild_id: int) -> None:
    global data
    member_data = data.guilds[guild_id].members
    for member_id in member_data:
        member_data[member_id].games = GamesData()


def abort_tests(guild_id: int) -> None:
    global data
    member_data = data.guilds[guild_id].members
    for member_id in member_data:
        member_data[member_id].tests = TestsData()


def get_options(path: tuple) -> list:
    global lang_dict
    opt = lang_dict[DEFAULT_LANG]
    for el in path:
        opt = opt[el]
    return list(opt.keys())


def lang(guild_id: int):
    global data
    return data.guilds[guild_id].lang


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


async def get_stats_line_emojis(guild):
    global stats_line_emojis
    emojis = await guild.fetch_emojis()
    for i in range(len(stats_line_emojis)):
        for e in emojis:
            if stats_line_emojis[i] == e.name:
                stats_line_emojis[i] = e


async def fill_reactions(message: discord.Message, reactions: iter):
    await message.clear_reactions()
    for reaction in reactions:
        await message.add_reaction(reaction)


async def answer_question(guild_id: int, member_id: int, message: discord.Message, correct: bool):
    global data
    ench_data = data.guilds[guild_id].members[member_id].tests.ench
    embed = message.embeds[0]
    if correct:
        ench_data.stats.right += 1
        embed.colour = 65_280
        await message.add_reaction('✅')
    else:
        ench_data.stats.wrong += 1
        embed.colour = 16_711_680
        await message.add_reaction('❌')
    await message.edit(embed=embed)
    del ench_data.questions[ench_data.index]
    if len(ench_data.questions) == 0:
        await finish_ench(guild_id, member_id)
    else:
        if len(ench_data.questions) == ench_data.index:
            ench_data.index = 0
            ench_data.questions_loop = True
        await print_question(guild_id, member_id)


async def finish_ench(guild_id: int, member_id: int):
    global data, bot
    guild = bot.get_guild(guild_id)
    member_data = data.guilds[guild_id].members[member_id]
    school = guild.get_channel(data.guilds[guild_id].school_id)
    member_data.tests.active = False
    ench_data = member_data.tests.ench
    ench_data.message_id = None
    if not ench_data.some_questions:
        pass
    else:
        stats_data = ench_data.stats
        counts = [stats_data.right, stats_data.wrong]
        unanswered = stats_data.questions_count - sum(counts)
        if unanswered:
            counts.append(unanswered)
        total = stats_data.questions_count
        lines = get_propotional_lines(*counts)
        fields = [{'name': f'✅  {counts[0]}  ({round(100 * counts[0] / total, 1)}%)',
                   'value': lines[0], 'inline': False},
                  {'name': f'❌  {counts[1]}  ({round(100 * counts[1] / total, 1)}%)',
                   'value': lines[1], 'inline': False}]
        if unanswered:
            fields.append({'name': f'❔  {counts[2]}  ({round(100 * counts[2] / total, 1)}%)',
                           'value': lines[2], 'inline': False})
        embed_dict = {'title': translate(lang(guild_id), ('tests', 'you_answered')),
                      'color': 16744192, 'fields': fields}
        await school.send(f'<@{member_id}>', embed=discord.Embed.from_dict(embed_dict))


async def print_question(guild_id: int, member_id: int):
    global data, bot
    guild = bot.get_guild(guild_id)
    guild_data = data.guilds[guild_id]
    ench_data = guild_data.members[member_id].tests.ench
    school = guild.get_channel(guild_data.school_id)
    questions = guild_data.members[member_id].tests.ench.questions
    embed = discord.Embed.from_dict(questions[ench_data.index].embed_dict)
    questions_count = len(questions)
    reactions = ['1️⃣', '2️⃣', '3️⃣']
    if questions_count != 1:
        if ench_data.index != 0 or ench_data.questions_loop:
            embed.add_field(name='⬅️', value=translate(lang(guild_id), ('tests', 'previous_question')), inline=True)
            reactions.insert(0, '⬅️')
        embed.add_field(name='➡️', value=translate(lang(guild_id), ('tests', 'next_question')), inline=True)
        reactions.append('➡️')
    #embed.add_field(name=translate(lang(guild_id), ('tests', 'for')), value=f'<@{member_id}>', inline=True)
    msg = await school.send(f'<@{member_id}>', embed=embed)
    ench_data.message_id = msg.id
    await fill_reactions(msg, reactions)


async def change_question(guild_id: int, member_id: int, message: discord.Message, delta: int):
    global data
    ench_data = data.guilds[guild_id].members[member_id].tests.ench
    questions = ench_data.questions
    question_index = ench_data.index
    questions_count = len(questions)
    new_question_index = (question_index + delta) % questions_count
    ench_data.questions_loop = ench_data.questions_loop or (question_index + delta == questions_count)
    ench_data.index = new_question_index
    embed = discord.Embed.from_dict(questions[new_question_index].embed_dict)
    reactions = ['1️⃣', '2️⃣', '3️⃣', '➡️']
    if (new_question_index != 0 or ench_data.questions_loop) and questions_count != 1:
        embed.add_field(name='⬅️', value=translate(lang(guild_id), ('tests', 'previous_question')), inline=True)
        reactions.insert(0, '⬅️')
    embed.add_field(name='➡️', value=translate(lang(guild_id), ('tests', 'next_question')), inline=True)
    embed.add_field(name=translate(lang(guild_id), ('tests', 'question_for')), value=f'<@{member_id}>', inline=True)
    await message.edit(embed=embed)
    await fill_reactions(message, reactions)


async def my_logout():
    save_data(data)
    await bot.logout()


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

#
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
#

# CHECKS


@bot.check
async def no_reply_on_bots(ctx: commands.Context):
    return not ctx.author.bot


def in_guild_home():
    global data

    async def predicate(ctx: commands.Context):
        home_id = data.guilds[ctx.guild.id].home_id
        if home_id is None:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'need_home')))
            raise MyCheckError
        elif home_id != ctx.channel.id:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'go_home')))
            raise MyCheckError
        return True

    return commands.check(predicate)


def in_guild_school():
    global data

    async def predicate(ctx: commands.Context):
        school_id = data.guilds[ctx.guild.id].school_id
        if school_id is None:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'need_school')))
            raise MyCheckError
        elif school_id != ctx.channel.id:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'go_to_school')))
            raise MyCheckError
        return True

    return commands.check(predicate)


def is_not_playing():
    global data

    async def predicate(ctx: commands.Context):
        member_data = data.guilds[ctx.guild.id].members[ctx.author.id]
        if member_data.games.active:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'is_playing_yet')))
            raise MyCheckError
        return True

    return commands.check(predicate)


def is_not_testing():
    global data

    async def predicate(ctx: commands.Context):
        member_data = data.guilds[ctx.guild.id].members[ctx.author.id]
        if member_data.tests.active:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'is_testing_yet')))
            raise MyCheckError
        return True

    return commands.check(predicate)


def is_playing():
    global data

    async def predicate(ctx: commands.Context):
        member_data = data.guilds[ctx.guild.id].members[ctx.author.id]
        if not member_data.games.active:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'is_not_playing')))
            raise MyCheckError
        return True

    return commands.check(predicate)


def is_testing():
    global data

    async def predicate(ctx: commands.Context):
        member_data = data.guilds[ctx.guild.id].members[ctx.author.id]
        if not member_data.tests.active:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'is_not_testing')))
            raise MyCheckError
        return True

    return commands.check(predicate)


class MyCheckError(commands.CheckFailure):
    pass


class NothingHere(commands.CommandNotFound):
    pass


# EVENTS


@bot.event
async def on_ready():
    print(f'{bot.user} is ready!')


@bot.event
async def on_guild_available(guild: discord.Guild):
    global data
    init_guild(guild.id)
    if guild.id == _MY_GUILD:
        await get_stats_line_emojis(guild)
    async for member in guild.fetch_members():
        if not member.bot:
            init_member(guild.id, member.id)


@bot.event
async def on_command_error(ctx: commands.Context, error: discord.DiscordException):
    if isinstance(error, NothingHere):
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'nothing_here')))
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'not_a_guild')))
    elif isinstance(error, MyCheckError):
        pass
    elif isinstance(error, commands.BadArgument):
        await ctx.message.add_reaction('❓')
    elif isinstance(error, commands.CheckFailure):
        await ctx.message.add_reaction('❓')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.add_reaction('❓')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction('❓')
    else:
        raise error


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    global data, question_numbers
    if not user.bot:
        guild = reaction.message.guild
        if guild is not None:
            guild_data = data.guilds[guild.id]
            user_data = guild_data.members[user.id]
            message_id = user_data.tests.ench.message_id
            school_id = guild_data.school_id
            if not (message_id is None or school_id is None):
                school = guild.get_channel(school_id)
                try:
                    message = await school.fetch_message(message_id)
                except discord.NotFound:
                    pass
                else:
                    if message == reaction.message:
                        emoji = str(reaction)
                        if emoji in question_numbers:
                            answer_index = question_numbers.index(emoji)
                            ench_data = user_data.tests.ench
                            correctness = answer_index == ench_data.questions[ench_data.index].answer_index
                            await answer_question(guild.id, user.id, message, correctness)
                        elif emoji in question_changers:
                            delta = 2 * question_changers.index(emoji) - 1
                            await change_question(guild.id, user.id, message, delta)


# COMMANDS


@bot.command()
@commands.is_owner()
async def kill(ctx):
    await ctx.send('Какой жестокий мир!\nОтключаюсь...')
    await my_logout()


@bot.command(name='lang')
@commands.has_permissions(manage_channels=True)
async def language(ctx: commands.Context, *, lang_: str = ''):
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


@bot.group(name='~')
@commands.has_permissions(manage_messages=True)
async def reacts(ctx: commands.Context, *reacts):
    global reactions
    msg_list = await ctx.channel.history(limit=1, before=ctx.message.created_at).flatten()
    msg = msg_list[0]
    reacts_list = []
    try_number = False
    react_type = None
    for i in reacts:
        if try_number:
            try_number = False
            if i.isdigit():
                for j in reactions[2][react_type][:int(i)]:
                    reacts_list.append(reactions[0][j])
                continue
        if i in reactions[0]:
            reacts_list.append(reactions[0][i])
        elif i in reactions[1]:
            for j in reactions[1][i]:
                reacts_list.append(reactions[0][j])
        elif i in reactions[2]:
            try_number = True
            react_type = i

    await fill_reactions(msg, reacts_list)
    await ctx.message.delete()


@bot.group(name='home')
@commands.has_permissions(manage_channels=True)
async def home_(ctx: commands.Context):
    global data
    if ctx.invoked_subcommand is None:
        guild_id = ctx.guild.id
        home_id = data.guilds[guild_id].home_id
        if home_id == ctx.channel.id:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'home_here')))
        elif home_id is not None:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'home_there'), {'home': f'<#{home_id}>'}))
        else:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_home')))


@home_.command(name='set')
@commands.has_permissions(manage_channels=True)
async def set_home(ctx: commands.Context, *, arg: str = ''):
    global data
    guild_id = ctx.guild.id
    home_id = data.guilds[guild_id].home_id
    if home_id == ctx.channel.id:
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'home_here_already')))
    else:
        games_count = count_games(guild_id)
        if games_count != 0 and arg != 'confirm':
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'sethome_warning'), {'games_count': games_count}))
        else:
            abort_games(guild_id)
            data.guilds[guild_id].home_id = ctx.channel.id
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'new_home')))


@home_.command(name='del')
@commands.has_permissions(manage_channels=True)
async def del_home(ctx: commands.Context, *, arg: str = ''):
    global data
    guild_id = ctx.guild.id
    home_id = data.guilds[guild_id].home_id
    if home_id is None:
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_home_yet')))
    else:
        games_count = count_games(guild_id)
        if games_count != 0 and arg != 'confirm':
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'delhome_warning'), {'games_count': games_count}))
        else:
            abort_games(guild_id)
            data.guilds[guild_id].home_id = None
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_home_now')))


@bot.group(name='school')
@commands.has_permissions(manage_channels=True)
async def school_(ctx: commands.Context):
    global data
    if ctx.invoked_subcommand is None:
        guild_id = ctx.guild.id
        school_id = data.guilds[guild_id].school_id
        if school_id == ctx.channel.id:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'school_here')))
        elif school_id is not None:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'school_there'), {'school': f'<#{school_id}>'}))
        else:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_school')))


@school_.command(name='set')
@commands.has_permissions(manage_channels=True)
async def set_school(ctx: commands.Context, *, arg: str = ''):
    global data
    guild_id = ctx.guild.id
    school_id = data.guilds[guild_id].school_id
    if school_id == ctx.channel.id:
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'school_here_already')))
    else:
        tests_count = count_tests(guild_id)
        if tests_count != 0 and arg != 'confirm':
            await ctx.send(
                translate(lang(ctx.guild.id), ('messages', 'setschool_warning'), {'tests_count': tests_count}))
        else:
            abort_tests(guild_id)
            data.guilds[guild_id].school_id = ctx.channel.id
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'new_school')))


@school_.command(name='del')
@commands.has_permissions(manage_channels=True)
async def del_school(ctx: commands.Context, *, arg: str = ''):
    global data
    guild_id = ctx.guild.id
    school_id = data.guilds[guild_id].school_id
    if school_id is None:
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_school_yet')))
    else:
        tests_count = count_tests(guild_id)
        if tests_count != 0 and arg != 'confirm':
            await ctx.send(
                translate(lang(ctx.guild.id), ('messages', 'delschool_warning'), {'tests_count': tests_count}))
        else:
            abort_tests(guild_id)
            data.guilds[guild_id].school_id = None
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'no_school_now')))


@bot.command()
async def say(ctx: commands.Context, *, arg: str = ''):
    if not arg or arg == 'list':
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'messages_list'), dict(list=", ".join(msgs))))
    elif arg in msgs:
        try:
            await ctx.send(msgs[arg])
        except FileNotFoundError:
            await ctx.send(FILE_NOT_FOUND.format(msgs[arg]))


@bot.command()
async def image(ctx: commands.Context, *, arg: str = ''):
    if not arg or arg == 'list':
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'images_list'), dict(list=", ".join(imgs))))
    elif arg in imgs:
        try:
            await ctx.send(file=discord.File('images/' + imgs[arg]))
        except FileNotFoundError:
            await ctx.send(FILE_NOT_FOUND.format(imgs[arg]))


@bot.command()
async def sound(ctx: commands.Context, *, arg: str = ''):
    if not arg or arg == 'list':
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'sounds_list'), dict(list=", ".join(snds))))
    elif arg in snds:
        try:
            await ctx.send(file=discord.File('sounds/' + snds[arg]))
        except FileNotFoundError:
            await ctx.send(FILE_NOT_FOUND.format(snds[arg]))


# noinspection PyUnreachableCode
@bot.group()
@commands.guild_only()
async def play(ctx: commands.Context, *, arg: str = ''):  # todo
    #raise NothingHere
    if not arg or arg == 'list':
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'games_list'), dict(list=", ".join(games))))
    else:
        homes = data.guilds['homes']
        guild = ctx.guild.id
        if guild in homes:
            home = homes[guild]
            if home == ctx.channel.id:
                # TODO games
                pass
            else:
                await ctx.send(translate(lang(ctx.guild.id), ('messages', 'go_home')))
        else:
            await ctx.send(translate(lang(ctx.guild.id), ('messages', 'need_home')))


@bot.group()
@commands.guild_only()
async def test(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        if ctx.subcommand_passed:
            raise commands.BadArgument(NO_SUBCOMMAND)
        else:
            await list_(ctx)


@test.command(name='list')
async def list_(ctx: commands.Context):
    await ctx.send(translate(lang(ctx.guild.id), ('messages', 'tests_list'), dict(list=", ".join(tests))))


@test.command(name='finish')
@is_testing()
async def ench_finish(ctx: commands.Context):
    await finish_ench(ctx.guild.id, ctx.author.id)


@test.command(name='resume')
@is_testing()
async def resume_ench(ctx: commands.Context):
    global data
    guild_id = ctx.guild.id
    member_id = ctx.author.id
    school = ctx.guild.get_channel(data.guilds[guild_id].school_id)
    ench_data = data.guilds[guild_id].members[member_id].tests.ench
    last_msg_id = ench_data.message_id
    try:
        last_message = await school.fetch_message(last_msg_id)
        await last_message.delete()
    except discord.NotFound:
        pass
    await print_question(guild_id, member_id)


@test.command(name='stats')
async def ench_stats(ctx: commands.Context):
    raise NothingHere


@test.group()
@in_guild_school()
async def start(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        raise commands.BadArgument(NO_SUBCOMMAND)


@start.command(name='ench')
@is_not_testing()
async def start_ench(ctx: commands.Context, count: int = 1):
    global data
    if count > ENCH_TEST_MAX_QUESTIONS_COUNT:
        await ctx.send(translate(lang(ctx.guild.id), ('messages', 'too_many_questions'),
                                 {'count': ENCH_TEST_MAX_QUESTIONS_COUNT}))
    elif count <= 0:
        raise commands.BadArgument
    else:
        tests_data = data.guilds[ctx.guild.id].members[ctx.author.id].tests
        tests_data.active = True
        ench_data = tests_data.ench
        questions = []
        if count != 1:
            ench_data.some_questions = True
            for i in range(1, count + 1):
                questions.append(Question(ctx.guild.id, i))
        else:
            ench_data.some_questions = False
            questions.append(Question(ctx.guild.id, 0))
        ench_data.questions = questions
        ench_data.index = 0
        ench_data.questions_loop = False
        ench_data.some_questions = count != 1
        ench_data.stats = EnchStatsData(len(questions))
        await print_question(ctx.guild.id, ctx.author.id)


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


if __name__ == '__main__':

    set_logging(log)

    data: GlobalData = load_data('data')

    ench_test_data = load_ench_data()

    guild_data_dict = GuildData().__dict__
    member_data_dict = MemberData().__dict__

    lang_dict = {}
    for elem in lang_list:
        lang_dict[elem] = load_lang(elem)

    ench_tests = list(lang_dict[DEFAULT_LANG]['ench']['questions'])

    with open('token.txt') as token:
        bot.run(token.readline())
