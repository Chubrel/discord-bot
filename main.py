#! python
# coding=utf-8
"""Chubaka bot"""

import logging
import pickle
import json
from random import choice, sample
from string import Template
import discord
from discord.ext import commands
from tasks import ench

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

msgs = {'hello': 'Дратути!'}
imgs = {'bedy': 'bedy_s_bashkoj.jpg'}
snds = {'blya': 'blyat_chto.ogg', 'izv': 'izvinite.ogg', 'bat': 'batyushki.ogg', 'uzh': 'uzhas.ogg',
        'nah': 'poshyol_nahuj.ogg', 'logo': 'bananana.ogg', 'logo1': 'banananana.ogg'}
games = ['numb', 'b&c', 'stones']
tests = ['ench']
langs = ['ru_ru', 'en_us']

DEFAULT_LANG = 'en_us'

FILE_NOT_FOUND = "File not found: '{}'"
NO_SUBCOMMAND = 'No subcommand'
CANNOT_READ = "Can't read data from '{}'"

MAX_SPACES = 8
MAX_NAME_LEN = 40

def load_data(file_name: str) -> dict:
    try:
        with open(file_name, 'rb') as db:
            data_ = pickle.load(db)
    except (FileNotFoundError, pickle.UnpicklingError):
        print(CANNOT_READ.format(file_name))
        data_ = {}
    return data_


def save_data(data_: dict) -> None:
    with open('data', 'wb') as db_:
        pickle.dump(data_, db_)


def load_lang(name: str) -> dict:
    try:
        with open(f'langs/{name}.json', encoding='utf-8') as lang_file:
            return json.load(lang_file)
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError(CANNOT_READ.format(f'langs/{name}.json'))


def init_guild(guild_id: int, lang: str = DEFAULT_LANG, extra_langs: set = None,
               home: int = None, school: int = None, activities: dict = None) -> None:
    global data
    if guild_id not in data:
        if activities is None:
            activities = {}
        if extra_langs is None:
            extra_langs = {DEFAULT_LANG}
        data[guild_id] = {'lang': lang, 'extra_langs': extra_langs,
                          'home': home, 'school': school, 'activities': activities}


def count_activities(guild_id: int, activity: str) -> int:
    global data
    if activity not in ('game', 'test'):
        raise ValueError("activity not in ('game', 'test')")
    count = 0
    for user_data in data[guild_id]['activities'].values():
        if user_data.get(activity) is not None:
            count += 1
    return count


def abort_activities(guild_id: int, activity: str) -> None:
    global data
    if activity not in ('game', 'test'):
        raise ValueError("activity not in ('game', 'test')")
    activities = data[guild_id]['activities']
    for user_id in activities:
        if activities[user_id].get(activity) is not None:
            del activities[user_id][activity]


def get_options(path: tuple) -> list:
    global lang
    opt = lang[DEFAULT_LANG]
    for el in path:
        opt = opt[el]
    return list(opt.keys())


def phrase(guild_id: int, lang_path: tuple, replace_dict: dict = None, rand: bool = False) -> str:
    global lang, data
    # init_guild(guild_id)
    lang_name = data[guild_id]['langs']
    phras = lang[lang_name]
    for el in lang_path:
        phras = phras[el]
    if rand:
        phras = choice(phras)
    if replace_dict is not None:
        phras = Template(phras).safe_substitute(replace_dict)
    return phras.replace('\\n', '\n')


def normalize(guild_id: int, old_str: str) -> str:
    global data, lang
    norm_str = ''
    for letter in old_str:
        if letter.isalpha() or letter.isspace():
            norm_str += letter
    for i in data[guild_id]['extra_langs']:
        for k, v in lang[i]['normalize'].items():
            norm_str.replace(k, v)
    return norm_str.lower()


def errors_count(s1: str, s2: str) -> int:
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
    return m[ls1][ls2]


ench_tests = get_options(('ench', 'questions'))
ench_enchs = get_options(('ench', 'enchantments'))
ench_items = get_options(('ench', 'items'))

data = load_data('data')

lang = {}
for elem in langs:
    lang[elem] = load_lang(elem)

bot = commands.Bot(command_prefix='&')


# ENCH START


class Answer:

    def __init__(self, list_: tuple, types: tuple):
        self.list = list_
        self.types = types

    def save(self):
        pass


class Reply:

    def __init__(self, guild_id: int, user_id: int, raw_str: str):
        self.raw = normalize(guild_id, raw_str).split()
        self.guild_id = guild_id
        #self.answer = data[guild_id]['activities'][user_id]['test']

    def compare(self, answer: Answer):
        pass

    def similar(self, string: str) -> str:
        global lang, data
        raw_str = self.raw_str
        len_raw = len(raw_str)
        len_str = len(string)
        max_error = max(len_str // 2 - 1, 0)
        pass_limit = max(len_str // 3 - 1, 0)

        for lang_name in data[self.guild_id]['extra_langs']:
            lang[lang_name]['ench']['enchantments'][]
            err_id = self.similar(ench_name)

        if abs(len_raw - len_str) <= max_error:
            err_count = self.errors_count(string.lower())
            if err_count <= pass_limit:
                return 2
            elif err_count <= max_error:
                return 1
            return 0

    def ench_parse(self) -> str:
        global lang, data
        if err_id == 2:
            return
        elif err_id == 1:
            return
        return

    def item_parse(self) -> str:
        pass

    def max_ench_lvl(self):
        pass


    def int_parse(self) -> int:
        if argument.isnumeric():
            return int(argument)
        else:
            trans_roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
            try:
                arabic = [trans_roman[i] for i in argument.upper()]
            except KeyError:
                raise commands.BadArgument
            i = 1
            while i < len(arabic):
                if arabic[i - 1] < arabic[i]:
                    arabic[i - 1] = -arabic[i - 1]
                    i += 2
                else:
                    i += 1
            return sum(arabic)


class Response:

    def __init__(self, reply: str):
        self.reply = reply


# ENCH END


async def my_logout():
    save_data(data)
    await bot.logout()


@bot.event
async def on_ready():
    print(f'{bot.user} is ready!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        # await ctx.channel.send(f'Не могу понять введённую команду:\n"{ctx.message}"')
        await ctx.message.add_reaction('❓')
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'not_a_guild')))
    elif isinstance(error, commands.CheckFailure):
        # await ctx.channel.send(f'У вас недостататочно прав, чтобы выполнить команду:\n"{ctx.message}"')
        await ctx.message.add_reaction('❓')


@bot.command()
@commands.is_owner()
async def kill(ctx):
    await ctx.channel.send('Какой жестокий мир!\nОтключаюсь...')
    await my_logout()


@kill.error
async def kill_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.channel.send(file=discord.File('sounds/poshyol_nahuj.ogg', 'kill.ogg'))


@bot.command()
async def see(ctx):
    await ctx.message.add_reaction('👁')


@bot.group(name='home')
@commands.guild_only()
async def home_(ctx):
    if ctx.invoked_subcommand is None:
        guild_id = ctx.guild.id
        init_guild(guild_id)
        home = data[guild_id]['home']
        if home == ctx.channel.id:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'home_here')))
        elif home is not None:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'home_there'), {'home': f'<#{home}>'}))
        else:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'no_home')))


@home_.command(name='set')
@commands.has_permissions(manage_messages=True)
async def set_home(ctx, arg):
    guild_id = ctx.guild.id
    init_guild(guild_id)
    home = data[guild_id]['home']
    if home == ctx.channel.id:
        await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'home_here_already')))
    else:
        games_count = count_activities(guild_id, 'game')
        if games_count != 0 and arg != 'confirm':
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'sethome_warning'), {'games_count': games_count}))
        else:
            abort_activities(guild_id, 'game')
            data[guild_id]['home'] = ctx.channel.id
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'new_home')))


@home_.command(name='del')
@commands.has_permissions(manage_messages=True)
async def del_home(ctx, arg):
    guild_id = ctx.guild.id
    init_guild(guild_id)
    home = data[guild_id]['home']
    if home is None:
        await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'no_home_yet')))
    else:
        games_count = count_activities(guild_id, 'game')
        if games_count != 0 and arg != 'confirm':
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'delhome_warning'), {'games_count': games_count}))
        else:
            abort_activities(guild_id, 'game')
            data[guild_id]['home'] = None
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'no_home_now')))


@bot.group(name='school')
@commands.guild_only()
async def school_(ctx):
    if ctx.invoked_subcommand is None:
        guild_id = ctx.guild.id
        init_guild(guild_id)
        school = data[guild_id].get('school')
        if school == ctx.channel.id:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'school_here')))
        elif school is not None:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'school_there'), {'school': f'<#{school}>'}))
        else:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'no_school')))


@school_.command(name='set')
@commands.has_permissions(manage_messages=True)
async def set_school(ctx, arg):
    guild_id = ctx.guild.id
    init_guild(guild_id)
    school = data[guild_id]['school']
    if school == ctx.channel.id:
        await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'school_here_already')))
    else:
        tests_count = count_activities(guild_id, 'test')
        if tests_count != 0 and arg != 'confirm':
            await ctx.channel.send(
                phrase(ctx.guild.id, ('messages', 'setschool_warning'), {'tests_count': tests_count}))
        else:
            abort_activities(guild_id, 'test')
            data[guild_id]['school'] = ctx.channel.id
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'new_school')))


@school_.command(name='del')
@commands.has_permissions(manage_messages=True)
async def del_school(ctx, arg):
    guild_id = ctx.guild.id
    init_guild(guild_id)
    school = data[guild_id]['school']
    if school is None:
        await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'no_school_yet')))
    else:
        tests_count = count_activities(guild_id, 'test')
        if tests_count != 0 and arg != 'confirm':
            await ctx.channel.send(
                phrase(ctx.guild.id, ('messages', 'delschool_warning'), {'tests_count': tests_count}))
        else:
            abort_activities(guild_id, 'test')
            data[guild_id]['school'] = None
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'no_school_now')))


@bot.command()
async def say(ctx, arg):
    if arg == 'list':
        await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'messages_list'), dict(list=f'{", ".join(msgs)}.')))
    elif arg in msgs:
        try:
            await ctx.channel.send(msgs[arg])
        except FileNotFoundError:
            await ctx.channel.send(FILE_NOT_FOUND.format(msgs[arg]))


@bot.command()
async def image(ctx, arg):
    if arg == 'list':
        await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'images_list'), dict(list=f'{", ".join(imgs)}.')))
    elif arg in imgs:
        try:
            await ctx.channel.send(file=discord.File('images/' + imgs[arg]))
        except FileNotFoundError:
            await ctx.channel.send(FILE_NOT_FOUND.format(imgs[arg]))


@bot.command()
async def sound(ctx, arg):
    if arg == 'list':
        await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'sounds_list'), dict(list=f'{", ".join(snds)}.')))
    elif arg in snds:
        try:
            await ctx.channel.send(file=discord.File('sounds/' + snds[arg]))
        except FileNotFoundError:
            await ctx.channel.send(FILE_NOT_FOUND.format(snds[arg]))


@bot.group()
@commands.guild_only()
async def play(ctx, arg):
    if arg == 'list':
        await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'games_list'), dict(list=f'{", ".join(games)}.')))
    else:
        homes = data['homes']
        guild = ctx.guild.id
        if guild in homes:
            home = homes[guild]
            if home == ctx.channel.id:
                with home.typing():
                    # TODO games
                    pass
            else:
                await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'go_home')))
        else:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'need_home')))


@bot.group()
@commands.guild_only()
async def test(ctx):
    if ctx.invoked_subcommand is None:
        raise commands.BadArgument(NO_SUBCOMMAND)


@test.command(name='list')
async def list_(ctx):
    await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'tests_list'), dict(list=f'{", ".join(tests)}.')))


def in_guild_home():
    async def predicate(ctx):
        home = data['homes'].get(ctx.guild.id)
        if home is None:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'go_to_school')))
            return False
        elif home != ctx.channel.id:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'need_school')))
            return False
        return True

    return commands.check(predicate)


def in_guild_school():
    async def predicate(ctx):
        school = data['school'].get(ctx.guild.id)
        if school is None:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'go_to_school')))
            return False
        elif school != ctx.channel.id:
            await ctx.channel.send(phrase(ctx.guild.id, ('messages', 'need_school')))
            return False
        return True

    return commands.check(predicate)


@test.group()
@in_guild_school()
async def start(ctx):
    if ctx.invoked_subcommand is None:
        raise commands.BadArgument(NO_SUBCOMMAND)


@start.command(name='ench')
async def ench_start(ctx, n: int):
    question = choice(ench_tests)
    async with ctx.channel.typing():
        pass


@test.command()
async def ans(ctx, *arg):
    pass


@test.command(name='finish')
async def ench_finish(ctx):
    pass


if __name__ == '__main__':
    with open('token.txt') as token:
        bot.run(token.readline())
