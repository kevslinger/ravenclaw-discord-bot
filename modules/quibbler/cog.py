from discord.ext import commands
import discord
from modules.quibbler import quibbler_constants
from utils import logging_utils
import constants


class QuibblerCog(commands.Cog, name="Quibbler"):
    """Information about The Quibbler"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quibbler", aliases=["quib"])
    async def quibbler(self, ctx):
        """
        Generic Quibbler info with links to:
            1.) r/TheQuibbler
            2.) The r/TheQuibbler submission form
            3.) The Issue profile page where all the quibbler's are stored
            4.) The Google Doc which has prompts for inspiration

        ~quib
            """
        logging_utils.log_command("quibbler", ctx.channel, ctx.author)
        description = f"The Quibbler is a light-hearted, quirky, facts-optional online magazine where creativity " \
                      f"and wit are prized over accuracy and factuality. We exist to put smiles on peoples' faces, " \
                      f"including our own! New editions are published quarterly on our [Issuu page]({quibbler_constants.ISSUU_LINK})" \
                      f"\n\nJoin [r/TheQuibbler]({quibbler_constants.SUBREDDIT_LINK})" \
                      f"\n\nAll submissions go to this [Google Form]({quibbler_constants.SUBMISSION_LINK})" \
                      f"\n\nCheck out our inspiration prompt [Google Doc]({quibbler_constants.PROMPT_LIST_LINK})" \
                      f"\n\nFor more information, take a look at r/TheQuibbler's [Wiki]({quibbler_constants.SUBREDDIT_WIKI_LINK})"
        embed = discord.Embed(title=f"r/TheQuibbler Information and Links",
                              color=constants.EMBED_COLOR,
                              description=description)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(QuibblerCog(bot))
