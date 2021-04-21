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
        # TODO: Add something like ~housepoints May 2020
        #self.history_sheet = self.spreadsheet.worksheet("Past Points")


    @commands.command(name="housepoints")
    async def housepoints(self, ctx):
        """Get the Current House Points!"""
        print("Received housepoints")

        # The points will return as a tensor, so we index 0 to drop the extra dimension
        points = self.current_points_sheet.batch_get(house_points_constants.CURRENT_HOUSE_POINTS_RANGE)[0]
        points_str = [f"{house}: {points[idx][0]}" for idx, house in enumerate(house_points_constants.HOUSES)]
        embed = discord.Embed(title=f"House Points Totals as of {datetime.now().strftime('%B %d')}",
                              description=f"{chr(10).join(points_str)}",
                              url=self.spreadsheet.url,
                              color=house_points_utils.get_winner_embed_color([int(pts[0]) for pts in points]))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HousePointsCog(bot))