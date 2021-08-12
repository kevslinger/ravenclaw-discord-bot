import asyncpraw
import os
from datetime import datetime


def create_reddit_client() -> asyncpraw.Reddit:
    """Initialize AsyncPraw reddit api"""
    return asyncpraw.Reddit(
        client_id=os.getenv("KEV_REDDIT_CLIENT_ID"),
        client_secret=os.getenv("KEV_REDDIT_CLIENT_SECRET"),
        password=os.getenv("KEV_REDDIT_PASSWORD"),
        user_agent=f"{os.getenv('KEV_REDDIT_USERNAME')} Bot",
        username=os.getenv("KEV_REDDIT_USERNAME"),
    )


def get_formatted_time() -> str:
    """Get time and format it to be human readable

    This prints out as e.g. September 22, 2015 08:30:59"""
    return datetime.strftime(datetime.now(), '%B %d, %Y %H:%M:%S')


def convert_reddit_timestamp(time) -> str:
    """Convert from unix time to human-readable

    Prints out as e.g. 09-29-1970 22:38:58"""
    return datetime.utcfromtimestamp(int(time)).strftime('%m-%d')
