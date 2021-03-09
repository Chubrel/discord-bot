#! python
# coding=utf-8


from core import *


def count_tests(guild_id: int) -> int:
    global data
    count = 0
    for member_data in data.guilds[guild_id].members.values():
        count += bool(member_data.tests.active)
    return count


def abort_tests(guild_id: int) -> None:
    global data
    member_data = data.guilds[guild_id].members
    for member_id in member_data:
        tests_data = member_data[member_id].tests
        tests_data.test = None
        tests_data.active = ''


def setup(bot):
    bot.add_cog(Schools(bot))


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
                await ctx.send(Translate(ctx.guild.id, ('messages', 'schools', 'here')).string())
            else:
                await self.school_list(ctx)

    @school.command(name='list')
    async def school_list(self, ctx: commands.Context):
        global data
        school_ids = data.guilds[ctx.guild.id].school_ids
        if school_ids:
            schools = ', '.join([f'<#{i}>' for i in school_ids])
            await ctx.send(Translate(ctx.guild.id, ('messages', 'lists', 'schools'), {'list': schools}).string())
        else:
            await ctx.send(Translate(ctx.guild.id, ('messages', 'schools', 'have_no')).string())

    @school.command(name='set')
    @commands.has_permissions(manage_channels=True)
    async def set_school(self, ctx: commands.Context):
        global data
        school_ids = data.guilds[ctx.guild.id].school_ids
        if ctx.channel.id in school_ids:
            await ctx.send(Translate(ctx.guild.id, ('messages', 'schools', 'here_already')).string())
        else:
            data.guilds[ctx.guild.id].school_ids.add(ctx.channel.id)
            await ctx.send(Translate(ctx.guild.id, ('messages', 'schools', 'new')).string())

    @school.command(name='remove')
    @commands.has_permissions(manage_channels=True)
    async def del_school(self, ctx: commands.Context, *, arg: str = ''):
        global data
        guild_id = ctx.guild.id
        school_ids = data.guilds[guild_id].school_ids
        if ctx.channel.id not in school_ids:
            await ctx.send(Translate(ctx.guild.id, ('messages', 'schools', 'there_no')).string())
        else:
            tests_count = count_tests(guild_id)
            if tests_count != 0 and arg != 'confirm':
                await ctx.send(
                    Translate(ctx.guild.id, ('messages', 'schools', 'remove_warning'),
                              {'tests_count': tests_count}).string())
            else:
                abort_tests(guild_id)
                data.guilds[guild_id].school_ids.remove(ctx.channel.id)
                await ctx.send(Translate(ctx.guild.id, ('messages', 'schools', 'removed')).string())
