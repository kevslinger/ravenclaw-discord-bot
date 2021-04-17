import pandas as pd
from modules.code import code_constants
import discord
import constants
import math



def create_embed() -> discord.Embed:
    """
    Create an empty discord embed with color.

    :return: (discord.Embed)
    """
    return discord.Embed(color=constants.EMBED_COLOR)


def create_level_prep_embed(level: int) -> discord.Embed:
    """
    Create an embed to let the team know their next level will start soon.
    
    :param level: (int) the level the team just completed.
    :param teamname: (str) the name of the team
    :return embed: (discord.Embed) the embed that includes the level-up message.
    """
    embed = create_embed()
    embed.add_field(name=f"Level {level} Complete!", value=f"Well done! Level {level+1} will begin in {code_constants.BREAK_TIME} seconds.")
    return embed


def get_opening_statement(sheet_used) -> discord.Embed:
    """
    Assemble the opening message to send to the team before their puzzle begins

    :return embed: (discord.Embed) the embed that includes the welcome message
    """
    embed = create_embed()
    embed.add_field(name=f"Welcome!", value=f"You have started a new race against the {sheet_used.capitalize()} wordlist! "
                                            f"Level 1 will start in about {code_constants.BREAK_TIME} seconds from this message! "
                                            f"You will have {code_constants.TIME_LIMIT} seconds to complete levels 1-5. "
                                            f"After every {code_constants.NUM_LEVELS}th level, you will get {code_constants.BONUS_TIME} "
                                            f"additional seconds (i.e you get {code_constants.TIME_LIMIT + code_constants.BONUS_TIME} "
                                            f"seconds to complete levels 6-10). Good luck and have fun!")
    return embed


def create_code_embed(level: int, codes: pd.DataFrame):
    """
    Function to create the code embed
    :param level: (int) The level of the current puzzle solvers
    :param codes: (pandas.DataFrame) the current set of codes

    :return embeds: (list of discord.Embed) The embeds we create for the code
    :return code_answer: (list of str) the answers to the given codes
    """
    code_answers = []
    embed_list = []
    embed = create_embed()
    embed.add_field(name=f"Level {level}", value=f"Welcome to level {level}! You will have {compute_level_time(level)} " + \
    f"seconds to solve {level} {code_constants.CODE}s, beginning now.", inline=False)
    embed_list.append(embed)
    for i in range(level):
        code_proposal = codes.sample()
        embed_list.append(create_embed())
        embed_list[-1].add_field(name=f"{code_constants.CODE.capitalize()} #{i+1}", value=f"{code_proposal[code_constants.URL].item()}", inline=False)
        embed_list[-1].set_image(url=code_proposal[code_constants.URL].item())
        code_answers.append(code_proposal[code_constants.ANSWER].item().replace(' ', '').lower())
    embed_list.append(create_embed())
    embed_list[-1].add_field(name="Answering", value=f"Use {constants.BOT_PREFIX}answer to make a guess on any of the {code_constants.CODE}s.",
                    inline=False)
    return embed_list, code_answers


def create_no_code_embed() -> discord.Embed:
    """
    Function to create an embed to say there is no code

    :return embed: (discord.Embed) The embed we create
    """
    embed = create_embed()
    embed.add_field(name=f"No Current {code_constants.CODE.capitalize()}",
                    value=f"You haven't started the race. To start, use command {constants.BOT_PREFIX}startrace.",
                    inline=False)
    return embed


def get_answer_result(user_answer: str, current_answers: list) -> str:
    """
    Return either correct or incorrect based on the team's answer and the list of codes.

    :param user_answer: (str) the answer given by the user
    :param current_answers: (list of str) the remaining answers for that team in the level

    :return result: (str) either correct or incorrect
    """
    user_answer = user_answer.lower()
    if user_answer in current_answers:
            current_answers.pop(current_answers.index(user_answer))
            result = code_constants.CORRECT
    else:
        result = code_constants.INCORRECT

    return result


def compute_level_time(level: int) -> int:
    """
    60 seconds on levels 1-5
    +10 on levels 6-10
    +10 on levels 10-15
    ...
    """
    return code_constants.TIME_LIMIT + code_constants.BONUS_TIME * math.floor((level - 1) / code_constants.NUM_LEVELS)
