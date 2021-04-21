import os
import discord
from discord.ext import commands
from utils import discord_utils, google_utils
from modules.house_points import house_points_constants, house_points_utils
from datetime import datetime


class HousePointsCog(commands.Cog, name="House Points"):
    """Gets House Points data"""

    def __init__(self, bot):
        self.bot = bot
        self.client = google_utils.create_gspread_client()
        self.sheet_key = os.getenv("HOUSE_POINTS_SHEET_KEY").replace('\'', '')
        self.spreadsheet = self.client.open_by_key(self.sheet_key)

        self.current_points_sheet = self.spreadsheet.worksheet("Current Points")
        self.history_sheet = self.spreadsheet.worksheet("Past Points")
        self.history_points_df = google_utils.get_dataframe_from_gsheet(self.history_sheet,
                                                                        house_points_constants.HISTORY_COLUMNS)


    @commands.command(name="housepoints")
    async def housepoints(self, ctx, *args):
        """
        Get the Current House Points!
        args (Optional): Month and Year to find historical house points (e.g. April 2015)"""
        print("Received housepoints")
        # If the user does not supply a month/date pair
        if (len(args) < 2) or (' '.join(args[:2]) == datetime.now().strftime('%B %Y')):
            # The points will return as a tensor, so we index 0 to drop the extra dimension
            points = [int(pts[0]) for pts in self.current_points_sheet.batch_get(house_points_constants.CURRENT_HOUSE_POINTS_RANGE)[0]]
            points_str = [f"{house}: {points[idx]}" for idx, house in enumerate(house_points_constants.HOUSES)]
            title = f"House Points Totals as of {datetime.now().strftime('%B %d')}"
        # If they do supply args we're going to get the date they supplied.
        else:
            # Only the first two args are relevant (if they supply "Jan 2020 hello" then cut off hello)
            date = ' '.join(args[:2])
            try:
                points = [int(pts) for pts in self.history_points_df[self.history_points_df['Date'] == date][house_points_constants.HOUSES].iloc[0]]
            # Date does not exist in sheet
            except (IndexError, ValueError):
                embed = discord_utils.create_embed()
                # First two rows in the Date column are header/blank
                embed.add_field(name="Error!",
                                value=f"Sorry, I couldn't find {date} in my database. I can tell you the house points from "
                                      f"{self.history_points_df['Date'].iloc[2]} until {datetime.now().strftime('%B %Y')}",
                                inline=False)
                await ctx.send(embed=embed)
                return
            points_str = [f"{house}: {points[i]}" for i, house in enumerate(house_points_constants.HOUSES)]
            title = f"House Points Totals for {date}"
        embed = discord.Embed(title=title,
                              description=f"{chr(10).join(points_str)}",
                              url=self.spreadsheet.url,
                              color=house_points_utils.get_winner_embed_color([pts for pts in points]))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HousePointsCog(bot))