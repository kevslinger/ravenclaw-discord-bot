

def format_spoiler_answer(answer, filler: int = 30):
    """Discord py embeds remove excess whitespace, so we need to add filler"""
    return f"||{'. '*(filler-len(answer))}{answer}{'. '*(filler-len(answer))}||"
