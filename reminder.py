from nextcord.ext import tasks
from nextcord import slash_command
from nextcord.ext.commands import Bot, Cog, Context, command
from nextcord import Interaction
from datetime import datetime, timedelta
import pytz


async def execute_if_authorized(func, ctx: Context):
    if ctx.author.id in ReminderCog.AUTHORIZED_USERS:
        await func()
    else:
        await ctx.send("You are not authorized to use this command.")

async def execute_slash_cmd_if_authorized(func, interaction: Interaction):
    print(f'USER WHO SENT COMMAND: {interaction.user.id}')
    if (interaction.user.id in ReminderCog.AUTHORIZED_USERS):
        await func()
    else:
        interaction.send('You are not authorized to use this command.')


class ReminderCog(Cog):
    ACTIVE_DEVS = "<@&938959783510294619>"
    AUTHORIZED_USERS = [716199395913105428, 229732075203330049, 581294190328152084, 310860100069883904]

    CHECK_IN_TEMPLATE = (
        "```\n"
        "**What I've done so far:** \n"
        "**What I still have to finish:** \n"
        "**What's blocking me:** \n"
        "```"
    )

    CHECK_OUT_TEMPLATE = (
        "```\n"
        "**What I'll do by the next meeting:** \n"
        "**What I foresee may slow my progress:** \n"
        "**Any feedback on last week's progress or today's meeting**: \n"
        "```"
    )

    @property
    def DEV_CHANNEL(self):
        return self.bot.get_channel(938956251080044608)

    @property
    def CHECK_IN_CHANNEL(self):
        return self.HACK_SESSION_CHANNEL

    @property
    def HACK_SESSION_CHANNEL(self):
        return self.bot.get_channel(942783396042645575)

    @property
    def TEST_CHANNEL(self): 
        return self.bot.get_channel(939658799059451904)
    
    @property
    def TEAM_CHANNEL(self):
        return self.bot.get_channel(1011335776639930468)

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.disabled_this_week = False
        self.active = True
        self.time_shift = timedelta(hours=0)
        self.reminder.start()

    @tasks.loop(seconds=59)
    async def reminder(self):
        if not self.active:
            return
        now = datetime.now(pytz.timezone("America/New_York"))
        now += self.time_shift

        print(f'now: {now}')

        if self.disabled_this_week:
            if is_post_hack_session_time(now):
                self.disabled_this_week = False
                if self.time_shift != timedelta(hours=0):
                    await self.reset_time_shift()
            return

        # (i don't think we do weekly check-ins anymore, commenting out for now -spencer)
        # if is_check_in_time(now):
        #     await self.send_check_in_message()

        if is_hour_before_hack_session(now):
            await self.send_before_hack_session_message()
        elif is_hack_session_time(now):
            await self.send_hack_session_message()
        elif is_post_hack_session_time(now):
            await self.send_check_out_message()
            if self.time_shift != timedelta(hours=0):
                await self.reset_time_shift()
        elif (is_timesheet_reminder_time(now)):
            await self.send_timesheet_reminder()

    async def send_test_alive_message(self):
        await self.TEST_CHANNEL.send('I AM ALIVE')

    async def send_check_in_message(self):
        await self.CHECK_IN_CHANNEL.send(
            f"{self.ACTIVE_DEVS} Week.ly Check-in now!\n"
            "Please check-in with the following template:\n"
        )
        await self.CHECK_IN_CHANNEL.send(self.CHECK_IN_TEMPLATE)

    async def send_before_hack_session_message(self):
        attendance_message = await self.HACK_SESSION_CHANNEL.send(
            f"{self.ACTIVE_DEVS} Week.ly Hack Session in 1 hour! "
            "Please react with ✅ if you can make it, "
            "⌛ if you will be late, and ❌ if you can't make it."
        )
        await attendance_message.add_reaction("✅")
        await attendance_message.add_reaction("⏳")
        await attendance_message.add_reaction("❌")
        modality_message = await self.HACK_SESSION_CHANNEL.send(
            "Additionally, please react with 🧑 if you will be attending in-person "
            "and 💻 if you will be attending remotely."
        )
        await modality_message.add_reaction("🧑")
        await modality_message.add_reaction("💻")

    async def send_hack_session_message(self):
        await self.HACK_SESSION_CHANNEL.send(
            f"{self.ACTIVE_DEVS} Week.ly Hack Session reminder!"
        )

    async def send_check_out_message(self):
        await self.CHECK_IN_CHANNEL.send(
            f"{self.ACTIVE_DEVS} Please check-out with the following template:\n"
        )
        await self.CHECK_IN_CHANNEL.send(self.CHECK_OUT_TEMPLATE)

    async def send_timesheet_reminder(self):
        await self.TEST_CHANNEL.send(
            f'{self.ACTIVE_DEVS} 📅 TimesheetX reminder 💸 — fill out your timesheets before Mon. 10am! '
        )

    async def reset_time_shift(self):
        self.time_shift = timedelta(hours=0)
        await self.CHECK_IN_CHANNEL.send("Time shift has been reset.")

    @reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()


    @slash_command(description="sends a test message to testing channel")
    async def test_command(self, interaction: Interaction):
        async def main():
            await interaction.response.send_message('test command received')

        await execute_slash_cmd_if_authorized(main, interaction)

    @slash_command(description="Activates reminders")
    async def activate(self, interaction: Interaction):
        async def main():
            self.active = True
            await interaction.response.send_message("Activated reminders.")

        await execute_slash_cmd_if_authorized(main, interaction)

    @slash_command(description="Deactivates reminders")
    async def deactivate(self, interaction: Interaction):
        async def main():
            self.active = False
            await interaction.response.send_message("Deactivated reminders.")

        await execute_slash_cmd_if_authorized(main, interaction)

    @slash_command(description="Enables this week's reminders")
    async def enable_this_week(self, interaction: Interaction):
        async def main():
            self.disabled_this_week = False
            await interaction.response.send_message("Enabled this week's reminders.")
            if not self.active:
                await interaction.response.send_message(
                    "Reminders are currently deactivated. "
                    "Please activate reminders if you want to receive reminders this week."
                )

        await execute_slash_cmd_if_authorized(main, interaction)

    @slash_command(description="Disables this week's reminders")
    async def disable_this_week(self, interaction: Interaction):
        async def main():
            self.disabled_this_week = True
            await interaction.response.send_message("Disabled this week's reminders.")

        await execute_slash_cmd_if_authorized(main, interaction)

    @slash_command(description="Sets the time shift")
    async def set_time_shift(self, interaction: Interaction, hours: int):
        async def main():
            self.time_shift = timedelta(hours=hours)
            await interaction.response.send_message(f"Set time shift to {hours} hours.")

        await execute_slash_cmd_if_authorized(main, interaction)



# time.weekday(): Monday is 0, Sunday is 6
# --> For Sun. 4pm meetings, weekday = 6

def is_check_in_time(time: datetime) -> bool:
    return time.weekday() == 5 and time.hour == 18 and time.minute == 0


def is_hour_before_hack_session(time: datetime) -> bool:
    return time.weekday() == 6 and time.hour == 15 and time.minute == 0


def is_hack_session_time(time: datetime) -> bool:
    return time.weekday() == 6 and time.hour == 16 and time.minute == 0

def is_post_hack_session_time(time: datetime) -> bool:
    return time.weekday() == 6 and time.hour == 17 and time.minute == 0

def is_timesheet_reminder_time(time: datetime) -> bool:
    return time.weekday() == 6 and time.hour == 22 and time.minute == 0
