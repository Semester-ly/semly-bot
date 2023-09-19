from discord import ChannelType
from nextcord import Message
from nextcord.ext.commands import Bot, Cog, Context, command
from nextcord.abc import PrivateChannel


class AnonyMessageCog(Cog):
    BOT_ID = 1153740007136305202
    RECEIVER = 581294190328152084

    def __init__(self, bot: Bot):
        self.bot = bot
        self.connections: list[PrivateChannel] = []

    @Cog.listener()
    async def on_message(self, message: Message):
        if (
            message.author.id == self.BOT_ID
            or message.author.id == self.RECEIVER
            or message.channel.type != ChannelType.private
        ):
            return
        channel = await self.bot.fetch_user(self.RECEIVER)
        echo = await channel.send(message.content)

        index = len(self.connections)
        self.connections.append(message.channel)
        await echo.edit(content=f"{index}: {echo.content}")

    @command()
    async def reply(self, ctx: Context, index: int, *, message: str):
        if ctx.message.author.id != self.RECEIVER:
            return
        await self.connections[index].send(message)
