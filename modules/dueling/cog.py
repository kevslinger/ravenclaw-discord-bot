import discord
from discord.ext import commands
import os
import string
import numpy as np
from utils import google_utils, discord_utils, logging_utils
from modules.dueling import dueling_utils, dueling_constants
import constants


class DuelingCog(commands.Cog, name="Dueling"):
    """Answer Harry Potter Trivia Questions!"""
    def __init__(self, bot):
        self.bot = bot
        self.gspread_client = google_utils.create_gspread_client()
        self.sheet = self.gspread_client.open_by_key(os.getenv("DUELING_SHEET_KEY"))
        self.quotes_tab = self.sheet.worksheet("QuotesDatabase")
        self.quarter_tab = self.sheet.worksheet("QuarterQuestions")

    @commands.command(name="dueling", aliases=["duelinghelp", "duelinginfo"])
    async def dueling(self, ctx):
        """Get info for dueling"""
        logging_utils.log_command("dueling", ctx.channel, ctx.author)
        embed = discord.Embed(title="Welcome to Discord Dueling!",
                              color=constants.EMBED_COLOR,
                              description=f"Get your Harry Potter trivia fill during no-points month right here!\n"
                                          f"We have several commands to give you full control over what kind of question "
                                          f"you want!\n\n"
                                          f"**Multiple Choice**: `{ctx.prefix}duelingmc`\n"
                                          f"**Name the BOOK and SPEAKER**: `{ctx.prefix}duelingquote`\n"
                                          f"**Random Question**: `{ctx.prefix}duelingrandom`\n"
                                          f"**Question from specific CATEGORY**:`{ctx.prefix}duelingcat <category>` "
                                          f"(use `{ctx.prefix}duelingcat` for available categories)\n"
                                          f"**Question from specific THEME**:`{ctx.prefix}duelingtheme <theme>` "
                                          f"(use `{ctx.prefix}duelingtheme` for available themes)\n\n"
                                          f"For now, I will always include the answer at the end in spoiler text so you "
                                          f"can check your answer. Feel free to put your answer in here, but be sure to "
                                          f"cover it with spoiler text! To use spoiler text, surround your answer "
                                          f"with \|\| e.g. \|\|answer\|\|"
                              )
        await ctx.send(embed=embed)

    @commands.command(name="duelingmultiplechoice", aliases=["duelingmc"])
    async def duelingmultiplechoice(self, ctx):
        """Get A Multiple Choice Question"""
        logging_utils.log_command("duelingmultiplechoice", ctx.channel, ctx.author)
        embed = discord_utils.create_embed()
        # Cut off header
        quarter_questions = self.quarter_tab.get_all_values()[1:]
        question = quarter_questions[np.random.randint(len(quarter_questions))]
        # TODO: Hacky way of saying there are not multiple options
        i = 0
        while question[-1] == "":
            question = quarter_questions[np.random.randint(len(quarter_questions))]
            i += 1
            if i >= 100:
                embed.add_field(name=f"{constants.FAILED}!",
                                value=f"Sorry! I was unable to find a multiple choice question. Try again later?")
                await ctx.send(embed=embed)
                return

        multiple_choice = [question[3]] + question[5:]
        np.random.shuffle(multiple_choice)
        embed.add_field(name=dueling_constants.THEME,
                        value=question[0],
                        )#inline=False)
        embed.add_field(name=dueling_constants.CATEGORY,
                        value=question[1],
                        )#inline=False)
        embed.add_field(name=dueling_constants.QUESTION,
                        value=question[2],
                        inline=False)
        embed.add_field(name=dueling_constants.CHOICES,
                        # TODO: woof that hardcoded formatting
                        # Some of the answers are ints
                        value="\n".join([f"{letter}.) {str(answer)}" for letter, answer in zip(string.ascii_uppercase, multiple_choice)]))
        embed.add_field(name=dueling_constants.ANSWER,
                        value=dueling_utils.format_spoiler_answer(question[3], filler=20),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="duelingquote")
    async def duelingquote(self, ctx):
        """Get a quote and answer the SPEAKER and BOOK"""
        logging_utils.log_command("duelingquote", ctx.channel, ctx.author)
        # Cut off header
        quote_questions = self.quotes_tab.get_all_values()[1:]
        question = quote_questions[np.random.randint(len(quote_questions))]
        embed = discord_utils.create_embed()
        embed.add_field(name=dueling_constants.QUOTE_PROMPT,
                        value=question[0],
                        inline=False)
        embed.add_field(name=dueling_constants.ANSWER,
                        value=dueling_utils.format_spoiler_answer(question[4]),
                        inline=False)
        embed.add_field(name="HINT (Book)",
                        value=dueling_utils.format_spoiler_answer(question[2], filler=10),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="duelingrandom")
    async def duelingrandom(self, ctx):
        """Give a random question"""
        logging_utils.log_command("duelingrandom", ctx.channel, ctx.author)

        # Cut off headers
        possible_questions = self.quarter_tab.get_all_values()[1:] + self.quotes_tab.get_all_values()[1:]
        question = possible_questions[np.random.randint(len(possible_questions))]
        embed = discord_utils.create_embed()
        # TODO: hardcoded hacked
        if len(question) <= 5:
            # name the quote
            embed.add_field(name=dueling_constants.QUOTE_PROMPT,
                            value=question[0],
                            inline=False)
            embed.add_field(name=dueling_constants.ANSWER,
                            value=dueling_utils.format_spoiler_answer(question[4]),
                            inline=False)
            embed.add_field(name="HINT (Book)",
                            value=dueling_utils.format_spoiler_answer(question[2], filler=10),
                            inline=False)
        else:
            # MC question (do not give MC)
            embed.add_field(name=dueling_constants.THEME,
                            value=question[0],
                            )  # inline=False)
            embed.add_field(name=dueling_constants.CATEGORY,
                            value=question[1],
                            )  # inline=False)
            embed.add_field(name=dueling_constants.QUESTION,
                            value=question[2],
                            inline=False)
            embed.add_field(name=dueling_constants.ANSWER,
                            value=dueling_utils.format_spoiler_answer(question[3]),
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
        logging_utils.log_command("duelingcategory", ctx.channel, ctx.author)

        categories = self.quarter_tab_get_column("B")
        user_cat = " ".join(args)
        # No supplied category -- give cats
        if len(args) < 1 or user_cat not in categories:
            embed = discord_utils.create_embed()
            embed.add_field(name="Available Categories",
                            value="\n".join(categories))
            await ctx.send(embed=embed)
            return
        # Find all questions of the given category
        # TODO: Hardcoded
        question = self.quarter_tab_get_question(user_cat, 2)
        embed = discord_utils.create_embed()
        embed.add_field(name=dueling_constants.THEME,
                        value=question[0],
                        )#inline=False)
        embed.add_field(name=dueling_constants.CATEGORY,
                        value=question[1],
                        )#inline=False)
        embed.add_field(name=dueling_constants.QUESTION,
                        value=question[2],
                        inline=False)
        embed.add_field(name=dueling_constants.ANSWER,
                        value=dueling_utils.format_spoiler_answer(question[3]),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="duelingtheme")
    async def duelingtheme(self, ctx, *args):
        """Get Dueling Questions from a particular theme!"""
        logging_utils.log_command("duelingtheme", ctx.channel, ctx.author)
        themes = self.quarter_tab_get_column("A")
        user_theme = " ".join(args)
        # No supplied theme -- give themes
        if len(args) < 1 or user_theme not in themes:
            embed = discord_utils.create_embed()
            embed.add_field(name="Available Themes",
                            value="\n".join(themes))
            await ctx.send(embed=embed)
            return
        question = self.quarter_tab_get_question(user_theme, 1)
        embed = discord_utils.create_embed()
        embed.add_field(name=dueling_constants.THEME,
                        value=question[0],
                        )#inline=False)
        embed.add_field(name=dueling_constants.CATEGORY,
                        value=question[1],
                        )#inline=False)
        embed.add_field(name=dueling_constants.QUESTION,
                        value=question[2],
                        inline=False)
        embed.add_field(name=dueling_constants.ANSWER,
                        value=dueling_utils.format_spoiler_answer(question[3]),
                        inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DuelingCog(bot))
