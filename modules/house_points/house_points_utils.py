from modules.house_points import house_points_constants


def get_winner_embed_color(points: list) -> int:
    """Get the current points leader index"""
    return house_points_constants.EMBED_COLORS[points.index(max(points))]


def get_points_tally_tab_url(sheet, tab_name: str = 'Tallies By Category'):
    """Get the URL of the 'Tallies By Category' tab"""
    return sheet.url + '/edit#gid=' + str(sheet.worksheet(tab_name).id)
