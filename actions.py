#! python
# coding=utf-8


import asyncio

from core import *


REACT_MAX_EMOJI_COUNT = 10


def setup(bot):
    bot.add_cog(Actions(bot))


class Actions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx: commands.Context, *, arg: str = ''):
        if not arg or arg == 'list':
            await ctx.send(
                Translate(ctx.guild.id, ('messages', 'lists', 'messages'), dict(list=", ".join(MESSAGES))).string())
        elif arg in MESSAGES:
            try:
                await ctx.send(MESSAGES[arg])
            except FileNotFoundError:
                print(FILE_NOT_FOUND.format(MESSAGES[arg]))

    @commands.command()
    @commands.has_permissions(attach_files=True, embed_links=True)
    async def image(self, ctx: commands.Context, *, arg: str = ''):
        if not arg or arg == 'list':
            await ctx.send(
                Translate(ctx.guild.id, ('messages', 'lists', 'images'), dict(list=", ".join(IMAGES))).string())
        elif arg in IMAGES:
            try:
                await ctx.send(IMAGES[arg])
            except FileNotFoundError:
                print(FILE_NOT_FOUND.format(IMAGES[arg]))

    @commands.command()
    @commands.has_permissions(attach_files=True)
    async def sound(self, ctx: commands.Context, *, arg: str = ''):
        if not arg or arg == 'list':
            await ctx.send(
                Translate(ctx.guild.id, ('messages', 'lists', 'sounds'), dict(list=", ".join(SOUNDS))).string())
        elif arg in SOUNDS:
            try:
                await ctx.send(file=discord.File('sounds/' + SOUNDS[arg]))
            except FileNotFoundError:
                print(FILE_NOT_FOUND.format(SOUNDS[arg]))

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
            members_and_channels.append(ctx.channel)

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

    @commands.group(name='lang')
    async def language(self, ctx: commands.Context):
        if not (ctx.guild is None or ctx.author.permissions_in(ctx.channel).manage_channels):
            raise commands.BadArgument
        if ctx.invoked_subcommand is None:
            await self.lang_list(ctx)

    @language.command(name='set')
    async def lang_set(self, ctx: commands.Context, *, lang: str = ''):
        global data, _lang_list
        if ctx.guild is None:
            lang_id = ctx.author.id
            special_data = data.users[lang_id]
        else:
            lang_id = ctx.guild.id
            special_data = data.guilds[lang_id]
        if lang in _lang_list:
            if special_data.lang != lang:
                special_data.lang = lang
                await ctx.send(Translate(lang_id, ('messages', 'langs', 'changed')).string())
            else:
                await ctx.send(Translate(lang_id, ('messages', 'langs', 'already')).string())
        else:
            await ctx.send(Translate(lang_id, ('messages', 'langs', 'no_such')).string())

    @language.command(name='list')
    async def lang_list(self, ctx: commands.Context):
        global data, _lang_list
        if ctx.guild is None:
            lang_set = Translate.user_lang(ctx.author.id)
        else:
            lang_set = Translate.guild_lang(ctx.guild.id)
        text = f"{Translate(lang_set, ('messages', 'langs', 'set'))}\n" \
               f"{Translate(lang_set, ('lang',))} [{lang_set}]\n" \
               f"{Translate(lang_set, ('messages', 'langs', 'available'))}\n"
        for k in _lang_list:
            if lang_set != k:
                text += f"{Translate(k, ('lang',))} [{k}]\n"
        await ctx.send(text)

    @commands.command()
    async def choose(self, ctx: commands.Context, n: Optional[int] = 1, *selection: str):
        if n <= 0 or n > len(selection) or len(selection) == 0:
            raise commands.BadArgument
        chosen = ', '.join(sample(selection, n))
        await ctx.send(Translate(ctx.guild.id, ('messages', 'choose', 'i_choose')).string())
        await asyncio.sleep(1)
        await ctx.send(Translate(ctx.guild.id, ('messages', 'choose', 'chosen'), {'chosen': chosen}).string())

    @commands.group()
    async def react(self, ctx: commands.Context):
        """For custom reactions"""
        if not (ctx.guild is None or ctx.author.permissions_in(ctx.channel).manage_channels):
            raise commands.BadArgument
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument

    @react.command(name='msg')
    async def react_msg(self, ctx: commands.Context, *args):
        global _reactions
        msg_list = await ctx.channel.history(limit=1, before=ctx.message.created_at).flatten()
        msg = msg_list[0]
        reacts_list = Placeholder.parse_reacts(args)
        await fill_reactions(msg, reacts_list)
        # await ctx.message.delete()

    @react.command(name='member')
    async def react_member(self, ctx: commands.Context,
                           emojis: commands.Greedy[EmojiMultiConverter],
                           members: commands.Greedy[discord.Member], nothing: Optional[str]):
        global data
        if nothing:
            raise DontUnderstand(nothing)
        reacts = [j for i in emojis for j in i]
        if len(reacts) > REACT_MAX_EMOJI_COUNT:
            await ctx.send(Translate(ctx.guild.id, ('messages', 'react_member', 'too_many'),
                                     {'count': REACT_MAX_EMOJI_COUNT}).string())
            raise PassCheckError
        if not members:
            members.append(ctx.author)
        guild_data = data.guilds[ctx.guild.id]
        for member in members:
            guild_data.members[member.id].reactions.set(reacts)
            if emojis:
                if member == ctx.author:
                    await ctx.send(Translate(ctx.guild.id, ('messages', 'react_member', 'set_self')).string())
                elif member == self.bot.user:
                    await ctx.send(Translate(ctx.guild.id, ('messages', 'react_member', 'set_me')).string())
                else:
                    await ctx.send(Translate(ctx.guild.id, ('messages', 'react_member', 'set'),
                                             {'member': member.display_name}).string())
            else:
                if member == ctx.author:
                    await ctx.send(Translate(ctx.guild.id, ('messages', 'react_member', 'removed_self')).string())
                elif member == self.bot.user:
                    await ctx.send(Translate(ctx.guild.id, ('messages', 'react_member', 'removed_me')).string())
                else:
                    await ctx.send(Translate(ctx.guild.id, ('messages', 'react_member', 'removed'),
                                             {'member': member.display_name}).string())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        global data
        if message.guild is None:
            reactions = data.users[message.author.id].reactions
        else:
            reactions = data.guilds[message.guild.id].members[message.author.id].reactions
        if reactions:
            await add_reactions(message, reactions)

