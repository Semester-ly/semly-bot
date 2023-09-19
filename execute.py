from nextcord import Message
from nextcord.ext.commands import Bot, Cog, Context, command


class ExecuteCog(Cog):
    SUPERUSER = 581294190328152084

    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def execute(self, ctx: Context, *, message: str):
        if ctx.message.author.id == self.SUPERUSER:
            try:
                result = eval(message.replace("```", ""))
                await ctx.send(result)
            except Exception as e:
                await ctx.send(str(e))
                raise e from e

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if after.content.startswith(self.bot.command_prefix + self.execute.name):
            context = await self.bot.get_context(after)
            await self.execute(
                context,
                message=after.content[
                    len(self.bot.command_prefix + self.execute.name) + 1 :
                ],
            )
