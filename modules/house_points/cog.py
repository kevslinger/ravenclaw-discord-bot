import os
import discord
from discord.ext import commands
from utils import discord_utils, google_utils
from modules.house_points import house_points_constants, house_points_utils, text_to_table
from datetime import datetime


class HousePointsCog(commands.Cog, name="House Points"):
    """Gets House Points data"""

    def __init__(self, bot):
        self.bot = bot
        self.client = google_utils.create_gspread_client()
        self.sheet_key = os.getenv("HOUSE_POINTS_SHEET_KEY").replace('\'', '')
        self.spreadsheet = self.client.open_by_key(self.sheet_key)

        self.current_points_sheet = self.spreadsheet.worksheet("Tallies By Category")
        self.history_sheet = self.spreadsheet.worksheet("Past Points")


    @commands.command(name="housepoints")
    async def housepoints(self, ctx, *args):
        """
        Get the Current House Points!
        args (Optional): Month and Year to find historical house points (e.g. April 2015)"""
        print("Received housepoints")
        # If the user does not supply a month/date pair
        if (len(args) < 2) or (' '.join(args[:2]) == datetime.now().strftime('%B %Y')):
            # The points will return as a tensor, so we index 0 to drop the extra dimension
            points = [pts[0] for pts in self.current_points_sheet.batch_get(house_points_constants.CURRENT_HOUSE_POINTS_RANGE)[0]]
            title = f"House Points Totals as of {datetime.now().strftime('%B %d')}"
        # If they do supply args we're going to get the date they supplied.
        else:
            # Only the first two args are relevant (if they supply "Jan 2020 hello" then cut off hello)
            date = ' '.join(args[:2])
            history_sheet_values = self.history_sheet.get_all_values()
            try:
                row = history_sheet_values[[month[1] for month in history_sheet_values].index(date)]
                points = list(filter(lambda x: x != '', row))[1:]
            # Date does not exist in sheet
            except ValueError:
                embed = discord_utils.create_embed()
                # First two rows in the Date column are header/blank
                embed.add_field(name="Error!",
                                value=f"Sorry, I couldn't find {date} in my database. I can tell you the house points from "
                                      f"{history_sheet_values[3][1]} until {datetime.now().strftime('%B %Y')}",
                                inline=False)
                await ctx.send(embed=embed)
                return
            title = f"House Points Totals for {date}"
        # Store all values in a table
        table = text_to_table.TextToTable(['House', 'Points'], [[house, points[i]] for i, house in enumerate(house_points_constants.HOUSES)], None, 14, 9).tableize()
        embed = discord.Embed(title=title,
                              description=f"```{table}```",
                              url=self.spreadsheet.url,
                              color=house_points_utils.get_winner_embed_color([int(pts) for pts in points]))
        await ctx.send(embed=embed)

    @commands.command(name="housepointsbreakdown")
    async def housepointsbreakdown(self, ctx):
        """
        Get the breakdown of current month's points by activity
        """
        print("Received housepointsbreakdown")
        # TODO: Get Eastern Time?
        title = f"House Points Breakdown as of {datetime.now().strftime('%B %d')}"

        # Get the points from the sheet
        # TODO: uses hardcoded cell range lookups. Gets destroyed if the sheet ever changes
        points = self.current_points_sheet.batch_get(house_points_constants.CURRENT_HOUSE_POINTS_RANGE + list(house_points_constants.ACTIVITY_SHEET_RANGE_MAP.values()))
        # The first values we grabbed were the total points, then each by activity
        total_points = [pts[0] for pts in points[0]]
        activity_points = [[activity] +  [pts[0] for pts in points[i+1]] for i, activity in enumerate(house_points_constants.ACTIVITIES)]
        # Convert to a table
        # Last 2 args are for table size
        table = text_to_table.TextToTable(['Activity', 'G', 'H', 'R', 'S'], activity_points, ['Total'] + total_points, 17, 5).tableize()
        embed = discord.Embed(title=title,
                              url=self.spreadsheet.url,
                              description=f"```{table}```",
                              color=house_points_utils.get_winner_embed_color([int(pts) for pts in total_points]))
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(HousePointsCog(bot))