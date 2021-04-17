class RedditPost:
	def __init__(self, bot, post):
		self.bot = bot
		self.post = post

	def process_post(self):
		"""check post and announce if not saved"""
		# log post details in console
		print(f"Recieved post by {self.post.author}")
		# create message with url and text
		title, message = self.__build_message()
		return self.post.subreddit, title, self.post.author, message

	def __trim_text(self, text, limit=97):
		"""trim text if over limit of characters"""
		if len(text) > limit:
			# trim text if over limit of characters
			return text[:limit] + "..."
		# otherwise, return original
		return text

	def __build_message(self):
		"""build message from post"""
		# get url and selftext
		title = self.__trim_text(self.post.title)
		url = f"https://www.reddit.com/r/{self.post.subreddit}/comments/{self.post.id}"
		return title, url
