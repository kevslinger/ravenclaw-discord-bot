# What do I want?
# ~casino should give you a help screen basically which tells you which games are avialable
# blackjack
# slots
# reacting to the help should open up the casino game selected.

# Want: Keep track of how much money the channel has?

# TODO: React to own message to help users

import os
from discord.ext import commands
from utils import discord_utils, google_utils
from modules.casino import casino_constants, slots
from emoji import EMOJI_ALIAS_UNICODE_ENGLISH as EMOJIS
import time


class CasinoCog(commands.Cog, name="Casino"):
    """Opens up the Casino"""

    def __init__(self, bot):
        self.bot = bot
        self.client = google_utils.create_gspread_client()
        self.sheet_key = os.getenv("CASINO_SHEET_KEY").replace('\'', '')
        self.sheet = self.client.open_by_key(self.sheet_key).sheet1

        self.cashsheet = google_utils.get_dataframe_from_gsheet(self.sheet, casino_constants.COLUMNS)

    def __del__(self):
        print(self.sheet)
        print(self.cashsheet)
        google_utils.update_sheet_from_df(self.sheet, self.cashsheet)
        time.sleep(10)


    @commands.command(name="casino")
    async def casino(self, ctx):
        """Command to start the casino! Shows a help message with games to play."""
        print("Received casino")

        names = ["Welcome",
                 "Games!",
                 #f"{casino_constants.BLACKJACK}",
                 f"{casino_constants.SLOTS}"]
        values = [f"Welcome to the Casino!",
                  f"We have {len(casino_constants.GAMES)} games for you: {casino_constants.BLACKJACK} and {casino_constants.SLOTS}",
                  #f"React with {casino_constants.BLACKJACK_EMOJI_DISCORD} to play {casino_constants.BLACKJACK}!",
                  f"React with {casino_constants.SLOTS_EMOJI_DISCORD} to play {casino_constants.SLOTS}!"]
        embed = discord_utils.populate_embed(names, values)
        msg = await ctx.send(embed=embed)
        for emoji in casino_constants.EMOJIS:
            await msg.add_reaction(EMOJIS[emoji])

    # TODO: You can't just do the slots on every slot machine react
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle a reaction being added"""
        if reaction.me and reaction.count < 2:
            return
        msg = reaction.message
        channel = msg.channel
        if reaction.emoji == EMOJIS[casino_constants.BLACKJACK_EMOJI_DISCORD]:
            await channel.send(f"I see you want to play blackjack")
        elif reaction.emoji == EMOJIS[casino_constants.SLOTS_EMOJI_DISCORD]:
            if user.id not in self.cashsheet[casino_constants.ID]:
                self.cashsheet = self.cashsheet.append({casino_constants.ID: user.id,
                                                        casino_constants.NAME: user.name,
                                                        casino_constants.BALANCE: casino_constants.OPENING_BALANCE,
                                                        casino_constants.NUM_BUYINS: 0},
                                                       ignore_index=True)
                google_utils.update_sheet_from_df(self.sheet, self.cashsheet)
            print(self.cashsheet[casino_constants.NAME])
            slots_obj = slots.Slots()
            result = slots_obj()
            embed = discord_utils.create_embed()
            embed.add_field(name="Slots!",
                            value=result,
                            inline=False)
            await channel.send(embed=embed)
        else:
            await msg.add_reaction(reaction.emoji)

class Blackjack:
    def __init__(self):
        pass


def setup(bot):
    bot.add_cog(CasinoCog(bot))
