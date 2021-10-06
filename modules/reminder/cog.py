from discord.ext import commands
from discord.ext.tasks import loop

import pytz
import datetime

from utils import logging_utils, time_utils, google_utils, discord_utils
import constants


class ReminderCog(commands.Cog, name="Subreddit Analysis"):
    """Track engagement with number of posts"""
    def __init__(self, bot):
        self.bot = bot
        self.gspread_client = google_utils.create_gspread_client()
        self.main_data_sheet = self.gspread_client.open_by_key(constants.MAIN_SHEET_KEY)

        self.reminder_tab = self.main_data_sheet.worksheet("Reminders")

    @commands.Cog.listener()
    async def on_ready(self):
        """When discord is connected"""
        self.check_reminders.start()

    @loop(minutes=1)
    async def check_reminders(self):
        """Check the Remindme sheet for all reminders"""
        utctime = datetime.datetime.now(tz=pytz.UTC)

        rows_to_remind = []
        idxs_to_delete = []

        # Server Channel Time Username ID Event
        reminders = self.reminder_tab.get_all_values()
        # Skip header row
        for i, row in enumerate(reminders[1:]):
            deadline_time = time_utils.parse_date(row[3],
                                                  from_tz=row[3].split()[-1],
                                                  to_tz=constants.UTC)
            # Check if it's time to remind the person
            if deadline_time.year != utctime.year or deadline_time.month != utctime.month or deadline_time.day != utctime.day \
                or deadline_time.minute != utctime.minute:
                continue

            # If we're here, that means it's time to announce
            rows_to_remind.append(row)
            idxs_to_delete.append(i)

        for row in rows_to_remind:
            author = self.bot.get_user(int(row[5]))
            channel = self.bot.get_channel(int(row[2]))

            await channel.send(f"{author.mention}, please don't forget to {row[6]}")

        idxs_to_delete = sorted(idxs_to_delete, reverse=True)
        # enumerate is 0-index, but google is 1-index plus we skip header row so we need +2
        for idx in idxs_to_delete:
            self.reminder_tab.delete_row(idx+2)


    @commands.command(name="remindme", aliases=["remind", "reminder"])
    async def remindme(self, ctx, *args):
        """
        Reminds you to do something later. Pick one of days (d), hours (h), minutes (m)

        Usage: `~remindme 24h Take out the trash`
        """
        logging_utils.log_command("remindme", ctx.channel, ctx.author)

        utctime = datetime.datetime.now(tz=pytz.UTC)

        # TODO: I'm being REALLY loose on the arguments here
        if 'd' in args[0]:
            remind_time = utctime + datetime.timedelta(days=int(args[0][:-1]))
        elif 'h' in args[0]:
            remind_time = utctime + datetime.timedelta(hours=int(args[0][:-1]))
        elif 'm' in args[0]:
            remind_time = utctime + datetime.timedelta(minutes=int(args[0][:-1]))
        else:
            embed = discord_utils.create_embed()
            embed.add_field(name=f"{constants.FAILED}!",
                            value="Must supply a unit of time! (e.g. 5d, 24h, 30m)",
                            inline=False)
            await ctx.send(embed=embed)
            return

        self.reminder_tab.append_row([ctx.guild.name, ctx.channel.name, str(ctx.channel.id),
                                      remind_time.strftime(constants.SHEET_DATETIME_FORMAT),
                                      ctx.author.name, str(ctx.author.id), ' '.join(args[1:])])

        embed = discord_utils.create_embed()
        embed.add_field(name=f"{constants.SUCCESS}!",
                        value=f"I will remind you to {' '.join(args[1:])} <t:{int(datetime.datetime.timestamp(remind_time))}:R>",
                        inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ReminderCog(bot))
