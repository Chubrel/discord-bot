#! python
# coding=utf-8


from datetime import timezone

from tools import *


BALLOT_PLACEHOLD_FIELD_VALUE = '---'
VOTE_GET_REACTION = '📝'
VOTE_CONFIRM_REACTION = '☑️'
VOTE_REACTION_OK = '🆗'
MAX_BALLOT_OPTIONS = 10
MAX_LAST_VOTERS_SHOW = 5

BALLOT_SETTINGS = dict(title=True, options=True, updateresults=False, resultsonfinish=True, optionscount=True,
                       status=True, voterscount=True, role=True, ballotid=True, voteid=True, ids=True, update=True,
                       maxvoterscount=True, finishtime=True, ballothint=True, votehint=True, hints=True)

_ballots = ('secret',)


def setup(bot):
    bot.add_cog(Ballots(bot))


class Ballot:

    def __init__(self, ballot_type: str, options_number: int, min_count: int, max_count: int,
                 main_embed_dict: dict, vote_embed_dict: dict, fields_indexes: dict, reactions: list[str],
                 max_votes_count: Optional[int] = None, finish_time: Optional[datetime] = None,
                 last_voters_count: int = 0, **settings: bool):
        self.ballot_type: str = ballot_type
        self.options: list = [0] * options_number
        self.min_count: int = min_count
        self.max_count: int = max_count
        self.main_embed_dict: dict = main_embed_dict
        self.vote_embed_dict: dict = vote_embed_dict
        self.fields_indexes: dict = fields_indexes
        self.reactions: list[str] = reactions
        self.max_votes_count: Optional[int] = max_votes_count
        self.finish_time: Optional[datetime] = finish_time
        self.last_voters: list = [None] * last_voters_count
        self.settings: dict[str, bool] = settings
        self.voters: set[int] = set()
        self.finished: bool = False
        self.ballot_message_path: Optional[tuple] = None
        self.id: Optional[int] = None

    def finish_check(self) -> None:
        if not self.finished:
            if self.finish_time is not None:
                self.finished = self.finish_time < datetime.now(tz=timezone.utc)
            if self.max_votes_count:
                self.finished = len(self.voters) >= self.max_votes_count

    def add(self, user_id: int, *options: int) -> str:
        self.finish_check()
        if self.finished:
            return 'FINISHED'
        if user_id not in self.voters:
            for option in options:
                self.options[option] += 1
            self.voters.add(user_id)
            self.add_last_voter(user_id)
            return 'ADDED'
        return 'ALREADY'

    def remove(self, user_id: int, *options: int) -> str:
        self.finish_check()
        if self.finished:
            return 'FINISHED'
        if user_id in self.voters:
            for option in options:
                self.options[option] -= 1
            self.voters.remove(user_id)
            return 'REMOVED'
        return 'THERE_NO'

    async def finish(self):
        self.finished = True
        await self.update()

    def delete(self):
        raise NotImplementedError

    async def change_vote_color(self, name: str, message: discord.Message):
        color = COLORS.get(name)
        if color is None:
            color = 0
        vote_embed_dict = self.vote_embed_dict.copy()
        vote_embed_dict['color'] = color
        await message.edit(embed=discord.Embed.from_dict(vote_embed_dict))

    def parse(self, reactions: list[str]) -> tuple[str, Optional[tuple]]:
        if len(reactions) > self.max_count or len(reactions) < self.min_count:

            if len(reactions) > self.max_count:
                return 'TOO_MANY', None
            return 'NOT_ENOUGH', None

        indexes = []
        for r in reactions:
            if r in self.reactions:
                indexes.append(self.reactions.index(r))
        return 'OK', tuple(indexes)

    def add_last_voter(self, user_id: int) -> None:
        if len(self.last_voters) > 0:
            for i in range(len(self.last_voters) - 1):
                self.last_voters[i] = self.last_voters[i + 1]
            self.last_voters[-1] = f'<@{user_id}>'

    def update_results_fields(self) -> None:
        values = get_stats_lines(*self.options)
        for i in range(len(self.options)):
            self.main_embed_dict['fields'][i]['value'] = values[i]

    def get_setting(self, setting: str) -> bool:
        value = self.settings.get(setting)
        if value is None:
            value = BALLOT_SETTINGS.get(setting)
            if value is None:
                raise KeyError(f'Invalid setting: {setting}')
        return value

    async def send_vote(self, user: discord.User) -> None:
        self.finish_check()
        if self.finished:
            await user.send(Translate(self.ballot_message_path[0],
                                      ('messages', 'ballots', 'finished_already')).string())
        else:
            embed = discord.Embed.from_dict(self.vote_embed_dict)
            message = await user.send(embed=embed)
            GlobalBallotData().new_vote_listner((message.channel.id, message.id), self)
            await add_reactions(message, self.reactions + [VOTE_CONFIRM_REACTION])

    async def update(self) -> None:
        self.finish_check()
        if not self.get_setting('update'):
            return
        message = await get_message(*self.ballot_message_path)

        if self.get_setting('options') and (self.get_setting('updateresults') or
                                            (self.finished and self.get_setting('resultsonfinish'))):
            self.update_results_fields()

        index = self.fields_indexes.get('count')
        if index is not None:
            self.main_embed_dict['fields'][index]['value'] = len(self.voters)

        index = self.fields_indexes.get('status')
        if index is not None:
            if self.finished:
                word = 'finished'
            else:
                word = 'active'
            self.main_embed_dict['fields'][index]['value'] = Translate(self.ballot_message_path[0],
                                                                       ('messages', 'ballots', word)).string()

        if len(self.last_voters) > 0 and self.last_voters[-1] is not None:
            value = ', '.join([i for i in self.last_voters if i is not None])
            index = self.fields_indexes['last_voters']
            self.main_embed_dict['fields'][index]['value'] = value

        await message.edit(embed=discord.Embed.from_dict(self.main_embed_dict))

    async def send_results(self, channel: discord.TextChannel) -> None:
        embed_dict = {'title': Translate(channel.guild.id, ('messages', 'ballots', 'results')).string(),
                      'description': self.vote_embed_dict['title'], 'color': COLORS['yellow'],
                      'fields': self.main_embed_dict['fields'][:len(self.options)]}
        await channel.send(embed=discord.Embed.from_dict(embed_dict))

    @classmethod
    async def try_get_vote(cls, user: discord.User, ballot_id: int) -> None:
        if ballot_id in data.users[user.id].ballots:
            ballot = GlobalBallotData().ballots.get(ballot_id)
            if ballot is not None:
                await ballot.send_vote(user)
                return
        raise BallotNotFound


class GlobalBallotData:

    _instance = None
    _from_data = False

    def __new__(cls, *args, **kwargs):
        global data
        if not cls._from_data:
            try:
                cls._instance = data.ballots
            except NameError:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
            else:
                cls._from_data = True
        return cls._instance

    def __init__(self):
        self.ballots: dict[int, Ballot] = {}
        self.ballot_listners: dict[tuple, int] = {}
        self.vote_listners: dict[tuple, int] = {}
        self._id: int = 0

    def get_free_id(self) -> int:
        ballot_id = self._id
        self._id += 1
        return ballot_id

    def new_ballot(self, ballot_id: int, ballot: Ballot) -> None:
        self.ballots[ballot_id] = ballot
        ballot.id = ballot_id

    def new_ballot_listner(self, msg_path: tuple, ballot: Ballot) -> None:
        ballot_id = ballot.id
        ballot.ballot_message_path = msg_path
        self.ballot_listners[msg_path] = ballot_id

    def new_vote_listner(self, msg_path: tuple, ballot: Ballot) -> None:
        ballot_id = ballot.id
        self.vote_listners[msg_path] = ballot_id


class Ballots(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def ballot(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument

    @ballot.command(name='start')
    async def ballot_start(self, *text):
        pass

    @ballot.command(name='finish')
    async def ballot_finish(self, ctx: commands.Context, ballot_id: int):
        global data
        if ballot_id in data.guilds[ctx.guild.id].ballots:
            ballot = GlobalBallotData().ballots.get(ballot_id)
            if ballot is not None:
                if ballot.finished:
                    await ctx.send(Translate(ctx.guild.id, ('messages', 'ballots', 'finished_already')).string())
                else:
                    await ballot.finish()
                    await ctx.send(Translate(ctx.guild.id, ('messages', 'ballots', 'manual_finish')).string())
                return
        raise BallotNotFound

    @ballot.command(name='results')
    async def ballot_results(self, ctx: commands.Context, ballot_id: int):
        global data
        if ballot_id in data.guilds[ctx.guild.id].ballots:
            ballot = GlobalBallotData().ballots.get(ballot_id)
            if ballot is not None:
                if ballot.finished:
                    await ballot.send_results(ctx.channel)
                else:
                    await ctx.send(Translate(ctx.guild.id, ('messages', 'ballots', 'not_finished')).string())
                return
        raise BallotNotFound

    @ballot.command(name='update')
    async def ballot_update(self, ctx: commands.Context, ballot_id: int):
        global data
        if ballot_id in data.guilds[ctx.guild.id].ballots:
            ballot = GlobalBallotData().ballots.get(ballot_id)
            if ballot is not None:
                await ballot.update()
                await ctx.send(Translate(ctx.guild.id, ('messages', 'ballots', 'updated')).string())
                return
        raise BallotNotFound

    @commands.command()
    @commands.dm_only()
    async def vote(self, ctx: commands.Context, ballot_id: int):
        await Ballot.try_get_vote(ctx.author, ballot_id)

    @classmethod
    async def ballot_time_wait(cls, guild_id: int, ballot_id: int):
        global data
        if ballot_id in data.guilds[guild_id].ballots:
            ballot = GlobalBallotData().ballots.get(ballot_id)
            if ballot is not None and not ballot.finished and ballot.finish_time is not None:
                await discord.utils.sleep_until(ballot.finish_time)
                await ballot.finish()

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild):
        global data
        for ballot_id in data.guilds[guild.id].ballots:
            await self.ballot_time_wait(guild.id, ballot_id)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        global _ballots

        try:
            msg = message.content

            if message.author.bot or not msg.startswith('~ballot start'):
                return

            b = len('~ballot start')
            lines = [i.strip() for i in msg.splitlines()]
            args = lines[0][b + 1:].split(None, 3)

            if len(args) <= 2:
                raise commands.BadArgument

            ballot_type, min_count, max_count, title, *_ = *args, ''

            ballot_type = ballot_type.lower()

            ctx = commands.Context(message=message, bot=self.bot, prefix=BOT_PREFIX)

            try:
                min_count = int(min_count)
                max_count = int(max_count)
            except ValueError:
                raise commands.BadArgument

            reacts = []
            strings = []
            i = 1
            j = 0
            try:
                try:
                    for i in range(1, len(lines)):
                        p = lines[i].split(None, 1)
                        emoji = await EveryEmojiConverter().convert(ctx, p[0])
                        reacts.append(emoji)
                        if len(p) == 2:
                            strings.append(p[1])
                        else:
                            strings.append('')
                except commands.BadArgument:
                    j = 1
                finally:
                    options_count = i - j
            except IndexError:
                raise commands.BadArgument

            max_voters_count: Optional[int] = None
            finish_time: Optional[datetime] = None
            vote_role: Optional[discord.Role] = None
            last_voters_count: int = 0
            color: Union[int, discord.Colour] = COLORS['blue']
            delete_msg: bool = False
            settings = BALLOT_SETTINGS.copy()

            for line in lines[options_count + 1:len(lines)]:
                line_ = line.split(None, 1)
                if len(line_) == 1:
                    if line_[0] in ('del', 'delete', 'rem', 'remove'):
                        delete_msg = True
                        continue
                    raise commands.BadArgument
                option, param = line_
                option = option.replace('_', '').lower()
                if option in ('enable', 'disable'):
                    params = param.replace('_', '').lower().split()
                    value = option == 'enable'
                    for elem in params:
                        try:
                            settings[elem] = value
                        except KeyError:
                            raise DontUnderstand(elem)
                    continue
                elif option in ('maxvoters', 'maxvoterscount', 'maxvotercount', 'votersmaxcount', 'votermaxcount'):
                    try:
                        max_voters_count = int(param)
                    except ValueError:
                        raise DontUnderstand(param)
                    else:
                        continue
                elif option in ('time', 'finishtime', 'endtime'):
                    try:
                        finish_time = ISOFormatConverter.parse(param)
                    except commands.BadArgument:
                        raise DontUnderstand(param)
                    else:
                        continue
                elif option in ('lastvoters', 'lastvoter'):
                    try:
                        last_voters_count = int(param)
                    except ValueError:
                        raise DontUnderstand(param)
                    else:
                        continue
                elif option in ('color', 'colour'):
                    param = param.lower()
                    color = COLORS.get(param)
                    if color is None:
                        try:
                            color = await commands.ColourConverter().convert(ctx, param)
                        except commands.BadColourArgument:
                            raise DontUnderstand(param)
                        else:
                            continue
                    else:
                        continue
                elif option in ('role', 'voterole'):
                    '''
                    word = ''
                    space = False
                    for c in line:
                        if c != ' ' or (space and word):
                            word += c
                            space = c == ' '
                        elif word:
                            try:
                                print(1, word)
                                vote_roles.append(await commands.RoleConverter().convert(ctx, word))
                            except commands.BadArgument:
                                space = True
                                word += ' '
                            else:
                                word = ''
                    print(2, word, vote_roles)
                    if not word:
                        continue
                        '''
                    try:
                        vote_role = await commands.RoleConverter().convert(ctx, param)
                    except commands.RoleNotFound:
                        DontUnderstand(param)
                    else:
                        continue
                raise DontUnderstand(option)

            vote_type_check = ballot_type in _ballots
            options_check = 0 < min_count <= max_count <= options_count >= 2 and\
                            (max_voters_count is None or max_voters_count > 0)

            prohib_reacts_check = VOTE_CONFIRM_REACTION not in reacts
            some_options = 2 <= options_count <= MAX_BALLOT_OPTIONS

            if not vote_type_check:
                raise DontUnderstand(ballot_type)
            if not options_check:
                raise commands.BadArgument
            if not prohib_reacts_check:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'ballots', 'reaction_prohibited'),
                                         {'reaction': VOTE_CONFIRM_REACTION}).string())
                return
            if not some_options:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'ballots', 'incorrect_option_count'),
                                         {'min_count': 2, 'max_count': MAX_BALLOT_OPTIONS}).string())
                return

            if settings['updateresults']:
                value = get_stats_lines(0)[0]
            else:
                value = BALLOT_PLACEHOLD_FIELD_VALUE

            if settings['options']:
                fields = [{'name': f'{r}  {t}', 'value': value, 'inline': False} for r, t in zip(reacts, strings)]
                index = options_count
            else:
                fields = []
                index = 0

            if settings['title']:
                title_ = title
            else:
                title_ = ''

            main_embed_dict = {'title': title_, 'description': '', 'color': color, 'fields': fields}

            vote_embed_dict = {'title': title, 'description': '', 'color': COLORS['blue'],
                               'fields': [{'name': f'{r}  {t}', 'value': BALLOT_PLACEHOLD_FIELD_VALUE, 'inline': False}
                                          for r, t in zip(reacts, strings)]}

            fields_indexes = {}

            if settings['hints']:
                if settings['ballothint']:
                    main_embed_dict['footer'] = {'text': Translate(ctx.guild.id,
                                                                   ('messages', 'ballots', 'secret_ballot_guide'),
                                                                   {'reaction': VOTE_GET_REACTION}).string()}
                if settings['votehint']:
                    vote_embed_dict['footer'] = {'text': Translate(ctx.guild.id,
                                                                   ('messages', 'ballots', 'vote_guide'),
                                                                   {'reaction': VOTE_CONFIRM_REACTION}).string()}

            if min_count == max_count:
                value = Translate(ctx.guild.id, ('messages', 'ballots', 'options_count_value'),
                                  {'count': min_count}).string()
            else:
                value = Translate(ctx.guild.id, ('messages', 'ballots', 'options_count_2_values'),
                                  {'min_count': min_count, 'max_count': max_count}).string()
            args = dict(name=Translate(ctx.guild.id, ('messages', 'ballots', 'options_count')).string(),
                        value=value, inline=True)
            if settings['optionscount']:
                main_embed_dict['fields'].append(args.copy())
                index += 1
            vote_embed_dict['fields'].append(args)

            if settings['voterscount']:
                main_embed_dict['fields'].append(dict(
                    name=Translate(ctx.guild.id, ('messages', 'ballots', 'count')).string(), value=0, inline=True))
                fields_indexes['count'] = index
                index += 1

            if settings['status']:
                main_embed_dict['fields'].append(dict(
                    name=Translate(ctx.guild.id, ('messages', 'ballots', 'status')).string(),
                    value=Translate(ctx.guild.id, ('messages', 'ballots', 'active')).string(), inline=True))
                fields_indexes['status'] = index
                index += 1

            if vote_role and settings['role']:
                main_embed_dict['fields'].append(dict(
                    name=Translate(ctx.guild.id, ('messages', 'ballots', 'role_restriction')).string(),
                    value=vote_role.mention, inline=True))
                index += 1

            if max_voters_count and settings['maxvoterscount']:
                main_embed_dict['fields'].append(dict(
                    name=Translate(ctx.guild.id, ('messages', 'ballots', 'max')).string(),
                    value=max_voters_count, inline=True))
                index += 1

            if finish_time and settings['finishtime']:
                main_embed_dict['fields'].append(dict(
                    name=Translate(ctx.guild.id, ('messages', 'ballots', 'finish_time')).string(),
                    value=finish_time.isoformat(sep=' ', timespec='minutes'), inline=True))
                index += 1

            ballot_id = GlobalBallotData().get_free_id()

            if settings['ids']:
                args = dict(name=Translate(ctx.guild.id, ('messages', 'ballots', 'id')).string(),
                            value=ballot_id, inline=True)
                if settings['ballotid']:
                    main_embed_dict['fields'].append(args.copy())
                    index += 1
                if settings['voteid']:
                    vote_embed_dict['fields'].append(args)

            if last_voters_count > 0:
                main_embed_dict['fields'].append(dict(
                    name=Translate(ctx.guild.id, ('messages', 'ballots', 'last_voters')).string(),
                    value=Translate(ctx.guild.id, ('messages', 'ballots', 'no_voters')).string(), inline=False))
                fields_indexes['last_voters'] = index

            message = await ctx.send(embed=discord.Embed.from_dict(main_embed_dict))

            ballot = Ballot(ballot_type, options_count, min_count, max_count,
                            main_embed_dict, vote_embed_dict, fields_indexes, reacts,
                            max_voters_count, finish_time, last_voters_count, **settings)

            GlobalBallotData().new_ballot(ballot_id, ballot)
            GlobalBallotData().new_ballot_listner((ctx.guild.id, ctx.channel.id, message.id), ballot)

            if vote_role:
                members = set(vote_role.members)
            else:
                members = ctx.guild.members

            for member in members:
                if not member.bot:
                    data.users[member.id].ballots.add(ballot_id)

            data.guilds[ctx.guild.id].ballots.add(ballot_id)

            if finish_time is not None:
                await self.ballot_time_wait(ctx.guild.id, ballot_id)

            await message.add_reaction(VOTE_GET_REACTION)

            if delete_msg:
                await message.delete()

        except discord.DiscordException as error:
            await handle_error(error, message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        global data
        guild_id = payload.guild_id
        channel_id = payload.channel_id
        message_id = payload.message_id

        if payload.user_id == MY_ID:
            return

        if guild_id:
            message = await get_message(guild_id, channel_id, message_id)
        else:
            message = await get_message(channel_id, message_id)

        try:
            emoji = str(payload.emoji)
            if emoji == VOTE_GET_REACTION:

                ballot_id = GlobalBallotData().ballot_listners.get(
                    (guild_id, channel_id, message_id))

                if ballot_id is not None:
                    await Ballot.try_get_vote(payload.member, ballot_id)

                reaction = None
                for elem in message.reactions:
                    if str(elem) == emoji:
                        reaction = elem
                        break

                await reaction.remove(payload.member)

            elif emoji == VOTE_CONFIRM_REACTION:

                ballot_id = GlobalBallotData().vote_listners.get(
                    (channel_id, message_id))

                if ballot_id is not None:
                    ballot = GlobalBallotData().ballots.get(ballot_id)

                    if ballot is not None:

                        reactions = [str(i) for i in message.reactions if i.count == 2]

                        if VOTE_CONFIRM_REACTION in reactions:
                            reactions.remove(VOTE_CONFIRM_REACTION)

                        p = ballot.parse(reactions)

                        user = self.bot.get_user(payload.user_id)

                        if p[0] == 'TOO_MANY':
                            await ballot.change_vote_color('red', message)
                            await user.send(Translate(user.id,
                                                           ('messages', 'ballots', 'too_many')).string())
                        elif p[0] == 'NOT_ENOUGH':
                            await ballot.change_vote_color('red', message)
                            await user.send(Translate(user.id,
                                                           ('messages', 'ballots', 'not_enough')).string())
                        else:
                            t = ballot.add(user.id, *p[1])
                            if t == 'FINISHED':
                                await ballot.change_vote_color('yellow', message)
                                await user.send(Translate(user.id,
                                                               ('messages', 'ballots', 'finished_already')).string())
                            elif t == 'ALREADY':
                                await ballot.change_vote_color('yellow', message)
                                await user.send(Translate(user.id,
                                                               ('messages', 'ballots', 'already')).string())
                            else:
                                await ballot.change_vote_color('green', message)
                                await message.add_reaction(VOTE_REACTION_OK)
                                await user.send(Translate(user.id, ('messages', 'ballots', 'added')).string())
                                await ballot.update()

        except discord.DiscordException as error:
            await handle_error(error, message)
