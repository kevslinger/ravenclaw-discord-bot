from discord.ext import commands
from discord.ext.tasks import loop
from modules.activity_calendar import activity_calendar_constants, activity_calendar_utils
from utils import google_utils, discord_utils, logging_utils, reddit_utils

import constants
import discord
import asyncpraw
from datetime import datetime

# TODO: filter by activity

class ActivityCalendarCog(commands.Cog, name="Activity Calendar"):
    """Create an Activity Calendar, post 24hr reminders"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gspread_client = google_utils.create_gspread_client()
        self.activity_calendar_sheet = self.gspread_client.open_by_key(activity_calendar_constants.ACTIVITY_CALENDAR_SHEET_KEY).sheet1

        self.reddit_client = reddit_utils.create_reddit_client()

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
            # TODO: is there a way we can batch this? I think it's what makes this stuff so slow
            row = self.activity_calendar_sheet.row_values(cell.row)
            # Need the -1 because google sheets is 1-indexed while the lists are 0-indexed
            deadline_time = activity_calendar_utils.parse_date(row[activity_calendar_constants.SHEET_TIMESTAMP_COLUMN-1],
                                                           from_tz=row[activity_calendar_constants.SHEET_TIMESTAMP_COLUMN-1].split()[-1],
                                                           to_tz=activity_calendar_constants.UTC)

            # Check that we are 24 hours away from the event.
            if deadline_time.day - utctime.day == 1 and deadline_time.hour - utctime.hour == 0:
                rows_to_announce.append(row)
            # Delete all rows which have already happened
            if deadline_time.month < utctime.month or (deadline_time.month == utctime.month and deadline_time.day - utctime.day < 0):
                idxs_to_delete.append(i)
        # Only make an announcement when we have something to announce
        if len(rows_to_announce):
            description = ""
            for row in rows_to_announce:
                description += f"\n\n[{row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN-1]}:]({row[activity_calendar_constants.SHEET_LINK_COLUMN-1]})" \
                               f"{row[activity_calendar_constants.SHEET_DESCRIPTION_COLUMN-1]}"
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
        ~addactivity "Dueling" "Harry Potter Trivia!" Tuesday, May 11, 2021 7pm EDT https://www.reddit.com/r/Dueling"""
        logging_utils.log_command("addactivity", ctx.channel, ctx.author)
        # Currently we require the args to be: Activity name, description, date, link
        # They have to use quotes if they want the name or description to be more than 1 word.
        # We pop off the name, description, and link, and what's left is the time.
        # Should we make them put the time in quotes too? Then it would just make things cleaner on the back end
        # I would prefer making it easier to use, though, I guess
        args = list(args)
        activity = args.pop(0)
        description = args.pop(0)
        link = args.pop()

        user_time = activity_calendar_utils.parse_date(' '.join(args))
        # We store all our times in UTC on the spreadsheet
        spreadsheet_time = activity_calendar_utils.parse_date(user_time.strftime(activity_calendar_constants.SHEET_DATETIME_FORMAT), to_tz='UTC')

        embed = discord.Embed(title="Added To Activities Calendar",
                              color=constants.EMBED_COLOR)
        embed.add_field(name="Time", value=user_time.strftime(activity_calendar_constants.DISPLAY_DATETIME_FORMAT), inline=False)
        embed.add_field(name="Activity", value=f"{activity}", inline=False)
        embed.add_field(name="Description", value=f"{description}", inline=False)
        embed.add_field(name="Link", value=link, inline=False)
        await ctx.send(embed=embed)

        self.activity_calendar_sheet.append_row([ctx.guild.name, spreadsheet_time.strftime(activity_calendar_constants.SHEET_DATETIME_FORMAT), activity, description, link])
        self.activity_calendar_sheet.sort((activity_calendar_constants.SHEET_TIMESTAMP_COLUMN, 'asc'))

    @commands.command(name="showactivitycalendar", aliases=["cal", "showcalendar", "activities"])
    async def showactivitycalendar(self, ctx, timezone: str = activity_calendar_constants.UTC):
        """Displays the current activity calendar
        Can add a timezone to display the times in that timezone

        ~showactivitycalendar CEST"""
        logging_utils.log_command("showactivitycalendar", ctx.channel, ctx.author)
        server_calendar_results = self.activity_calendar_sheet.findall(ctx.guild.name, in_column=activity_calendar_constants.SHEET_SERVER_COLUMN)
        description = ""
        for cell in server_calendar_results:
            row = self.activity_calendar_sheet.row_values(cell.row)
            date = activity_calendar_utils.parse_date(row[activity_calendar_constants.SHEET_TIMESTAMP_COLUMN-1],
                                                      from_tz=activity_calendar_constants.UTC,
                                                      to_tz=timezone)
            description += f"\n\n{activity_calendar_utils.replace_offset(date.strftime(activity_calendar_constants.DISPLAY_DATETIME_FORMAT))}: " \
                           f"[{row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN-1]}]({row[activity_calendar_constants.SHEET_LINK_COLUMN-1]})"
        embed = discord.Embed(title="Current Activity Calendar",
                              description=description,
                              color=constants.EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.command(name="showweekcalendar", aliases=["week", "showweek"])
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
            date = activity_calendar_utils.parse_date(row[activity_calendar_constants.SHEET_TIMESTAMP_COLUMN-1],
                                                      from_tz=activity_calendar_constants.UTC,
                                                      to_tz=timezone)
            # Only show activities that are 1 week out
            if date.day - current_date.day <= 7:
                description += f"\n\n{activity_calendar_utils.replace_offset(date.strftime(activity_calendar_constants.DISPLAY_DATETIME_FORMAT))}: " \
                               f"[{row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN-1]}:]({row[activity_calendar_constants.SHEET_LINK_COLUMN-1]})" \
                               f" {row[activity_calendar_constants.SHEET_DESCRIPTION_COLUMN-1]}"

        embed = discord.Embed(title=f"Activity Calendar for Week of {current_date.strftime('%B %d')}",
                              description=description,
                              color=constants.EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.command(name="deleteactivity", aliases=["dactivity"])
    async def deleteactivity(self, ctx, *args):
        """Remove all instances of activity from the calendar

        ~deleteactivity Dueling"""
        logging_utils.log_command("deleteactivity", ctx.channel, ctx.author)
        # In general, I've been adding activities with specifics e.g. "Dueling: Helga Game"
        # If you want to delete only that instance, ~dactivity "Dueling: Helga Game"
        # If you want to delete all dueling activities, ~dactivity Dueling
        activity = ' '.join(args)
        result_cells = self.activity_calendar_sheet.findall(ctx.guild.name, in_column=activity_calendar_constants.SHEET_SERVER_COLUMN)
        num_deletions = 0
        for cell in result_cells:
            row = self.activity_calendar_sheet.row_values(cell.row)
            if activity in row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN-1]:
                self.activity_calendar_sheet.delete_row(cell.row - num_deletions)
                num_deletions += 1
        embed = discord_utils.create_embed()
        embed.add_field(name="Success",
                        value=f"Deleted {num_deletions} instances of {activity} from the calendar.",
                        inline=False)

        await ctx.send(embed=embed)

    # TODO: should this be in the house points module?
    # TODO: PROBABLY
    # TODO: Be able to filter by activity
    # e.g. ~submissions HW only shows HW
    @commands.command(name="submissions", aliases=["submission"])
    async def submissions(self, ctx):
        """Count submissions for homework and extra credit

        ~submissions"""
        logging_utils.log_command("submissions", ctx.channel, ctx.author)

        # Get HW and EC if possible
        result_cells = self.activity_calendar_sheet.findall(ctx.guild.name, in_column=activity_calendar_constants.SHEET_SERVER_COLUMN)
        activity_ids = []
        submission_counts = {}
        for cell in result_cells:
            row = self.activity_calendar_sheet.row_values(cell.row)
            if "Homework:" in row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN-1] or "EC:" in row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN-1]:
                # TODO: pls
                if row[activity_calendar_constants.SHEET_LINK_COLUMN-1] not in [link[2] for link in activity_ids]:
                    activity_ids.append((row[activity_calendar_constants.SHEET_ACTIVITY_COLUMN-1], row[activity_calendar_constants.SHEET_DESCRIPTION_COLUMN-1], row[activity_calendar_constants.SHEET_LINK_COLUMN-1]))

        HOUSES = ["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"]
        # TODO: I'm going to add some hardcoded stuff for Arthur's Artifacts Part 2
        # UPDATE: nobody is putting their house in the comment so I guess I can't
        #arthur_part2_submisssions = [0, 0, 0, 0]
        description = ""
        for activity in activity_ids:
            submission = asyncpraw.models.Submission(self.reddit_client, url=activity[2])
            for comment in await submission.comments():
                for house in HOUSES:
                    if "submit" in comment.body.lower() and house.lower() in comment.body.lower():
                        if activity[0] not in submission_counts:
                            submission_counts[activity[0]] = [0, 0, 0, 0]

                        submission_counts[activity[0]][HOUSES.index(house)] = len(comment.replies)
                        # Hardcoded thing for arthur's part 2
                        # if activity[2] == "https://redd.it/owixx9":
                        #
                        #     for reply in comment.replies:
                        #         for part2_submission in reply.replies:
                        #             print(part2_submission.body)
                        #             if house.lower() in part2_submission.body.lower():
                        #                 arthur_part2_submisssions[HOUSES.index(house)] += 1

            if activity[0] in submission_counts:
                description += f"\n\n**[{activity[0]}:]({activity[2]})** {activity[1]} \n" \
                               f"{chr(10).join([f'{house}: {submissions}' for house, submissions in zip(HOUSES, submission_counts[activity[0]])])}"
        embed = discord.Embed(title="Submission counts for HW and ECs",
                              description=description,
                              color=constants.EMBED_COLOR)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ActivityCalendarCog(bot))
