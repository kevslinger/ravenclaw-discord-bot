import os
from dotenv.main import load_dotenv
import discord
from discord.ext import commands
load_dotenv(override=True)
import constants
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


def main():
    intents = discord.Intents.default()
    client = commands.Bot(constants.BOT_PREFIX, intents=intents, help_command=None, case_insensitive=True)

    # Get the modules of all cogs whose directory structure is modules/<module_name>/cog.py
    for folder in os.listdir("modules"):
        if os.path.exists(os.path.join("modules", folder, "cog.py")):
            client.load_extension(f"modules.{folder}.cog")

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord.Activity(name="the House Cup", type=5))
        for guild in client.guilds:
            print(f"{client.user.name} has connected to the following guild: {guild.name} (id: {guild.id})")
        

    client.run(DISCORD_TOKEN)
        
if __name__ == '__main__':
    main()
