from modules.house_points import house_points_constants

def get_winner_embed_color(points: list) -> int:
    """Get the current points leader index"""
    return house_points_constants.EMBED_COLORS[points.index(max(points))]

