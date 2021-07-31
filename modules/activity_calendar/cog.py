from discord.ext import commands
from discord.ext.tasks import loop
from modules.activity_calendar import activity_calendar_constants, activity_calendar_utils
from utils import google_utils, discord_utils, logging_utils

import constants
import discord
from datetime import datetime

# TODO: filter by activity

class ActivityCalendarCog(commands.Cog, name="Activity Calendar"):
    """Create an Activity Calendar, post 24hr reminders"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gspread_client = google_utils.create_gspread_client()
        self.activity_calendar_sheet = self.gspread_client.open_by_key(activity_calendar_constants.ACTIVITY_CALENDAR_SHEET_KEY).sheet1

    # Reload the google sheet every hour
    @commands.Cog.listener()
    async def on_ready(self):
        """When discord is connected"""
        self.announce_activities.start()

    @loop(hours=1)
    async def announce_activities(self):
        print("Announcing activities")
        utctime = datetime.utcnow()
        # Get first column of google sheet
        # TODO: avoid hardcoding? Have multiple announcement channels for each server?
        server_calendar_results = self.activity_calendar_sheet.findall("ravenclaw", in_column=activity_calendar_constants.SHEET_SERVER_COLUMN)
        rows_to_announce = []
        idxs_to_delete = []
        for i, cell in enumerate(server_calendar_results):
            row = self.activity_calendar_sheet.row_values(cell)
            deadline_time = activity_calendar_utils.parse_date(row[activity_calendar_constants.SHEET_TIMESTAMP_COLUMN],
                                                           from_tz=row[1].split()[-1],
                                                           to_tz=activity_calendar_constants.UTC)
            print(f"Activity: {row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN]}, date: {deadline_time}, now: {utctime}")

            # Check that we are 24 hours away from the event.
            if deadline_time.day - utctime.day == 1 and deadline_time.hour - utctime.hour == 0:
                rows_to_announce.append(row)
            # Delete all rows which have already happened
            if deadline_time.month < utctime.month or (deadline_time.month == utctime.month and deadline_time.day - utctime.day < 0):
                idxs_to_delete.append(i)

        if len(rows_to_announce):
            description = ""
            for row in rows_to_announce:
                description += f"\n\n[{row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN]}]({row[activity_calendar_constants.SHEET_LINK_COLUMN]})"
            embed = discord.Embed(title=f"24 Hour Warning for the following activities!",
                                  description=description,
                                  color=constants.EMBED_COLOR)
            channel = self.bot.get_channel(activity_calendar_constants.ACTIVITY_CALENDAR_CHANNEL_ID)
            await channel.send(embed=embed)
        # Rows are 1-indexed, but enumerate is 0-indexed
        for idx in idxs_to_delete:
            self.activity_calendar_sheet.delete_row(idx+1)

    # TODO: More lenient argument parsing
    @commands.command(name="addactivity", aliases=["aactivity"])
    async def addactivity(self, ctx: commands.Context, *args):
        """Add an activity to the calendar
        ~addactivity Dueling Tuesday, May 11, 2021 7pm EDT https://www.reddit.com/r/Dueling"""
        logging_utils.log_command("addactivity", ctx.channel, ctx.author)
        args = list(args)
        activity = args.pop(0)
        link = args.pop()

        user_time = activity_calendar_utils.parse_date(' '.join(args))
        spreadsheet_time = activity_calendar_utils.parse_date(user_time.strftime(activity_calendar_constants.SHEET_DATETIME_FORMAT), to_tz='UTC')

        embed = discord.Embed(title="Added To Activities Calendar",
                              color=constants.EMBED_COLOR)
        embed.add_field(name="Time", value=user_time.strftime(activity_calendar_constants.DISPLAY_DATETIME_FORMAT),inline=False)
        embed.add_field(name="Activity", value=f"{activity}", inline=False)
        embed.add_field(name="Link", value=link, inline=False)
        await ctx.send(embed=embed)

        self.activity_calendar_sheet.append_row([ctx.guild.name, spreadsheet_time.strftime(activity_calendar_constants.SHEET_DATETIME_FORMAT), activity, link])
        self.activity_calendar_sheet.sort((activity_calendar_constants.SHEET_TIMESTAMP_COLUMN, 'asc'))

    @commands.command(name="showactivitycalendar", aliases=["sactivity", "showcalendar", "activities"])
    async def showactivitycalendar(self, ctx, timezone: str = activity_calendar_constants.UTC):
        """Displays the current activity calendar
        Can add a timezone to display the times in that timezone

        ~showactivitycalendar CEST"""
        logging_utils.log_command("showactivitycalendar", ctx.channel, ctx.author)
        server_calendar_results = self.activity_calendar_sheet.findall(ctx.guild.name, in_column=activity_calendar_constants.SHEET_SERVER_COLUMN)
        description = ""
        for cell in server_calendar_results:
            row = self.activity_calendar_sheet.row_values(cell.row)
            date = activity_calendar_utils.parse_date(row[activity_calendar_constants.SHEET_TIMESTAMP_COLUMN],
                                                      from_tz=activity_calendar_constants.UTC,
                                                      to_tz=timezone)
            description += f"\n\n{activity_calendar_utils.replace_offset(date.strftime(activity_calendar_constants.DISPLAY_DATETIME_FORMAT))}: " \
                           f"[{row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN]}]({row[activity_calendar_constants.SHEET_LINK_COLUMN]})"
        embed = discord.Embed(title="Current Activity Calendar",
                              description=description,
                              color=constants.EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.command(name="showweekcalendar", aliases=["showweek"])
    async def showweekcalendar(self, ctx, timezone: str = activity_calendar_constants.UTC):
        """Show the calendar for the next 7 days

        ~showweekcalendar EDT"""
        logging_utils.log_command("showweekcalendar", ctx.channel, ctx.author)

        server_calendar_results = self.activity_calendar_sheet.findall(ctx.guild.name, in_column=activity_calendar_constants.SHEET_SERVER_COLUMN)
        description = ""
        current_date = activity_calendar_utils.parse_date(datetime.utcnow().strftime(activity_calendar_constants.SHEET_DATETIME_FORMAT),
                                                          from_tz=activity_calendar_constants.UTC,
                                                          to_tz=timezone)
        for cell in server_calendar_results:
            row = self.activity_calendar_sheet.row_values(cell.row)
            date = activity_calendar_utils.parse_date(row[activity_calendar_constants.SHEET_TIMESTAMP_COLUMN],
                                                      from_tz=activity_calendar_constants.UTC,
                                                      to_tz=timezone)

            if date.day - current_date.day <= 7:
                description += f"\n\n{activity_calendar_utils.replace_offset(date.strftime(activity_calendar_constants.DISPLAY_DATETIME_FORMAT))}: " \
                               f"[{row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN]}]({row[activity_calendar_constants.SHEET_LINK_COLUMN]})"

        embed = discord.Embed(title=f"Activity Calendar for Week of {current_date.strftime('%B %d')}",
                              description=description,
                              color=constants.EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.command(name="deleteactivity", aliases=["dactivity"])
    async def deleteactivity(self, ctx, *args):
        """Remove all instances of activity from the calendar

        ~deleteactivity Dueling"""
        logging_utils.log_command("deleteactivity", ctx.channel, ctx.author)

        activity = ' '.join(args)
        result_cells = self.activity_calendar_sheet.findall(activity, in_column=activity_calendar_constants.SHEET_ACTIVITY_COLUMN)
        print(result_cells)
        for cell in result_cells:
            self.activity_calendar_sheet.delete_row(cell.row)
        embed = discord_utils.create_embed()
        embed.add_field(name="Success",
                        value=f"Deleted {len(result_cells)} instances of {activity} from the calendar.",
                        inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ActivityCalendarCog(bot))
