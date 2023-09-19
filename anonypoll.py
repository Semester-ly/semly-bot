from collections import Counter, defaultdict
from dataclasses import dataclass, field
from nextcord import ChannelType, Reaction, User, Message, Emoji
from nextcord.ext.commands import Bot, Cog, Context, command


@dataclass
class Report:
    message: Message
    emojis: Counter[Emoji] = field(default_factory=Counter)

    def increment(self, emoji: Emoji):
        self.emojis[emoji] += 1

    def decrement(self, emoji: Emoji):
        self.emojis[emoji] -= 1

    async def update_report(self):
        await self.message.edit(content=self.generate_report())

    def generate_report(self) -> str:
        emojis = "\n".join(
            list(
                map(lambda e, c: f"{e}: {c}", self.emojis.keys(), self.emojis.values())
            )
        )
        return f"{self.message.content}\n{emojis}"


class AnonyPollCog(Cog):
    BOT_ID = 1153740007136305202
    RECEIVER = 581294190328152084
    ACTIVE_DEVS = 938959783510294619
    SERVER = 938956251080044605

    def __init__(self, bot: Bot):
        """
        polls: Poll Message -> Response Messages
        responses: Response Message -> Report
        """
        self.bot = bot
        self.polls: dict[Message, list[Message]] = defaultdict(list)
        self.responses: dict[Message, Report] = {}

    @command()
    async def poll(self, ctx: Context, *, poll: str):
        if ctx.author.id != self.RECEIVER:
            return await ctx.send("You aren't allowed to use this command.")
        results = await ctx.send(f"Results for {poll}:")
        report = Report(results)
        for dev in self.get_active_devs():
            if dev.id != self.RECEIVER:
                message = await dev.send(poll)
                self.polls[ctx.message].append(message)
                self.responses[message] = report

    def get_active_devs(self):
        return filter(
            lambda m: m.get_role(self.ACTIVE_DEVS),
            self.bot.get_guild(self.SERVER).members,
        )

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: User):
        if self.is_invalid_reaction(reaction, user):
            return
        if user.id == self.RECEIVER:
            await self.add_to_responses(reaction)
        else:
            await self.add_to_report(reaction)

    def is_invalid_reaction(self, reaction: Reaction, user: User):
        return (
            user.id == self.BOT_ID
            or reaction.message.channel.type != ChannelType.private
            or (
                reaction.message not in self.polls
                and reaction.message not in self.responses
            )
        )

    async def add_to_responses(self, reaction: Reaction):
        for response in self.polls[reaction.message]:
            await response.add_reaction(reaction.emoji)

    async def add_to_report(self, reaction: Reaction):
        report = self.responses[reaction.message]
        report.increment(reaction.emoji)
        await report.update_report()

    @Cog.listener()
    async def on_reaction_remove(self, reaction: Reaction, user: User):
        if self.is_invalid_reaction(reaction, user):
            return
        if user.id == self.RECEIVER:
            await self.remove_from_responses(reaction)
        else:
            await self.remove_from_report(reaction)

    async def remove_from_responses(self, reaction: Reaction):
        for response in self.polls[reaction.message]:
            await response.remove_reaction(reaction.emoji, self.bot.user)

    async def remove_from_report(self, reaction):
        report = self.responses[reaction.message]
        report.decrement(reaction.emoji)
        await report.update_report()

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before in self.polls:
            for response in self.polls[before]:
                await response.edit(content=after.content)

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        if message in self.polls:
            for response in self.polls[message]:
                await response.delete()
                del self.responses[response]
            del self.polls[message]
