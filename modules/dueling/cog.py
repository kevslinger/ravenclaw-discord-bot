import discord
from discord.ext import commands
from discord.ext.tasks import loop
import os
import string
import numpy as np
from utils import google_utils, discord_utils
from modules.dueling import dueling_utils
import constants


class DuelingCog(commands.Cog, name="Dueling"):
    """Answer Harry Potter Trivia Questions!"""
    def __init__(self, bot):
        self.bot = bot
        self.gspread_client = google_utils.create_gspread_client()
        self.sheet = self.gspread_client.open_by_key("1CeilQ3n4szkZunYCOO2T0HNP89PlxOrknIQAgveuXfw")
        self.quotes_tab = self.sheet.worksheet("QuotesDatabase")
        self.quarter_tab = self.sheet.worksheet("QuarterQuestions")

    @commands.command(name="dueling", aliases=["duelinghelp", "duelinginfo"])
    async def dueling(self, ctx):
        """Get info for dueling"""
        print(f"Received dueling from {ctx.channel.name}")
        embed = discord.Embed(title="Welcome to Discord Dueling!",
                              color=constants.EMBED_COLOR,
                              description=f"Get your Harry Potter trivia fill during no-points month right here!\n"
                                          f"We have several commands to give you full control over what kind of game "
                                          f"you want to play!\n\n"
                                          f"**Multiple Choice**: `{ctx.prefix}duelingmc`\n"
                                          f"**Name the BOOK and SPEAKER**: `{ctx.prefix}duelingquote`\n"
                                          f"**Question from specific CATEGORY**:`{ctx.prefix}duelingcat <category>` "
                                          f"(use `{ctx.prefix}duelingcat` for available categories)\n"
                                          f"**Question from specific THEME**:`{ctx.prefix}duelingtheme <theme>` "
                                          f"(use `{ctx.prefix}duelingtheme` for available themes)\n\n"
                                          f"For now, I will always include the answer at the end in spoiler text. Feel "
                                          f"free to put your answer in here, but be sure to cover it with spoiler text! "
                                          f"To use spoiler text, surround your answer with \|\| e.g. \|\|answer\|\|"
                              )
        await ctx.send(embed=embed)

    @commands.command(name="duelingmultiplechoice", aliases=["duelingmc"])
    async def duelingmultiplechoice(self, ctx):
        """Get A Multiple Choice Question"""
        print(f"Received duelingmultiplechoice from {ctx.channel.name}")
        embed = discord_utils.create_embed()
        # Cut off header
        quarter_questions = self.quarter_tab.get_all_values()[1:]
        question = quarter_questions[np.random.choice(range(len(quarter_questions)))]
        # TODO: Hacky way of saying there are not multiple options
        i = 0
        while question[-1] == "":
            print(question)
            question = quarter_questions[np.random.choice(range(len(quarter_questions)))]
            i += 1
            if i >= 100:
                embed.add_field(name=f"{constants.FAILED}!",
                                value=f"Sorry! I was unable to find a multiple choice question. Try again later?")
                await ctx.send(embed=embed)
                return

        multiple_choice = [question[3]] + question[5:]
        np.random.shuffle(multiple_choice)
        embed.add_field(name="THEME",
                        value=question[0],
                        )#inline=False)
        embed.add_field(name="CATEGORY",
                        value=question[1],
                        )#inline=False)
        embed.add_field(name="QUESTION",
                        value=question[2],
                        inline=False)
        embed.add_field(name="CHOICES",
                        # TODO: woof that hardcoded formatting
                        # Some of the answers are ints
                        value="\n".join([f"{letter}.) {str(answer)}" for letter, answer in zip(string.ascii_uppercase, multiple_choice)]))
        embed.add_field(name="ANSWER",
                        value=dueling_utils.format_spoiler_answer(question[3], filler=20),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="duelingquote")
    async def duelingquote(self, ctx):
        """Get a quote and answer the SPEAKER and BOOK"""
        print(f"Received duelingquote from {ctx.channel.name}")
        # Cut off header
        quote_questions = self.quotes_tab.get_all_values()[1:]
        question = quote_questions[np.random.choice(range(len(quote_questions)))]
        embed = discord_utils.create_embed()
        embed.add_field(name="Identify the BOOK and SPEAKER of the following quote",
                        value=question[0],
                        inline=False)
        embed.add_field(name="ANSWER",
                        value=dueling_utils.format_spoiler_answer(question[1]),
                        inline=False)
        embed.add_field(name="HINT (Book)",
                        value=dueling_utils.format_spoiler_answer(question[2], filler=10),
                        inline=False)
        await ctx.send(embed=embed)

    def quarter_tab_get_column(self, column: string):
        """Get all the Unique entries from one column on the QuarterQuestions sheet"""
        # TODO: Hardcoded. Can we search for the header named Category and then use that column instead?
        return np.unique(np.array(self.quarter_tab.get(f"{column}:{column}")[1:]).flatten())

    def quarter_tab_get_question(self, query: str, column: int):
        """Find all questions from a particular theme/category, then pick a question at random"""
        cells = self.quarter_tab.findall(query, in_column=column)
        cell = np.random.choice(cells)
        return self.quarter_tab.row_values(cell.row)

    @commands.command(name="duelingcategory", aliases=["duelingcat"])
    async def duelingcategory(self, ctx, *args):
        """Get Dueling Questions from a particular category!"""
        print(f"Received duelingcategory from {ctx.channel.name}")

        categories = self.quarter_tab_get_column("B")
        user_cat = " ".join(args)
        # No supplied category -- give cats
        if len(args) < 1 or user_cat not in categories:
            embed = discord_utils.create_embed()
            embed.add_field(name="Available Categories",
                            value=", ".join(categories))
            await ctx.send(embed=embed)
            return
        # Find all questions of the given category
        # TODO: Hardcoded
        question = self.quarter_tab_get_question(user_cat, 2)
        embed = discord_utils.create_embed()
        embed.add_field(name="THEME",
                        value=question[0],
                        )#inline=False)
        embed.add_field(name="CATEGORY",
                        value=question[1],
                        )#inline=False)
        embed.add_field(name="QUESTION",
                        value=question[2],
                        inline=False)
        embed.add_field(name="ANSWER",
                        value=dueling_utils.format_spoiler_answer(question[3]),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="duelingtheme")
    async def duelingtheme(self, ctx, *args):
        """Get Dueling Questions from a particular theme!"""
        print(f"Received duelingtheme from {ctx.channel.name}")
        themes = self.quarter_tab_get_column("A")
        user_theme = " ".join(args)
        # No supplied theme -- give themes
        if len(args) < 1 or user_theme not in themes:
            embed = discord_utils.create_embed()
            embed.add_field(name="Available Themes",
                            value=", ".join(themes))
            await ctx.send(embed=embed)
            return
        question = self.quarter_tab_get_question(user_theme, 1)
        embed = discord_utils.create_embed()
        embed.add_field(name="THEME",
                        value=question[0],
                        )#inline=False)
        embed.add_field(name="CATEGORY",
                        value=question[1],
                        )#inline=False)
        embed.add_field(name="QUESTION",
                        value=question[2],
                        inline=False)
        embed.add_field(name="ANSWER",
                        value=dueling_utils.format_spoiler_answer(question[3]),
                        inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DuelingCog(bot))
