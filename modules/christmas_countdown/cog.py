import discord
from discord.ext import commands
from discord.ext.tasks import loop

from datetime import datetime, date
import pytz
from utils import logging_utils
from modules.christmas_countdown import christmas_countdown_constants
import constants
from emoji import EMOJI_ALIAS_UNICODE_ENGLISH as EMOJIS


class ChecklistCog(commands.Cog, name="Christmas"):
    """Counts Down to Christmas!"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """When discord is connected"""
        self.announce_christmas.start()

    @loop(hours=1)
    async def announce_christmas(self):
        now = datetime.now(tz=pytz.UTC)

        # Handle the case where exactly christmas or after
        if now.month == 12:
            if now.day == 25:
                # 6am UTC
                if now.hour == 6:
                    embed = discord.Embed(
                        title="IT'S CHRISTMAS!",
                        url="https://www.youtube.com/watch?v=s1LUXQWzCno",
                        description=f"{EMOJIS[':cloud_with_snow:']}{EMOJIS[':snowman:']}{EMOJIS[':Santa_Claus:']} "
                                    f"Merry Christmas, Ravenclaw! "
                                    f"{EMOJIS[':Christmas_tree:']}{EMOJIS[':snowflake:']}{EMOJIS[':cloud_with_snow:']}",
                        color=constants.EMBED_COLOR
                    )
                    channel = self.bot.get_channel(christmas_countdown_constants.COMMON_ROOM_CHANNEL_ID)
                    await channel.send(embed=embed)
                    return
            # Don't do a negative countdown or whatever.
            elif now.day > 25:
                return

        # Only announce starting from Oct 1 to Dec 25
        if now.month >= 10:
            # Announce once a day -- at 6am UTC
            if now.hour == 6:
                delta_time = date(now.year, 12, 25) - now.date()
                embed = discord.Embed(
                    title=f"There are {delta_time.days} sleeps until {EMOJIS[':Santa_Claus:']} Christmas {EMOJIS[':Christmas_tree:']}",
                    url="https://christmascountdown.live/",
                    description=f"{EMOJIS[':snowflake:']}{EMOJIS[':cloud_with_snow:']}{EMOJIS[':deer:']}"
                                f"[Countdown Timer](https://christmascountdown.live/live)"
                                f"{EMOJIS[':bell:']}{EMOJIS[':cloud_with_snow:']}{EMOJIS[':snowflake:']}",
                    color=constants.EMBED_COLOR
                )
                channel = self.bot.get_channel(christmas_countdown_constants.COMMON_ROOM_CHANNEL_ID)
                await channel.send(embed=embed)

    @commands.command(name="christmas")
    async def christmas(self, ctx):
        """Print out a countdown to Christmas

        Usage: `~christmas`"""
        logging_utils.log_command("christmas", ctx.channel, ctx.author)

        now = datetime.now(tz=pytz.UTC)
        delta_time = date(now.year, 12, 25) - now.date()
        embed = discord.Embed(
            title=f"There are {delta_time.days} sleeps until {EMOJIS[':Santa_Claus:']} Christmas {EMOJIS[':Christmas_tree:']}",
            url="https://christmascountdown.live/",
            description=f"{EMOJIS[':snowflake:']}{EMOJIS[':cloud_with_snow:']}{EMOJIS[':deer:']}{EMOJIS[':bell:']}{EMOJIS[':cloud_with_snow:']}{EMOJIS[':snowflake:']}\n"
                        f"Check out the countdown timer [here](https://christmascountdown.live/)",

            color=constants.EMBED_COLOR
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ChecklistCog(bot))
