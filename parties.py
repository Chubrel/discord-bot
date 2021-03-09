#! python
# coding=utf-8


from core import *


PARTY_LIFETIME = 3600
PARTY_INVITE_LIFETIME = 300

_phrase_codes = {'INVITED': 'invited',
                 'INVITED_BUT_IN_PARTY': 'invited_but_in_party',
                 'JOINED': 'joined_in_party',
                 'INVITED_ALREADY': 'already_invited',
                 'NO_INVITES': 'no_invites',
                 'IN_YOUR_PARTY': 'in_your_party',
                 'UNCERTAIN': 'ambiguous_invites',
                 'NO_INVITE_FROM': 'no_invites_from',
                 'DISBANDED': 'party_disbanded',
                 'IN_PARTY': 'in_party',
                 'LEADER_ALREADY': 'already_leader',
                 'KICKED': 'kicked_from_party',
                 'NEW_LEADER_SET': 'new_leader_set',
                 'NOT_IN_PARTY': 'not_in_party',
                 'NOT_MEMBER': 'not_member',
                 'LEFT': 'left_from_party'}


def setup(bot):
    bot.add_cog(Parties(bot))


class PartyInvite:
    def __init__(self, guild_id: int, member_id: int):
        self._guild_id = guild_id
        self._member_id = member_id
        self.inviters: dict[int, datetime] = {}

    def _clear_invites(self) -> None:
        now = datetime.utcnow()
        for inviter_id in self.inviters:
            if now - self.inviters[inviter_id] > timedelta(minutes=PARTY_INVITE_LIFETIME) or \
                    get_member(self._guild_id, inviter_id) is None:
                del self.inviters[inviter_id]

    def invited_by(self, inviter_id: int) -> str:
        self._clear_invites()
        invite_time = self.inviters.get(inviter_id)
        if invite_time is None:
            if self.in_party:
                if self.is_inviter_party(inviter_id):
                    return 'IN_YOUR_PARTY'
                else:
                    self.inviters[inviter_id] = datetime.utcnow()
                    return 'INVITED_BUT_IN_PARTY'
            else:
                self.inviters[inviter_id] = datetime.utcnow()
                return 'INVITED'
        else:
            return 'INVITED_ALREADY'

    def try_accept(self, inviter_id: Optional[int] = None) -> str:
        if self.in_party:
            return 'IN_PARTY'
        self._clear_invites()
        invites_count = len(self.inviters)
        if invites_count == 0:
            return 'NO_INVITES'
        elif inviter_id is None:
            if invites_count == 1:
                inviter_id = self.inviters.popitem()[0]
                return self._accept(inviter_id)
            else:
                return 'UNCERTAIN'
        elif inviter_id in self:
            del self.inviters[inviter_id]
            return self._accept(inviter_id)
        else:
            return 'NO_INVITE_FROM'

    def _accept(self, inviter_id: int) -> str:
        global data
        return data.guilds[self._guild_id].members[inviter_id].party.join(self._member_id)

    @property
    def invites_list(self) -> list:
        self._clear_invites()
        return sorted(self.inviters, key=lambda x: self.inviters[x])

    @property
    def in_party(self) -> bool:
        global data
        return data.guilds[self._guild_id].members[self._member_id].party.is_group

    def is_inviter_party(self, inviter_id: int) -> bool:
        global data
        return self is data.guilds[self._guild_id].members[inviter_id].party

    def __contains__(self, item: int):
        return item in self.inviters

    def __bool__(self):
        return bool(self.inviters)


class Party:
    def __init__(self, guild_id: int, member_id: int):
        self._guild_id = guild_id
        self.members: list[int] = [member_id]
        self.delay: Optional[datetime] = None

    def join(self, member_id: int) -> str:
        self.members.append(member_id)
        self._join_member(member_id)
        self.delay_expire()
        return 'JOINED'

    def leave(self, member_id: int) -> str:
        if self.one_person_party:
            return 'NOT_IN_PARTY'
        self._kick_member(member_id)
        return 'LEFT'

    def kick(self, member_id: int) -> str:
        if self.one_person_party:
            return 'NOT_IN_PARTY'
        elif not self.in_list(member_id):
            return 'NOT_MEMBER'
        self._kick_member(member_id)
        return 'KICKED'

    def set_leader(self, member_id: int) -> str:
        if self.is_leader(member_id):
            return 'LEADER_ALREADY'
        if member_id not in self:
            return 'NOT_MEMBER'
        self.members.remove(member_id)
        self.members.insert(0, member_id)
        return 'NEW_LEADER_SET'

    def disband(self) -> str:
        if self.one_person_party:
            return 'NOT_IN_PARTY'
        for m in self.members:
            Party.recreate(self._guild_id, m)
        return 'DISBANDED'

    def is_leader(self, member_id: int) -> bool:
        return member_id == self.members[0]

    def in_list(self, member_id: int) -> bool:
        return member_id in self

    @property
    def one_person_party(self) -> bool:
        return len(self.members) == 1

    @property
    def is_group(self) -> bool:
        return len(self.members) > 1

    @property
    def leader(self):
        return self.members[0]

    @classmethod
    def recreate(cls, guild_id: int, member_id: int) -> None:
        global data
        data.guilds[guild_id].members[member_id].party = Party(guild_id, member_id)

    def _join_member(self, member_id) -> None:
        global data
        data.guilds[self._guild_id].members[member_id].party = self

    def _kick_member(self, member_id) -> None:
        global data
        self.members.remove(member_id)
        Party.recreate(self._guild_id, member_id)

    def delay_expire(self):
        self.delay = datetime.utcnow() + timedelta(seconds=PARTY_LIFETIME)

    def __contains__(self, item: int):
        return item in self.members

    def __bool__(self):
        return self.is_group


class Parties(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    async def party(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument

    @party.command(name='list')
    @Checks.in_party()
    async def party_list(self, ctx: commands.Context):
        global data
        party_member_ids = data.guilds[ctx.guild.id].members[ctx.author.id].party.members
        party_member_nicks = [ctx.guild.get_member(i).display_name for i in party_member_ids]
        await ctx.send(Translate(ctx.guild.id, ('messages', 'lists', 'parties'),
                                 dict(list=', '.join(party_member_nicks))).string())

    @party.command(name='invite')
    @Checks.is_party_leader()
    async def party_invite(self, ctx: commands.Context, members: commands.Greedy[discord.Member]):
        global data, bot
        if not members:
            raise commands.BadArgument
        for member in members:
            if member.id == bot.user.id:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', 'i_invited')).string())
            elif member.bot:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', 'bot_invited'),
                                         {'bot': member.display_name}).string())
            elif member.id == ctx.author.id:
                await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', 'self_invite')).string())
            else:
                result = data.guilds[ctx.guild.id].members[member.id].invites.invited_by(ctx.author.id)
                await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', _phrase_codes[result]),
                                         {'member': member.display_name}).string())

    @party.command(name='accept')
    @Checks.not_in_party()
    async def party_accept(self, ctx: commands.Context, member: Optional[discord.Member]):
        global data
        if member is None:
            member_id = None
        else:
            member_id = member.id
        member_data = data.guilds[ctx.guild.id].members[ctx.author.id]
        result = member_data.invites.try_accept(member_id)
        if result == 'AMBIGUOUS':
            inviters = ', '.join([ctx.guild.get_member(i).display_name for i in member_data.invites.invites_list])
            await ctx.send(
                Translate(ctx.guild.id, ('messages', 'parties', _phrase_codes[result]), {'list': inviters}).string())
        elif result == 'NO_INVITE_FROM':
            await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', _phrase_codes[result]),
                                     {'member': ctx.guild.get_member(member_id).display_name}).string())
        elif result == 'JOINED':
            if member is None:
                member_id = member_data.party.leader
            await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', _phrase_codes[result]),
                                     {'member': ctx.guild.get_member(member_id).display_name}).string())
        elif result == 'NO_INVITES':
            await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', _phrase_codes[result])).string())
        else:
            raise RaiseError

    @party.command(name='join')
    @Checks.not_in_party()
    async def party_join(self, ctx: commands.Context, member: Optional[discord.Member]):
        await self.party_accept(ctx, member)

    @party.command(name='leave')
    @Checks.in_party()
    async def party_leave(self, ctx: commands.Context):
        global data
        result = data.guilds[ctx.guild.id].members[ctx.author.id].party.leave(ctx.author.id)
        await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', _phrase_codes[result])).string())

    @party.command(name='kick')
    @Checks.is_party_leader()
    @Checks.in_party()
    async def party_kick(self, ctx: commands.Context, members: commands.Greedy[discord.Member]):
        global data
        if not members:
            raise commands.BadArgument
        party = data.guilds[ctx.guild.id].members[ctx.author.id].party
        for member in members:
            result = party.kick(member.id)
            await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', _phrase_codes[result]),
                                     {'member': member.display_name}).string())

    @party.command(name='leader')
    @Checks.is_party_leader()
    @Checks.in_party()
    async def party_leader(self, ctx: commands.Context, member: discord.Member):
        result = data.guilds[ctx.guild.id].members[ctx.author.id].party.set_leader(member.id)
        await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', _phrase_codes[result]),
                                 {'member': member.display_name}).string())

    @party.command(name='disband')
    @Checks.is_party_leader()
    @Checks.in_party()
    async def party_disband(self, ctx: commands.Context):
        result = data.guilds[ctx.guild.id].members[ctx.author.id].party.disband()
        await ctx.send(Translate(ctx.guild.id, ('messages', 'parties', _phrase_codes[result])).string())

    async def cog_before_invoke(self, ctx: commands.Context):
        await party_lifetime(ctx)
