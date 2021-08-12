from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd
import io

import constants
from utils import logging_utils
from modules.subreddit_analysis import reddit_utils, subreddit_analysis_utils
import matplotlib.pyplot as plt
import datetime
import discord
from discord.ext import commands
from dotenv.main import load_dotenv
load_dotenv(override=True)

NUM_DAYS = 31


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
        driver = subreddit_analysis_utils.get_chromedriver()
        # Open redesign reddit first to get the login
        driver.get("https://www.reddit.com/")
        # Okay I honestly have no idea what this is, but I ripped it from the internet to be able to
        # Log in to Reddit using selenium which lets me access r/ravenclaw.
        # Wait until you can see click the login button
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//a[starts-with(@href, 'https://www.reddit.com/login')]"))).click()
        # Reddit login is an iframe not a separate page
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH,"//iframe[starts-with(@src, 'https://www.reddit.com/login')]")))
        # Wait for the username and password options to appear, fill them in, and click login
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@id='loginUsername']"))).send_keys(os.getenv("KEV_REDDIT_USERNAME"))
        driver.find_element(By.XPATH, "//input[@id='loginPassword']").send_keys(os.getenv("KEV_REDDIT_PASSWORD"))
        driver.find_element(By.XPATH, "//button[@class='AnimatedForm__submitButton m-full-width']").click()
        # Sleep for 5 seconds to load the login
        # TODO: How do I use WebDriverWait here?
        time.sleep(5)

        # Open up the traffic stats in old reddit to get a nice table (the new reddit html is hard to work with)
        driver.get("https://old.reddit.com/r/ravenclaw/about/traffic")
        table = driver.find_element_by_xpath("//*[@id=\"traffic-day\"]")

        # The first row of the table has some weird options values so i want to cut those out.
        data = io.StringIO("\n".join(table.text.split('\n')[1:]))
        df = pd.read_csv(data, sep=" ")
        df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)\

        df = df[(df['date'] > (datetime.datetime.now() - datetime.timedelta(days=NUM_DAYS)).strftime('%Y-%m-%d')) &
                (df['date'] < (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))]
        df['date'] = df['date'].dt.strftime('%m-%d')

        df = df.reindex(index=df.index[::-1])
        driver.quit()

        # Now that we got our traffic dataframe, we need to use PRAW
        # TODO: Can we do these tow at the same time?
        reddit = reddit_utils.create_reddit_client()
        subreddit = await reddit.subreddit("ravenclaw")
        submission_frequency_dict = {}
        comment_frequency_dict = {}
        for date in df['date']:
            submission_frequency_dict[date] = 0
            comment_frequency_dict[date] = 0

        async for submission in subreddit.new(limit=None):
            date_created = reddit_utils.convert_reddit_timestamp(submission.created_utc)
            # Only want july and august
            if date_created not in df['date'].values:
                break
            submission_frequency_dict[date_created] += 1
            # if date_created in submission_frequency_dict:
            #     submission_frequency_dict[date_created] += 1
            # else:
            #     submission_frequency_dict[date_created] = 1

        async for comment in subreddit.comments(limit=None):
            date_created = reddit_utils.convert_reddit_timestamp(comment.created_utc)
            if date_created not in df['date'].values:
                break
            if date_created in comment_frequency_dict:
                comment_frequency_dict[date_created] += 1
            else:
                comment_frequency_dict[date_created] = 1

        print(submission_frequency_dict)
        print(comment_frequency_dict)

        fig, ax = plt.subplots()
        ax.plot(range(len(df['uniques'])), df['uniques'], color='k', label="Unique Views")
        ax.set_xlabel('Date')
        ax.set_ylabel('Unique Views')
        ax.set_title('r/ravenclaw Engagement, Last 31 Days')
        # TODO: For now I think we should hardcode values? I think that's better
        # ax.set_ylim([0, df['uniques'].max()+50])
        ax.set_ylim([0, 500])
        ax.set_xlim([0, len(df['uniques'])-1])
        ax.set_xticks(range(0, len(df), 3))
        ax.set_xticklabels(df['date'][::3])
        plt.xticks(rotation=45)
        ax2 = ax.twinx()
        ax2.plot(range(len(submission_frequency_dict)), submission_frequency_dict.values(), color='b', label="Submissions")
        ax2.plot(range(len(comment_frequency_dict)), comment_frequency_dict.values(), color='r', label="Comments")
        # TODO: I think it's better to hardcode limits
        # ax2.set_ylim([0, max(list(comment_frequency_dict.values()) + list(submission_frequency_dict.values()))+50])
        ax2.set_ylim([0, 100])
        ax2.set_ylabel('Submissions/Comments', color='purple')
        plt.legend()
        ax.grid(True)

        # plt.show()
        plt.savefig("Unique_views_over_time.png")
        await ctx.send(file=discord.File('Unique_views_over_time.png'))


def setup(bot):
    bot.add_cog(SubredditAnalysisCog(bot))
