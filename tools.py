#! python
# coding=utf-8


import re
from datetime import datetime, timedelta
from random import choice, sample
from string import Template

from errors import *
from data_classes import *


# CONSTANTS


MAX_STATS_LINE_LENGTH = 20
MY_GUILD = 671035889174183941
MY_ID = 711806909908385802
REACTION_LETTER = ord('🇦') - ord('a')

stats_line_emojis = ['line_small', 'line_left', 'line_middle', 'line_right']

COLORS = {'red': 13369344, 'green': 52224, 'blue': 3368652, 'yellow': 13408512, 'black': 3355443, 'white': 13421772,
          'orange': 13395456,
          'limonchik': 16640272, 'chubrel': 6225811}

MESSAGES = {'hello': 'Дратути!'}

IMAGES = {'bedy': 'https://cdn.discordapp.com/attachments/800634568356134922/803033539468722206/bedy_s_bashkoj.jpg',
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
          'house': 'https://cdn.discordapp.com/attachments/802531716085973003/803010693912985630/unknown.png',
          'bot': 'https://cdn.discordapp.com/attachments/800634568356134922/807613944281301042/bot.jpg',
          'yorsh': 'https://cdn.discordapp.com/attachments/800634568356134922/807613952254672937/yorshik.jpg',
          'akva': 'https://cdn.discordapp.com/attachments/800634568356134922/807613948341256242/aqua_disco.jpg'}

SOUNDS = {'blya': 'blyat_chto.ogg',
          'izv': 'izvinite.ogg',
          'bat': 'batyushki.ogg',
          'uzh': 'uzhas.ogg',
          'nah': 'poshyol_nahuj.ogg',
          'logo': 'bananana.ogg',
          'logo1': 'banananana.ogg',
          '56k': '56k.ogg',
          'clown': 'clown.ogg',
          'deeper': 'deeper.ogg',
          'guarantee': 'guarantee.ogg',
          'horn': 'horn.ogg',
          'letitgo': 'letitgo.ogg',
          'noooo': 'noooo.ogg',
          'nyan': 'nyan.ogg',
          'ohmy': 'ohmy.ogg',
          'rumble': 'rumble.ogg',
          'story': 'story.ogg',
          'tada': 'tada.ogg',
          'trololo': 'trololo.ogg',
          'trombone': 'trombone.ogg',
          'wups': 'wups.ogg',
          'f': 'f.ogg',
          'empty': 'empty.ogg',
          'tem': 'tem.ogg'
          }

REACTS = ({'look': '👀', 'up': '👍', 'down': '👎', 'check': '✅', 'cross': '❌', 'think': '🤔', 'question': '❔',
               'info': 'ℹ️', 'ok': '🆗', 'speak': '💬', 'warn': '⚠️', '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣',
               '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣', '10': '🔟', 'bs': '🟦'},
          {'vote': ('up', 'down'), 'ivote': ('check', 'cross'), 'blue_square': ('bs',)},
          ('numvote',),
          ('word',))


# FUNCTIONS


def get_stats_line(length: int) -> str:
    global bot, stats_line_emojis
    if length == 1:
        line = stats_line_emojis[0]
    else:
        line = stats_line_emojis[1] + (length - 2) * stats_line_emojis[2] + stats_line_emojis[3]
    return line


def get_proportional_lines(*weights) -> list:
    total = sum(weights)
    if total == 0:
        total = 1
    return [get_stats_line(int(MAX_STATS_LINE_LENGTH * i / total - 0.001) + 1) for i in weights]


def formatted_results(counts: list[int], strings: list[str]) -> tuple:
    total = sum(counts)
    if not total:
        total = 1
    lines = get_proportional_lines(*counts)
    values = [f'{string}  {count}  ({round(100 * count / total, 1)}%)' for string, count in zip(strings, counts)]
    return values, lines


def get_stats_lines(*counts) -> list:
    total = sum(counts)
    if not total:
        total = 1
    lines = get_proportional_lines(*counts)
    values = [f'{line} • {count} • {round(100 * count / total, 1)}%' for line, count in zip(lines, counts)]
    return values


async def get_stats_line_emojis(guild) -> None:
    global stats_line_emojis
    emojis = await guild.fetch_emojis()
    for i in range(len(stats_line_emojis)):
        for e in emojis:
            if stats_line_emojis[i] == e.name:
                stats_line_emojis[i] = str(e)


async def add_reactions(message: discord.Message, reactions: iter) -> None:
    for reaction in reactions:
        await message.add_reaction(reaction)


async def fill_reactions(message: discord.Message, reactions: iter) -> None:
    await message.clear_reactions()
    await add_reactions(message, reactions)


def numvote_list(number: int) -> list:
    global REACTS
    if number > 10:
        number = 10
    elif number < 1:
        return []
    return [REACTS[0][str(i)] for i in range(1, int(number) + 1)]


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
    if channel is None:
        channel = await bot.fetch_channel(args[-2])
        if channel is None:
            raise AttributeError(f'No channel with args {args}')
    return await channel.fetch_message(args[-1])


async def get_dm_channel(user: discord.User) -> discord.DMChannel:
    channel = user.dm_channel
    if channel is None:
        channel = await user.create_dm()
    return channel


def get_embed_dict_with_placeholders(json_text: str) -> dict:
    json_text = Placeholder(json_text).parsed
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


async def handle_error(error, message: discord.Message):
    channel = message.channel
    guild = message.guild
    if guild is None:
        lang_id = message.author.id
    else:
        lang_id = guild.id
    if isinstance(error, PassCheckError):
        pass
    elif isinstance(error, PassArgumentError):
        pass
    elif isinstance(error, NothingHere):
        await message.channel.send(Translate(lang_id, ('messages', 'common', 'nothing_here')).string())
    elif isinstance(error, TranslationFail):
        print(error)
    elif isinstance(error, commands.NoPrivateMessage):
        await channel.send(Translate(lang_id, ('messages', 'common', 'not_a_guild')).string())
    elif isinstance(error, BadJSON):
        error_msg = error.args[0]
        await channel.send(
            Translate(lang_id, ('messages', 'common', 'bad_json'), {'json_error': error_msg}).string())
    elif isinstance(error, BadPlaceholder):
        error_msg = error.args[0]
        await channel.send(Translate(lang_id, ('messages', 'common', 'bad_placeholder'),
                                     {'placeholder': error_msg}).string())
    elif isinstance(error, DontUnderstand):
        error_msg = error.args[0]
        await channel.send(
            Translate(lang_id, ('messages', 'common', 'dont_understand'), {'text': error_msg}).string())
    elif isinstance(error, PlayersRepeat):
        await channel.send(Translate(lang_id, ('messages', 'common', 'players_repeat')).string())
    elif isinstance(error, PlayerNotInParty):
        error_msg = error.args[0]
        await channel.send(Translate(lang_id, ('messages', 'common', 'player_not_in_party'),
                                     {'player': error_msg}).string())
    elif isinstance(error, BallotNotFound):
        await channel.send(Translate(lang_id, ('messages', 'ballots', 'not_found')).string())
    elif isinstance(error, commands.BadArgument):
        await message.add_reaction('❓')
    elif isinstance(error, commands.CheckFailure):
        await message.add_reaction('❓')
    elif isinstance(error, commands.MissingRequiredArgument):
        await message.add_reaction('❓')
    elif isinstance(error, commands.CommandNotFound):
        await message.add_reaction('❓')
    else:
        raise error


# CLASSES


class Translate:

    def __init__(self, lang: Union[str, int], lang_path: Union[str, tuple], replace_dict: dict = None):

        if isinstance(lang, int):
            lang_name = self.guild_lang(lang)
            if lang_name is None:
                lang_name = self.user_lang(lang)
        else:
            lang_name = lang

        self.lang_name: str = lang_name

        if isinstance(lang_path, str):
            str_path = lang_path
            path = tuple(lang_path.split('.'))
        else:
            str_path = '.'.join(lang_path)
            path = lang_path

        self.str_path: str = str_path
        self.path: tuple = path

        self.replace_dict: dict = replace_dict
        self.translation: Optional[list, str] = None

    def string(self) -> str:
        if self.translation is None:
            self.translate()
        self.translation: Union[list, str]
        if isinstance(self.translation, str):
            return self.translation
        try:
            string = choice(self.translation)
            return string
        except (TypeError, KeyError):
            pass
        raise TranslationFail(self.lang_name, self.str_path)

    def list(self, randomize: int = 1) -> list:
        if self.translation is None:
            self.translate()
        self.translation: Union[list, str]
        if isinstance(self.translation, str):
            if randomize <= 1:
                return [self.translation]
        else:
            try:
                if len(self.translation) <= randomize:
                    if randomize > 0:
                        return sample(self.translation, randomize)
                    else:
                        return self.translation
            except TypeError:
                pass
        raise TranslationFail(self.lang_name, self.str_path)

    @classmethod
    def guild_lang(cls, guild_id: int) -> Optional[str]:
        global data
        guild_data = data.guilds.get(guild_id)
        if guild_data is not None:
            return guild_data.lang
        return None

    @classmethod
    def user_lang(cls, user_id: int) -> Optional[str]:
        global data
        user_data = data.users.get(user_id)
        if user_data is not None:
            return user_data.lang
        return None

    def translate(self):
        global lang_dict, data
        phrase = lang_dict[self.lang_name]
        try:
            for el in self.path:
                phrase = phrase[el]
        except KeyError:
            raise TranslationFail(self.lang_name, self.str_path)
        if self.replace_dict is not None:
            # .replace('\\n', '\n')
            phrase = Template(phrase).safe_substitute(self.replace_dict)
        self.translation = phrase

    def __str__(self):
        return self.string()


class Placeholder:
    RE_PATTERN = '<~.*?>+'
    RE_PATTERN_EXACT = '<~[^~]*?>+'

    def __init__(self, text: str):
        self._text: str = text

    @property
    def parsed(self) -> str:
        return self._parse_text_with_placeholders()

    def _parse_text_with_placeholders(self):
        text = self._text
        r = re.findall(Placeholder.RE_PATTERN, text)
        for string in r:
            text = text.replace(string, self._parse_placeholder(string))
        return text

    def _parse_placeholder(self, string: str) -> str:
        if string[2] == '~':
            return string[:2] + string[3:]
        string = string.lower()
        p = string[2:-1].split(':', 1)
        if len(p) == 2:
            p = [i.strip() for i in p]
            ph_type = p[0]
            if ph_type == 'image':
                image_url = IMAGES.get(p[1].replace(' ', '_'))
                if image_url is not None:
                    return f'"{image_url}"'
            elif ph_type == 'react':
                reacts = p[1].split()
                return ' '.join(self.parse_reacts(reacts))
        raise BadPlaceholder(string)

    @classmethod
    def parse_reacts(cls, reacts: iter) -> list:
        global REACTS
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
                        reacts_list.append(REACTS[0]['bs'])
            elif i in REACTS[0]:
                reacts_list.append(REACTS[0][i])
            elif i in REACTS[1]:
                for j in REACTS[1][i]:
                    reacts_list.append(REACTS[0][j])
            elif i in REACTS[2]:
                try_number = True
            elif i in REACTS[3]:
                try_word = True
        return reacts_list

    @property
    def is_placeholder(self) -> bool:
        return bool(re.fullmatch(Placeholder.RE_PATTERN_EXACT, self._text))

    @property
    def has_placeholder(self) -> bool:
        return bool(re.search(Placeholder.RE_PATTERN_EXACT, self._text))

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str):
        placeholder = Placeholder(argument)
        if placeholder.is_placeholder:
            return placeholder
        raise commands.BadArgument(argument)


class MyEmojiConverter(commands.Converter):

    async def convert(self, ctx, argument) -> str:
        print(2)
        return MyEmojiConverter.parse(argument)

    @classmethod
    def parse(cls, arg: str) -> str:
        global discord_emojis
        if arg in discord_emojis:
            print(3)
            return arg
        print(4)
        raise commands.BadArgument


class EveryEmojiConverter(commands.EmojiConverter, MyEmojiConverter):

    async def convert(self, ctx, argument) -> str:
        thing = None

        for cls in self.__class__.__bases__:
            try:
                thing = await cls().convert(ctx, argument)
            except commands.BadArgument:
                pass
            else:
                break

        if thing is None:
            raise commands.BadArgument

        if isinstance(thing, str):
            return thing
        else:
            return str(thing)


class EmojiMultiConverter(commands.EmojiConverter, MyEmojiConverter, Placeholder):

    async def convert(self, ctx, argument) -> tuple[str]:
        thing: Union[commands.EmojiConverter, MyEmojiConverter, Placeholder, None] = None

        for cls in self.__class__.__bases__:
            try:
                print(cls, argument)
                thing = await cls().convert(ctx, argument)
            except commands.BadArgument:
                pass
            else:
                break

        if thing is None:
            print(1)
            raise commands.BadArgument

        if isinstance(thing, str):
            return thing,
        elif isinstance(thing, discord.Emoji):
            return str(thing),
        else:
            return tuple(thing.parsed.split())


class ISOFormatConverter(commands.Converter):

    async def convert(self, ctx, argument) -> datetime:
        return ISOFormatConverter.parse(argument)

    @classmethod
    def parse(cls, arg) -> datetime:
        try:
            #  example: '2011-11-04T00:05:23+04:00'
            return datetime.fromisoformat(arg)
        except ValueError:
            raise commands.BadArgument


class Checks:

    @classmethod
    def in_guild_home(cls):
        global data

        async def predicate(ctx: commands.Context):
            home_ids = data.guilds[ctx.guild.id].home_ids
            if not home_ids:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'homes', 'need')).string())
                raise PassCheckError
            elif ctx.channel.id not in home_ids:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'homes', 'go_to')).string())
                raise PassCheckError
            return True

        return commands.check(predicate)

    @classmethod
    def in_guild_school(cls):
        global data

        async def predicate(ctx: commands.Context):
            school_ids = data.guilds[ctx.guild.id].school_ids
            if not school_ids:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'schools', 'need')).string())
                raise PassCheckError
            elif ctx.channel.id not in school_ids:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'schools', 'go_to')).string())
                raise PassCheckError
            return True

        return commands.check(predicate)

    @classmethod
    def is_playing(cls, game=None):
        global data

        async def predicate(ctx: commands.Context):
            active = data.guilds[ctx.guild.id].members[ctx.author.id].games.active
            if game is None and active == '':
                await ctx.send(Translate(ctx.guild.id, ('messages', 'games', 'not_playing')).string())
                raise PassCheckError
            elif active != game and game:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'games', 'not_that'), {'game': game}).string())
                raise PassCheckError
            elif game == '' != active:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'games', 'playing_yet')).string())
                raise PassCheckError
            return True

        return commands.check(predicate)

    @classmethod
    def is_testing(cls, test=None):
        global data

        async def predicate(ctx: commands.Context):
            active = data.guilds[ctx.guild.id].members[ctx.author.id].tests.active
            if test is None and active != '':
                await ctx.send(Translate(ctx.guild.id, ('messages', 'tests', 'not_testing')).string())
                raise PassCheckError
            elif active != test != '':
                await ctx.send(Translate(ctx.guild.id, ('messages', 'tests', 'not_that'), {'test': test}).string())
                raise PassCheckError
            elif test == '' != active:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'tests', 'testing_yet')).string())
                raise PassCheckError
            return True

        return commands.check(predicate)

    @classmethod
    def in_party(cls):
        global data

        async def predicate(ctx: commands.Context):
            party = data.guilds[ctx.guild.id].members[ctx.author.id].party
            if party.one_person_party:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', 'not_in')).string())
                raise PassCheckError
            return True

        return commands.check(predicate)

    @classmethod
    def not_in_party(cls):
        global data

        async def predicate(ctx: commands.Context):
            party = data.guilds[ctx.guild.id].members[ctx.author.id].party
            if party.is_group:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', 'in_party')).string())
                raise PassCheckError
            return True

        return commands.check(predicate)

    @classmethod
    def is_party_leader(cls):
        global data

        async def predicate(ctx: commands.Context):
            party = data.guilds[ctx.guild.id].members[ctx.author.id].party
            if not party.is_leader(ctx.author.id):
                await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', 'not_leader')).string())
                raise PassCheckError
            return True

        return commands.check(predicate)
