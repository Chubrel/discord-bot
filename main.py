#! python
# coding=utf-8
"""Chubaka bot"""


import discord
from discord.ext import commands

from core import *

# ⛔🚫🛑💯❓❗

COGS = ('Main', 'Actions', 'Homes', 'Schools', 'Games', 'Tests', 'Parties', 'Ballots', 'Reloads')
EXTENTIONS_FOR_RELOAD = ('actions', 'homes', 'schools', 'games', 'tests', 'parties', 'ballots')
EXTENTIONS_FOR_LOAD = ('main',) + EXTENTIONS_FOR_RELOAD


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


def init_member(guild_id: int, member_id: int, is_bot: bool) -> None:
    global data, member_data_dict, bot_member_data_dict
    if is_bot:
        member_class = BotMemberData
        data_dict = bot_member_data_dict
    else:
        member_class = MemberData
        data_dict = member_data_dict
    guild_members = data.guilds[guild_id].members
    member_data = guild_members.get(member_id)
    if member_data is None:
        if is_bot:
            guild_members[member_id] = member_class()
        else:
            guild_members[member_id] = member_class(guild_id, member_id)
    else:
        member_dict = member_data.__dict__
        if member_dict != data_dict:
            member_data.__dict__ = data_dict | member_dict
            guild_members[member_id] = member_data


def init_user(user_id: int):
    global data, user_data_dict
    user_data = data.users.get(user_id)
    if user_data is None:
        data.users[user_id] = UserData()
    else:
        user_dict = user_data.__dict__
        if user_dict != user_data_dict:
            user_data.__dict__ = user_data_dict | user_dict
            data.users[user_id] = user_data


def load_extensions(bot):
    for elem in EXTENTIONS_FOR_LOAD:
        bot.load_extension(elem)


def setup(bot):
    bot.add_cog(Main(bot))
    bot.add_cog(Reloads(bot))


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


def inner_list(list_: list[list]) -> list:
    while len(list_) != 0:
        list_ = list_[-1]
    return list_
'''


'''
def get_path_from_message_link(link: str) -> tuple:
    pass
'''


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
        if guild.id == MY_GUILD:
            await get_stats_line_emojis(guild)
        async for member in guild.fetch_members():
            init_member(member.guild.id, member.id, member.bot)
            init_user(member.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        init_member(member.guild.id, member.id, member.bot)
        init_user(member.id)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await handle_error(error, ctx.message)

    @commands.Cog.listener()
    async def on_disconnect(self):
        global data
        Loaders.save_data(data)
        print('Данные сохранены')

    @commands.command()
    @commands.is_owner()
    async def kill(self, ctx: commands.Context):
        await ctx.send('Какой жестокий мир!\nОтключаюсь...', )
        await self.on_disconnect()
        await self.bot.logout()


class Reloads(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, extention: str):
        if extention not in EXTENTIONS_FOR_RELOAD:
            raise commands.BadArgument
        self.bot.reload_extention(extention)


if __name__ == '__main__':

    Loaders.set_logging(debug=True)

    load_extensions(bot)

    with open('utils/token.txt') as token:
        bot.run(token.readline())
