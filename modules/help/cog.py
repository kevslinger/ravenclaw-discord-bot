from discord.ext import commands
import constants
import discord
from utils import discord_utils
from modules.help import help_constants
from modules.lookup import lookup_constants
from modules.code import code_constants


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def real_help(self, ctx, *args):
        if len(args) < 1:
            embed = discord.Embed(title=f"{help_constants.HELP}",
                                  url="https://github.com/kevslinger/DiscordCipherRace",
                                  color=constants.EMBED_COLOR)
            embed.add_field(name="Welcome!",
                            value=f"Welcome to the help page! We offer the following modules. "
                                  f"Use {constants.BOT_PREFIX}help <module> to learn about "
                                  f"the commands in that module!",
                            inline=False)
            embed.add_field(name=help_constants.CIPHER_RACE,
                            value=f"Race against the clock as you decode ciphers. "
                                  f"Use {constants.BOT_PREFIX}startrace "
                                   "to start a race! "
                                  f"\nRead more on the [GitHub README]({help_constants.CIPHER_RACE_README})",
                            inline=False)
            embed.add_field(name=help_constants.HOUSE_POINTS,
                            value=f"Get the house points standings! "
                                  f"Use {constants.BOT_PREFIX}housepoints to get the "
                                  f"current house points tallies."
                                  f"\nRead more on the [GitHub README]({help_constants.HOUSE_POINTS_README})",
                            inline=False)
            embed.add_field(name=help_constants.LOOKUP,
                            value=f"Search the interwebs (google)!\n"
                                  f"Read more on the [GitHub README]({help_constants.LOOKUP_README})",
                            inline=False)
            embed.add_field(name=help_constants.TIME,
                            value=f"Current time anywhere in the world!\n"
                                  f"Read more on the [GitHub README]({help_constants.TIME_README})",
                            inline=False)
        else:
            module = ' '.join(args).lower()
            if module in MODULE_TO_HELP:
                embed = MODULE_TO_HELP[module]()
            else:
                embed = discord_utils.create_embed()
                embed.add_field(name="Module not found!",
                                value=f"Sorry! Cannot find module {module}. The modules we have are \n"
                                      f"{', '.join(help_constants.MODULES)}",
                                inline=False)
        await ctx.send(embed=embed)


def cipher_race_help():
    embed = discord.Embed(title=f"{help_constants.CIPHER_RACE} {help_constants.HELP}",
                          url=help_constants.CIPHER_RACE_README,
                          color=constants.EMBED_COLOR)
    embed.add_field(name=f"{constants.BOT_PREFIX}startrace",
                    value=f"Starts a race!\n"
                          f"Optional: choose a wordlist (from {', '.join(code_constants.SHEETS)})\n"
                          f"e.g. {constants.BOT_PREFIX}startrace {code_constants.COMMON}",
                    inline=False)
    embed.add_field(name=f"{constants.BOT_PREFIX}answer <your_answer>",
                    value=f"Answer any of the codes during a race! If you are correct, the bot will react with "
                          f"a {code_constants.CORRECT_EMOJI}. Otherwise, it will react with a {code_constants.INCORRECT_EMOJI}",
                    inline=False)
    embed.add_field(name=f"{constants.BOT_PREFIX}practice",
                    value=f"Get a randomly selected word and cipher to decode at your own pace!\n"
                          f"Optional: Choose a cipher from {', '.join(code_constants.CIPHERS)}\n"
                          f"e.g. {constants.BOT_PREFIX}practice {code_constants.PIGPEN}\n"
                          f"Note: the bot will NOT check your answer. When you've solved, check it yourself by "
                          f"uncovering the spoiler text next to the image!",
                    inline=False)
    embed = more_help(embed, help_constants.CIPHER_RACE_README)
    #TODO: Add reload and reset?
    return embed


def house_points_help():
    embed = discord.Embed(title=f"{help_constants.HOUSE_POINTS} {help_constants.HELP}",
                          url=help_constants.HOUSE_POINTS_README,
                          color=constants.EMBED_COLOR)
    embed.add_field(name=f"{constants.BOT_PREFIX}housepoints",
                    value=f"Get the current house points standings!\n"
                          f"Optional: add a month and year to get old results.\n"
                          f"e.g. {constants.BOT_PREFIX}housepoints November 2020",
                    inline=False)
    embed = more_help(embed, help_constants.HOUSE_POINTS_README)
    return embed


def lookup_help():
    embed = discord.Embed(title=f"{help_constants.LOOKUP} {help_constants.HELP}",
                          url=help_constants.LOOKUP_README,
                          color=constants.EMBED_COLOR)
    embed.add_field(name=f"{constants.BOT_PREFIX}search <target_site> <query>",
                    value=f"Search the interwebs!\n"
                          f"<target_site> must match ({', '.join(list(lookup_constants.REGISTERED_SITES.keys()))}) or "
                          f"be a domain name (e.g. 'khanacademy').\n"
                          f"e.g. {constants.BOT_PREFIX}search hp kevin entwhistle\n"
                          f"{constants.BOT_PREFIX}search kaspersky cryptography",
                    inline=False)
    embed = more_help(embed, help_constants.LOOKUP_README)
    return embed


def more_help(embed, readme_link):
    return embed.add_field(name=f"More {help_constants.HELP}",
                           value=f"Want to know more? Check out the [GitHub README]({readme_link})",
                           inline=False)


def time_help():
    embed = discord.Embed(title=f"{help_constants.TIME} {help_constants.HELP}",
                          url=help_constants.TIME_README,
                          color=constants.EMBED_COLOR)
    embed.add_field(name=f"{constants.BOT_PREFIX}time <location>",
                    value=f"Find the time zone and current time anywhere in the world!\n"
                          f"e.g. {constants.BOT_PREFIX}time New York City",
                    inline=False)
    embed = more_help(embed, help_constants.TIME_README)
    return embed


MODULE_TO_HELP = {
    help_constants.CIPHER_RACE.lower() : cipher_race_help,
    help_constants.HOUSE_POINTS.lower(): house_points_help,
    help_constants.LOOKUP.lower(): lookup_help,
    help_constants.TIME.lower(): time_help
}


def setup(bot):
    bot.add_cog(HelpCog(bot))
