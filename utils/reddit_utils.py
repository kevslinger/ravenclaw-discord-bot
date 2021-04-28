import asyncpraw
import os

def get_reddit_client():
    """Initialize AsyncPraw reddit api"""
    return asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=f"{os.getenv('REDDIT_USERNAME')} Bot",
        username=os.getenv("REDDIT_USERNAME"),
    )