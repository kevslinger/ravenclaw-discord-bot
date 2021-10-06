from discord.ext import commands
from discord.ext.tasks import loop

from datetime import datetime
from utils import logging_utils, google_utils, discord_utils
import constants


class ChecklistCog(commands.Cog, name="Checklist"):
    """Create an Activity Calendar, post 24hr reminders"""
    def __init__(self, bot):
        self.bot = bot
        self.gspread_client = google_utils.create_gspread_client()
        self.main_data_sheet = self.gspread_client.open_by_key(constants.MAIN_SHEET_KEY)

        self.checklist_tab = self.main_data_sheet.worksheet("Monthly Checklist")

    @commands.Cog.listener()
    async def on_ready(self):
        """When discord is connected"""
        self.post_checklist.start()

    def get_checklist(self):
        return "• " + "\n• ".join(self.checklist_tab.col_values(1))

    @loop(hours=1)
    async def post_checklist(self):
        """Post the monthly checklist to mod chat at Noon UTC on the first of every month."""
        utctime = datetime.utcnow()

        # Fuck it I'm shooting for noon UTC on the first of the month
        if utctime.day == 1 and utctime.hour == 12:
            print("Posting monthly checklist to mod-chat")
            checklist = self.get_checklist()
            embed = discord_utils.create_embed()
            embed.add_field(name=f"Welcome to {utctime.strftime('%B')}! Here's your monthly checklist",
                            value=checklist,
                            inline=False)
            # Get ravenclaw mod chat
            mod_chat_channel = await self.bot.get_channel(518227474191220777)
            await mod_chat_channel.send(embed=embed)

    @commands.command(name="monthlychecklist", aliases=["monthchecklist"])
    @commands.has_any_role(
        *constants.MOD_ROLES,
        constants.KEV_SERVER_TESTER_ROLE
    )
    async def monthlychecklist(self, ctx):
        """
        Prints out a list of things to do at the start of every month

        Usage: `~monthlychecklist`
        """
        logging_utils.log_command("monthlychecklist", ctx.channel, ctx.author)

        checklist = self.get_checklist()
        embed = discord_utils.create_embed()
        embed.add_field(name="Monthly Checklist",
                        value=checklist,
                        inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ChecklistCog(bot))
