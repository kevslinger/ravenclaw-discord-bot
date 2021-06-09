import datetime
import time
import constants
import discord
from discord.ext.tasks import loop
from discord.ext import commands
from asyncprawcore.exceptions import AsyncPrawcoreException
from modules.reddit_feed.reddit_post import RedditPost
from utils import reddit_utils
import os

# Reddit feed settings
CHECK_INTERVAL = 5  # seconds to wait before checking again
SUBMISSION_LIMIT = 5  # number of submissions to check


def is_in_guild(guild_id):
	"""Check that command is in a guild"""

	async def predicate(ctx):
		return ctx.guild and ctx.guild.id == guild_id

	return commands.check(predicate)


class RedditFeedCog(commands.Cog, name="Reddit Feed"):
	"""Checks for `resend` command and starts Reddit feed loop to check submissions"""

	def __init__(self, bot):
		self.bot = bot
		self.reddit = reddit_utils.get_reddit_client()

	@commands.Cog.listener()
	async def on_ready(self):
		"""When discord is connected"""
		# Start Reddit loop
		self.reddit_feed.start()

	@commands.command(name="resend")
	@commands.has_permissions(administrator=True)
	@is_in_guild(int(os.getenv("RAVENCLAW_DISCORD_ID")))
	async def resend(self, ctx):
		"""Command to resend the last post again.
		Invoked with ~resend"""
		# log command in console
		print("Received resend command")
		# respond to command
		await ctx.send("Resending last announcement!")
		# check for last submission in subreddit
		subreddit = await self.reddit.subreddit(os.getenv("RAVENCLAW_SUBREDDIT"))
		async for submission in subreddit.new(limit=1):
			# process submission
			subreddit, title, author, message = RedditPost(self.bot, submission).process_post()
			embed = discord.Embed(title=title,
								  description=f"By u/{author}",
								  color=constants.EMBED_COLOR)
			embed.add_field(name=f"New Post in r/{subreddit}!",
							value=message,
							inline=False)
			channel = self.bot.get_channel(int(os.getenv("REDDIT_ANNOUNCEMENTS_CHANNEL_ID")))
			await channel.send(embed=embed)

	@loop(seconds=CHECK_INTERVAL)
	async def reddit_feed(self):
		"""loop every few seconds to check for new submissions"""
		try:
			# check for new submission in subreddit
			subreddit = await self.reddit.subreddit(os.getenv("RAVENCLAW_SUBREDDIT"))
			async for submission in subreddit.new(limit=SUBMISSION_LIMIT):
				# check if the post has been seen before
				if not submission.saved:
					# save post to mark as seen
					await submission.save()
					# process submission
					subreddit, title, author, message = RedditPost(self.bot, submission).process_post()
					embed = discord.Embed(title=title,
										  description=f"By u/{author}",
										  color=constants.EMBED_COLOR)
					embed.add_field(name=f"New Post in r/{subreddit}!",
									value=message,
									inline=False)
					channel = self.bot.get_channel(int(os.getenv("REDDIT_ANNOUNCEMENTS_CHANNEL_ID")))
					await channel.send(embed=embed)
		except AsyncPrawcoreException as err:
			print(f"EXCEPTION: AsyncPrawcoreException. {err}")
			time.sleep(10)

	@reddit_feed.before_loop
	async def reddit_feed_init(self):
		"""print startup info before reddit feed loop begins"""
		print(f"Logged in: {str(datetime.datetime.now())[:-7]}")
		print(f"Timezone: {time.tzname[time.localtime().tm_isdst]}")
		print(f"Subreddit: {os.getenv('RAVENCLAW_SUBREDDIT')}")
		print(f"Checking {SUBMISSION_LIMIT} posts every {CHECK_INTERVAL} seconds")


def setup(bot):
	bot.add_cog(RedditFeedCog(bot))
