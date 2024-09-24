from reminder import ReminderCog
# from anonymessage import AnonyMessageCog
# from anonypoll import AnonyPollCog
# from execute import ExecuteCog
from nextcord import Intents
from nextcord.ext import commands
from decouple import config

# ints = Intents.default()
# ints.members = True
# bot = commands.Bot(command_prefix="$", intents=ints)
bot = commands.Bot(command_prefix="$")
bot.add_cog(ReminderCog(bot))
# bot.add_cog(AnonyMessageCog(bot))
# bot.add_cog(AnonyPollCog(bot))
# bot.add_cog(ExecuteCog(bot))
bot.run(config('TOKEN'))
