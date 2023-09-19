from reminder import ReminderCog
from anonymessage import AnonyMessageCog
from anonypoll import AnonyPollCog
from execute import ExecuteCog
from nextcord import Intents
from nextcord.ext import commands
from decouple import config

ints = Intents.default()
ints.members = True
ints.message_content = True
bot = commands.Bot(command_prefix="$", intents=ints)
bot.add_cog(ReminderCog(bot))
bot.add_cog(AnonyMessageCog(bot))
bot.add_cog(AnonyPollCog(bot))
bot.add_cog(ExecuteCog(bot))
print("Starting bot...")
bot.run(config("TOKEN"))
