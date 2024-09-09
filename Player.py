"""
File which contains the Player class, to hold fishing data which would depend on the player.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import config

class Player():
    """The player of the game in regards to what we care about. Which is fishing."""

    def __init__(self):
        self.fishing_level = 1
        self.pct_perfect = 0
        self.fishing_depth = 1
        self.bait = None
        self.bait_target_id = None
        self.fishing_rod = config.FISHING_ROD_BAMBOO
