import discord
from discord.ext import commands
from utils import logging_utils, reddit_utils
from modules.subreddit_analysis import subreddit_analysis_constants
import matplotlib.pyplot as plt
import constants
import datetime





class SubredditAnalysisCog(commands.Cog, name="Subreddit Analysis"):
    """Track engagement with number of posts"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="subredditanalysis", aliases=["sra", "engagement"])
    @commands.has_any_role(
        *constants.MOD_ROLES,
        constants.KEV_SERVER_TESTER_ROLE
    )
    async def subredditanalysis(self, ctx):
        """Mod command. Graphs the number of unique member views on r/ravenclaw and compares with
        number of posts and comments

        ~engagement"""
        logging_utils.log_command("subredditanalysis", ctx.channel, ctx.author)

        # Now that we got our traffic dataframe, we need to use PRAW
        reddit = reddit_utils.create_reddit_client(user=subreddit_analysis_constants.REDDIT_USER_KEV)
        subreddit = await reddit.subreddit(subreddit_analysis_constants.RAVENCLAW_SUBREDDIT)
        stats = await subreddit.traffic()
        unique_pageviews = {}
        utcnow = datetime.datetime.utcnow()
        # stats['day'] gives the traffic stats by day, in format [unixtime, unique, total, # subscribers]
        for row in stats['day']:
            date = reddit_utils.convert_reddit_timestamp(row[0])
            if utcnow - datetime.timedelta(days=subreddit_analysis_constants.NUM_DAYS) < date:
                unique_pageviews[date.strftime(subreddit_analysis_constants.DISPLAYTIME_FORMAT)] = row[1]

        submission_frequency_dict = {}
        comment_frequency_dict = {}
        for date in unique_pageviews.keys():
            submission_frequency_dict[date] = 0
            comment_frequency_dict[date] = 0

        async for submission in subreddit.new(limit=None):
            date_created = reddit_utils.convert_reddit_timestamp(submission.created_utc)\
                .strftime(subreddit_analysis_constants.DISPLAYTIME_FORMAT)
            # Since this is sorted by new, once we get too far beyond our x-axis we can just stop
            if date_created not in unique_pageviews.keys():
                break
            submission_frequency_dict[date_created] += 1

        async for comment in subreddit.comments(limit=None):
            date_created = reddit_utils.convert_reddit_timestamp(comment.created_utc)\
                .strftime(subreddit_analysis_constants.DISPLAYTIME_FORMAT)
            # Since this is sorted by new, once we get too far beyond our x-axis we can just stop
            if date_created not in unique_pageviews.keys():
                break
            comment_frequency_dict[date_created] += 1

        # TODO: Move this plotting code to a util function?
        fig, ax = plt.subplots()
        ax.plot(range(len(unique_pageviews)), unique_pageviews.values(),
                color='k', label="Unique Views")
        ax.set_xlabel('Date')
        ax.set_ylabel('Unique Views')
        ax.set_title('r/ravenclaw Engagement, Last 31 Days')
        # TODO: For now I think we should hardcode values? I think that's better
        # ax.set_ylim([0, df['uniques'].max()+50])
        ax.set_ylim([0, 500])
        ax.set_xlim([0, len(unique_pageviews)-1])
        ax.set_xticks(range(0, len(unique_pageviews), 3))
        ax.set_xticklabels(list(unique_pageviews.values())[::3])
        plt.xticks(rotation=45)
        ax2 = ax.twinx()
        ax2.plot(range(len(submission_frequency_dict)), submission_frequency_dict.values(),
                 color='b', label="Submissions")
        ax2.plot(range(len(comment_frequency_dict)), comment_frequency_dict.values(),
                 color='r', label="Comments")
        # TODO: I think it's better to hardcode limits
        # ax2.set_ylim([0, max(list(comment_frequency_dict.values()) + list(submission_frequency_dict.values()))+50])
        ax2.set_ylim([0, 100])
        ax2.set_ylabel('Submissions/Comments', color='purple')
        plt.legend()
        ax.grid(True)

        plt.savefig("Unique_views_over_time.png")
        await ctx.send(file=discord.File('Unique_views_over_time.png'))


def setup(bot):
    bot.add_cog(SubredditAnalysisCog(bot))
