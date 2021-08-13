import asyncpraw
import os
import datetime


def create_reddit_client(user: str="BOT"):
    """Initialize AsyncPraw reddit api

    UPDATE: added optional user arg so I can switch between
    the bot's reddit account and my own (used for traffic stats"""
    return asyncpraw.Reddit(
        client_id=os.getenv(f"{user}_REDDIT_CLIENT_ID"),
        client_secret=os.getenv(f"{user}_REDDIT_CLIENT_SECRET"),
        password=os.getenv(f"{user}_REDDIT_PASSWORD"),
        user_agent=f"{os.getenv(f'{user}_REDDIT_USERNAME')} Bot",
        username=os.getenv(f"{user}_REDDIT_USERNAME"),
    )


def convert_reddit_timestamp(time) -> str:
    """Convert from unix time to a datetime object"""
    return datetime.datetime.utcfromtimestamp(int(time))
