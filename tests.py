#! python
# coding=utf-8


from random import randrange

from tools import *


ENCH_TEST_MAX_QUESTIONS_COUNT = 10

NO_SUCH_QUESTION_TYPE = "No such question type '{}'"

_tests = ('ench',)
_test_codes = {'ENCH': 'Enchantment'}
_question_numbers = ('1️⃣', '2️⃣', '3️⃣')
_test_options_number = len(_question_numbers)
_question_changers = ('⬅️', '➡️')


def get_options(path: tuple) -> list:
    global lang_dict
    opt = lang_dict[DEFAULT_LANG]
    for el in path:
        opt = opt[el]
    return list(opt.keys())


def setup(bot):
    bot.add_cog(Tests(bot))


class Question:
    """Generates a test question"""

    def __init__(self, guild_id: int, number: int, type_index: Optional[int] = None):
        global ench_tests
        self._guild_id: int = guild_id
        self.number: int = number
        if type_index is None:
            type_ = choice(ench_tests[:4])
        elif 0 <= type_index < 12:
            type_ = ench_tests[type_index]
        else:
            raise TypeError
        self._type: str = type_
        question_data = self.get_question_data()
        self._description_substitution: dict = question_data[0]
        self._answer_options_lang_path: list = question_data[1]
        self.answer_index: int = question_data[2]
        self._random_choice: int = question_data[3]  # >= 1

    @property
    def embed_dict(self):
        global data, _question_numbers
        title = Translate(self._guild_id, ('messages', 'tests', 'question')).string()
        if self.number != 0:
            title += Translate(self._guild_id, ('messages', 'tests', 'question_number'), {'number': self.number}) \
                .string()
        description = Translate(self._guild_id, ('ench', 'questions', self._type), self._description_substitution) \
            .string()
        fields = []
        for i in range(_test_options_number):
            field = {'name': _question_numbers[i], 'inline': True,
                     'value': Translate(self._guild_id, self._answer_options_lang_path[i], {})
                         .string()}
            fields.append(field)
        embed_dict = {'title': title, 'description': description, 'color': 16_776_960, 'fields': fields}
        return embed_dict

    def get_question_data(self) -> tuple:
        try:
            func = Question.__dict__[self._type]
            return func(self)
        except KeyError:
            raise ValueError(NO_SUCH_QUESTION_TYPE.format(self._type))

    def max_ench_lvl(self) -> tuple:
        global ench_test_data
        ench = choice(list(ench_test_data['enchantments']))
        description_substitution = {'ench': Translate(self._guild_id, ('ench', 'enchantments', ench)).string()}
        number = ench_test_data['enchantments'][ench]['max_level']
        numbers = sample(range(1, 6), _test_options_number)
        if number not in numbers:
            numbers[0] = number
        numbers.sort()
        answer_index = numbers.index(number)
        answer_options_lang_path = [('roman_numerals', str(i)) for i in numbers]
        return description_substitution, answer_options_lang_path, answer_index, False

    def max_table_ench_lvl(self) -> tuple:
        global ench_test_data
        ench = choice(list(ench_test_data['enchantments']))
        description_substitution = {'ench': Translate(self._guild_id, ('ench', 'enchantments', ench)).string()}
        number = ench_test_data['enchantments'][ench]['max_ench_table_level']
        numbers = sample(range(0, 6), _test_options_number)
        if number not in numbers:
            numbers[0] = number
        numbers.sort(key=lambda x: x if x != 0 else 100)
        answer_index = numbers.index(number)
        answer_options_lang_path = [('roman_numerals', str(i)) for i in numbers]
        if numbers[-1] == 0:
            answer_options_lang_path[-1] = ('messages', 'tests', 'impossible')
        return description_substitution, answer_options_lang_path, answer_index, False

    def get_ench_item(self) -> tuple:
        global ench_test_data
        enchs = ench_test_data['enchantments']
        enchantments = list(ench_test_data['enchantments'])
        enchantments.remove('curse_of_vanishing')
        ench = choice(enchantments)
        description_substitution = {'ench': Translate(self._guild_id, ('ench', 'enchantments', ench)).string()}
        ench_items = set(enchs[ench]['primary_ench_items']) | set(enchs[ench]['secondary_ench_items'])
        available_items = list(set(ench_test_data['items']) - ench_items)
        items = sample(available_items, 2)
        answer_index = randrange(3)
        items.insert(answer_index, choice(list(ench_items)))
        answer_options_lang_path = [('ench', 'items', str(i)) for i in items]
        return description_substitution, answer_options_lang_path, answer_index, False

    def get_table_ench_item(self) -> tuple:
        global ench_test_data
        enchs = ench_test_data['enchantments']
        ench = choice(list(enchs))
        description_substitution = {'ench': Translate(self._guild_id, ('ench', 'enchantments', ench)).string()}
        ench_items = set(enchs[ench]['primary_ench_items'])
        available_items = list(set(ench_test_data['items']) - ench_items)
        item1_index = randrange(len(available_items))
        items = [available_items.pop(item1_index)]
        if ench_items:
            item2 = sample(available_items + [None], 1, counts=[1] * len(available_items) + [8])[0]
            if item2 is None:
                answer_index = randrange(2)
                items.insert(answer_index, choice(list(ench_items)))
                items.append(item2)
            else:
                items.append(item2)
                answer_index = randrange(3)
                items.insert(answer_index, choice(list(ench_items)))
        else:
            items.append(choice(available_items))
            items.append(None)
            answer_index = 2
        answer_options_lang_path = []
        for i in items:
            if i is None:
                answer_options_lang_path.append(('messages', 'tests', 'no_such_item'))
            else:
                answer_options_lang_path.append(('ench', 'items', str(i)))
        return description_substitution, answer_options_lang_path, answer_index, False


class EnchTest:
    def __init__(self, guild_id: int, member_id: int, questions_count: int):
        self._guild_id = guild_id
        self._member_id = member_id
        questions = []
        if questions_count != 1:
            for i in range(1, questions_count + 1):
                questions.append(Question(guild_id, i))
        else:
            questions.append(Question(guild_id, 0))
        self.some_questions = questions_count != 1
        self.message_id: Optional[int] = None
        self.index: int = 0
        self.questions_loop: bool = False
        self.questions: list[Question] = questions
        self.right: int = 0
        self.wrong: int = 0
        self.questions_count: int = questions_count

    async def answer_question(self, correct: bool):
        message = await get_school_message(self._guild_id, self._member_id, self.message_id)
        embed = message.embeds[0]
        if correct:
            self.right += 1
            embed.colour = 65_280
            await message.add_reaction('✅')
        else:
            self.wrong += 1
            embed.colour = 16_711_680
            await message.add_reaction('❌')
        await message.edit(embed=embed)
        del self.questions[self.index]
        if len(self.questions) == 0:
            await self.finish_ench()
        else:
            if len(self.questions) == self.index:
                self.index = 0
                self.questions_loop = True
            await self.print_question()

    async def reaction(self, message_id, emoji):
        if message_id == self.message_id:
            if emoji in _question_numbers:
                answer_index = _question_numbers.index(emoji)
                correctness = answer_index == self.questions[self.index].answer_index
                await self.answer_question(correctness)
            elif emoji in _question_changers:
                delta = 2 * _question_changers.index(emoji) - 1
                await self.change_question(delta)

    async def finish_ench(self):
        if self.some_questions:
            counts = [self.right, self.wrong]
            unanswered = self.questions_count - sum(counts)
            strings = ['✅', '❌']
            if unanswered:
                counts.append(unanswered)
                strings.append('❔')
            results = formatted_results(counts, strings)
            fields = [{'name': value, 'value': line, 'inline': False} for value, line in results]
            embed_dict = {'title': Translate(self._guild_id, ('messages', 'tests', 'you_answered')).string(),
                          'color': 16744192, 'fields': fields}
            school = get_school(self._guild_id, self._member_id)
            await school.send(f'<@{self._member_id}>', embed=discord.Embed.from_dict(embed_dict))

    async def resume_ench(self):
        try:
            last_message = await get_school_message(self._guild_id, self._member_id, self.message_id)
            await last_message.delete()
        except (AttributeError, discord.NotFound):
            pass
        await self.print_question()

    async def print_question(self):
        global _question_numbers
        school = get_school(self._guild_id, self._member_id)
        embed = discord.Embed.from_dict(self.questions[self.index].embed_dict)
        questions_amount = len(self.questions)
        reactions = list(_question_numbers)
        if questions_amount != 1:
            if self.index != 0 or self.questions_loop:
                embed.add_field(name='⬅️', value=Translate(self._guild_id, 'messages.tests.previous_question').string(),
                                inline=True)
                reactions.insert(0, '⬅️')
            embed.add_field(name='➡️', value=Translate(self._guild_id, 'messages.tests.next_question').string(),
                            inline=True)
            reactions.append('➡️')
        msg = await school.send(f'<@{self._member_id}>', embed=embed)
        self.message_id = msg.id
        await fill_reactions(msg, reactions)

    async def change_question(self, delta: int):
        global _question_numbers, _question_changers
        questions_amount = len(self.questions)
        new_question_index = (self.index + delta) % questions_amount
        self.questions_loop = self.questions_loop or (self.index + delta == questions_amount)
        self.index = new_question_index
        embed = discord.Embed.from_dict(self.questions[new_question_index].embed_dict)
        reactions = list(_question_numbers + _question_changers[1:2])
        if (new_question_index != 0 or self.questions_loop) and questions_amount != 1:
            embed.add_field(name='⬅️', value=Translate(self._guild_id, 'messages.tests.previous_question').string(),
                            inline=True)
            reactions.insert(0, '⬅️')
        embed.add_field(name='➡️', value=Translate(self._guild_id, ('messages', 'tests', 'next_question')).string(),
                        inline=True)
        embed.add_field(name=Translate(self._guild_id, ('messages', 'tests', 'question_for')).string(),
                        value=f'<@{self._member_id}>', inline=True)
        message = await get_school_message(self._guild_id, self._member_id, self.message_id)
        await message.edit(embed=embed)
        await fill_reactions(message, reactions)


class Tests(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @Checks.in_guild_school()
    async def test(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            if not ctx.subcommand_passed:
                raise commands.BadArgument
            else:
                await self.test_list(ctx)

    @test.command(name='list')
    async def test_list(self, ctx: commands.Context):
        await ctx.send(Translate(ctx.guild.id, ('messages', 'lists', 'tests'), dict(list=", ".join(_tests))).string())

    @test.command(name='finish')
    @Checks.is_testing()
    async def test_finish(self, ctx: commands.Context):
        global data
        testers = data.guilds[ctx.guild.id].members[ctx.author.id].tests.testers
        for i in testers:
            tests_data = data.guilds[ctx.guild.id].members[i].tests
            if tests_data.active == 'ENCH':
                await tests_data.test.finish_ench()
            tests_data.finish()

    @test.command(name='resume')
    @Checks.is_testing()
    async def test_resume(self, ctx: commands.Context):
        global data
        await data.guilds[ctx.guild.id].members[ctx.author.id].tests.test.resume_ench()

    @test.command(name='stats')
    async def test_stats(self, ctx: commands.Context):
        raise NothingHere

    @test.group(name='start')
    @Checks.in_guild_school()
    async def test_start(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument

    @test_start.command(name='ench')
    @Checks.is_testing('')
    async def start_ench(self, ctx: commands.Context, count: int = 1):
        global data
        if count > ENCH_TEST_MAX_QUESTIONS_COUNT:
            await ctx.send(Translate(ctx.guild.id, ('messages', 'tests', 'too_many_questions'),
                                     {'count': ENCH_TEST_MAX_QUESTIONS_COUNT}).string())
        elif count <= 0:
            raise commands.BadArgument
        else:
            tests = data.guilds[ctx.guild.id].members[ctx.author.id].tests
            tests.active = 'ENCH'
            tests.school_id = ctx.channel.id
            ench_test = EnchTest(ctx.guild.id, ctx.author.id, count)
            tests.test = ench_test
            await ench_test.print_question()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        global data
        if not user.bot:
            try:
                tests_data = data.guilds[reaction.message.guild.id].members[user.id].tests
                if tests_data.active == 'ench':
                    await tests_data.test.reaction(reaction.message.id, str(reaction))
            except (KeyError, AttributeError):
                pass

    async def cog_before_invoke(self, ctx: commands.Context):
        await party_lifetime(ctx)
