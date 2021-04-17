import numpy as np
from modules.casino import casino_constants


class Slots:
    def __init__(self):
        pass

    # TODO: Figure out payouts
    def __call__(self):
        output_str = ""
        col = []
        for reel in casino_constants.REELS:
            rand = np.random.randint(len(reel))
            # Wrap around
            col.append(reel[rand:min(rand+3, len(reel))] + reel[:max(0, rand-(len(reel)-3))])
        print(col)
        output_str += "-----------------\n"
        output_str += "|Crazy Kev's Slot|\n"
        output_str += "-----------------\n"
        for row in range(len(col)):
            output_str += "|"
            for column in range(len(col[row])):
                output_str += col[column][row] + " | "
            output_str += "\n"
        return output_str



