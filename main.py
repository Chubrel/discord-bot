#! python
# coding=utf-8
"""Chubaka bot"""

import discord
from discord.ext import commands
import logging
import pickle

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

msgs = {'hello': 'Дратути!'}
imgs = {'bedy': 'bedy_s_bashkoj.jpg'}
snds = {'blya': 'blyat_chto.ogg', 'izv': 'izvinite.ogg', 'bat': 'batyushki.ogg', 'uzh': 'uzhas.ogg',
        'nah': 'poshyol_nahuj.ogg', 'logo': 'bananana.ogg', 'logo1': 'banananana.ogg'}
games = {'numb': 'guessing_number.py', 'b&c': 'bulls_and_cows.py', 'stones': 'stones.py'}
tests = {'ench': ''}

fileNotFound = 'Ошибка: файл **{}** не найден.'


def load_data(file_name):
    try:
        with open(file_name, 'rb') as db:
            data_ = pickle.load(db)
    except (FileNotFoundError, pickle.UnpicklingError):
        print(f'Не удалось считать данные из файла "{file_name}".')
        data_ = {'homes': {}, 'games': {}, 'tests': {}}
    return data_


def save_data(data_):
    with open('data', 'wb') as db_:
        pickle.dump(data_, db_)


class IntConvert(commands.Converter):
    async def convert(self, ctx, argument):
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


data = load_data('data')
bot = commands.Bot(command_prefix='&')


async def mylogout():
    save_data(data)
    await bot.logout()


@bot.event
async def on_ready():
    print(f'{bot.user} готов!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        # await ctx.channel.send(f'Не могу понять введённую команду:\n"{ctx.message}"')
        ctx.message.add_reaction('❓')
    elif isinstance(error, commands.CheckFailure):
        # await ctx.channel.send(f'У вас недостататочно прав, чтобы выполнить команду:\n"{ctx.message}"')
        ctx.message.add_reaction('❓')


@bot.command()
@commands.is_owner()
async def kill(ctx):
    await ctx.channel.send('Какой жестокий мир!\nОтключаюсь...')
    await mylogout()


@kill.error
async def kill_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.channel.send(file=discord.File('sounds/poshyol_nahuj.ogg', 'kill.ogg'))


@bot.command()
async def sethome(ctx):
    home = data['homes'].get(ctx.guild.id)
    if home == ctx.channel.id:
        await ctx.channel.send('Мой дом уже находится в этом канале.')
    else:
        data['homes'][ctx.guild.id] = ctx.channel.id
        await ctx.channel.send('Ура! Теперь у меня есть дом в этом канале. 🏠')


@bot.command(name='home')
async def home_(ctx):
    home = data['homes'].get(ctx.guild.id)
    if home == ctx.channel.id:
        await ctx.channel.send('Мой дом находится в этом канале.')
    elif home is not None:
        await ctx.channel.send(f'Мой дом находится в канале <#{home}>')
    else:
        await ctx.channel.send('Здесь у меня ещё нет дома. 😕')


@bot.command()
async def delhome(ctx):
    home = data['homes'].pop(ctx.guild.id, None)
    if home is not None:
        await ctx.channel.send('Теперь я бездомный. 😟')
    else:
        await ctx.channel.send('У меня и так не дома. 😭')


@bot.command()
async def say(ctx, arg):
    if arg == 'list':
        await ctx.channel.send(f'Список всех сообщений: {", ".join(msgs)}.')
    elif arg in msgs:
        try:
            await ctx.channel.send(msgs[arg])
        except FileNotFoundError:
            await ctx.channel.send(fileNotFound.format(msgs[arg]))


@bot.command()
async def image(ctx, arg):
    if arg == 'list':
        await ctx.channel.send(f'Список всех картинок: {", ".join(imgs)}.')
    elif arg in imgs:
        try:
            await ctx.channel.send(file=discord.File('images/' + imgs[arg]))
        except FileNotFoundError:
            await ctx.channel.send(fileNotFound.format(imgs[arg]))


@bot.command()
async def sound(ctx, arg):
    if arg == 'list':
        await ctx.channel.send(f'Список всех звукозаписей: {", ".join(snds)}.')
    elif arg in snds:
        try:
            await ctx.channel.send(file=discord.File('sounds/' + snds[arg]))
        except FileNotFoundError:
            await ctx.channel.send(fileNotFound.format(snds[arg]))


@bot.command()
async def play(ctx, arg):
    if arg == 'list':
        await ctx.channel.send(f'Список всех игр: {", ".join(games)}.')
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
                await ctx.channel.send('Ты же не хочешь устроить здесь погром?',
                                       'Давай лучше играть у меня дома! 😉')
        else:
            await ctx.channel.send('Мне нужен дом, чтобы мы могли сыграть!')


@bot.group()
async def test(ctx):
    if ctx.invoked_subcommand is None:
        raise commands.BadArgument('Нет субкоманды')


@test.command(name='list')
async def list_(ctx):
    await ctx.channel.send(f'Список всех тестов: {", ".join(tests)}.')


@test.command()
async def get(ctx, arg, n: IntConvert = 1):
    home = data['homes'].get(ctx.guild.id)
    if home is None:
        await ctx.channel.send('Мне нужен дом, чтобы мы могли сыграть!')
    elif home != ctx.channel.id:
        await ctx.channel.send('Ты же не хочешь устроить здесь погром?',
                               'Давай лучше играть у меня дома! 😉')
    else:
        with home.typing():
            if arg == 'ench':
                pass


@test.command()
async def ans(ctx, *arg):
    pass


@test.command()
async def finish(ctx):
    pass


with open('token.txt') as token:
    bot.run(token.readline())
