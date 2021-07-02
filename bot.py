import os
from dotenv.main import load_dotenv
import discord
from discord.ext import commands
load_dotenv(override=True)
import constants
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


def main():
    intents = discord.Intents.default()
    intents.members = True
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


    @client.event
    async def on_member_update(before, after):
        # Get the guild the member is updating their profile in (since the bot belongs to multiple guilds)
        guild = after.guild
        # If it isn't in the ravenclaw server, we don't care
        if guild.id != int(os.getenv("RAVENCLAW_DISCORD_ID")):
            return
        # Make sure they did not have the ravenclaw role and are adding it now
        if int(os.getenv("RAVENCLAW_DISCORD_ROLE_ID")) not in [role.id for role in before.roles] and \
                int(os.getenv("RAVENCLAW_DISCORD_ROLE_ID")) in [role.id for role in after.roles]:
            # Get the-tower, where we want to put the message
            welcome_channel = guild.get_channel(int(os.getenv("RAVENCLAW_THE_TOWER_CHANNEL_ID")))
            # Send the message to the tower
            if welcome_channel:
                await welcome_channel.send(
                    f"Welcome to {guild.name.capitalize()}, {after.mention}!")
            else:
                print("Error, Could not find welcome channel")


    client.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
