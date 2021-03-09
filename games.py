#! python
# coding=utf-8


from core import *

from random import randrange, sample, shuffle


_games = ('codenames',)  # ('guess', 'numb', 'b&c', 'stones')

_game_codes = {'CODENAMES': 'Codenames', 'GUESS': 'GuessCraft'}


def setup(bot):
    bot.add_cog(Games(bot))


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
        codenames = Loaders.read_file('langs/codenames_ru.txt').split()
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


class Games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @Checks.in_guild_home()
    async def game(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed:
                raise commands.BadArgument
            else:
                await self.game_list(ctx)

    @game.command(name='list')
    async def game_list(self, ctx: commands.Context):
        await ctx.send(Translate(ctx.guild.id, ('messages', 'lists', 'games'), dict(list=", ".join(_games))).string())

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
        await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', 'finish')).string())

    @game.command(name='stats')
    async def game_stats(self, ctx: commands.Context):
        raise NothingHere

    @game.group(name='start')
    @Checks.is_party_leader()
    async def game_start(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument

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
