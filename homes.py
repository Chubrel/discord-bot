#! python
# coding=utf-8


from core import *


def count_games(guild_id: int) -> int:
    global data
    count = 0
    for member_data in data.guilds[guild_id].members.values():
        count += bool(member_data.games.active)
    return count


def abort_games(guild_id: int) -> None:
    global data
    member_data = data.guilds[guild_id].members
    for member_id in member_data:
        games_data = member_data[member_id].games
        games_data.game = None
        games_data.active = ''


def setup(bot):
    bot.add_cog(Homes(bot))


class Homes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='home')
    async def home(self, ctx: commands.Context):
        global data
        if ctx.invoked_subcommand is None:
            home_ids = data.guilds[ctx.guild.id].home_ids
            if ctx.channel.id in home_ids:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'homes', 'here')).string())
            else:
                await self.home_list(ctx)

    @home.command(name='list')
    async def home_list(self, ctx: commands.Context):
        global data
        home_ids = data.guilds[ctx.guild.id].home_ids
        if home_ids:
            homes = ', '.join([f'<#{i}>' for i in home_ids])
            await ctx.send(Translate(ctx.guild.id, ('messages', 'lists', 'homes'), {'list': homes}).string())
        else:
            await ctx.send(Translate(ctx.guild.id, ('messages', 'homes', 'have_no')).string())

    @home.command(name='set')
    @commands.has_permissions(manage_channels=True)
    async def set_home(self, ctx: commands.Context):
        global data
        home_ids = data.guilds[ctx.guild.id].home_ids
        if ctx.channel.id in home_ids:
            await ctx.send(Translate(ctx.guild.id, ('messages', 'homes', 'here_already')).string())
        else:
            data.guilds[ctx.guild.id].home_ids.add(ctx.channel.id)
            await ctx.send(Translate(ctx.guild.id, ('messages', 'homes', 'new')).string())

    @home.command(name='remove')
    @commands.has_permissions(manage_channels=True)
    async def del_home(self, ctx: commands.Context, *, arg: str = ''):
        global data
        guild_id = ctx.guild.id
        home_ids = data.guilds[guild_id].home_ids
        if ctx.channel.id not in home_ids:
            await ctx.send(Translate(ctx.guild.id, ('messages', 'homes', 'there_no')).string())
        else:
            games_count = count_games(guild_id)
            if games_count != 0 and arg != 'confirm':
                await ctx.send(Translate(ctx.guild.id, ('messages', 'homes', 'remove_warning'),
                                         {'games_count': games_count}).string())
            else:
                abort_games(guild_id)
                data.guilds[guild_id].home_ids.remove(ctx.channel.id)
                await ctx.send(Translate(ctx.guild.id, ('messages', 'homes', 'removed')).string())
