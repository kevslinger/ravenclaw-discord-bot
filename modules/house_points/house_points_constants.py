####################
### HOUSE POINTS ###
####################

GRYFFINDOR = "Gryffindor"
HUFFLEPUFF = "Hufflepuff"
RAVENCLAW = "Ravenclaw"
SLYTHERIN = "Slytherin"
HOUSES = [GRYFFINDOR, HUFFLEPUFF, RAVENCLAW, SLYTHERIN]

# In Current Points sheet, the points are in cells B1, B2, B3, B4
CURRENT_HOUSE_POINTS_RANGE = ["F24:F27"]

GRYFF_EMBED_COLOR = 0xff4e4e
PUFF_EMBED_COLOR = 0xffee4e
CLAW_EMBED_COLOR = 0x4ee4ff
SNEK_EMBED_COLOR = 0x4eff4e
EMBED_COLORS = [GRYFF_EMBED_COLOR, PUFF_EMBED_COLOR, CLAW_EMBED_COLOR, SNEK_EMBED_COLOR]

HISTORY_COLUMNS = ['', 'Date', '', GRYFFINDOR, '', HUFFLEPUFF, '', RAVENCLAW, '', SLYTHERIN]

ARITHMANCY = "Arithmancy"
INTERHOUSE = "Interhouse Challenge"
DUELING = "Dueling"
EXTRA_CREDIT = "Extra Credit"
FANWORKS = "Fanworks"
DISCUSSION_COMMENT = "Great Discussion/Comment"
HOMEWORK = "Homework"
IN_HOUSE = "In-House Contest"
HUMOR = "Just Because/Humor"
QUIDDITCH = "Quidditch"
ACTIVITIES = [ARITHMANCY,
              INTERHOUSE,
              DUELING,
              EXTRA_CREDIT,
              FANWORKS,
              DISCUSSION_COMMENT,
              HOMEWORK,
              IN_HOUSE,
              HUMOR,
              QUIDDITCH]
ACTIVITY_SHEET_RANGE_MAP = {
    ARITHMANCY: ["C3:C6"],
    INTERHOUSE: ["F3:F6"],
    DUELING: ["I3:I6"],
    EXTRA_CREDIT: ["C10:C13"],
    FANWORKS: ["F10:F13"],
    DISCUSSION_COMMENT: ["I10:I13"],
    HOMEWORK: ["C17:C20"],
    IN_HOUSE: ["F17:F20"],
    HUMOR: ["I17:I20"],
    QUIDDITCH: ["C24:C27"]
}

