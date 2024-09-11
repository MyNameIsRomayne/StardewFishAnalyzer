"""
File which contains the Player class, to hold fishing data which would depend on the player.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import config

class Player():
    """The player of the game in regards to what we care about. Which is fishing."""

    def __init__(self):
        self.fishing_level = config.FISHING_LEVEL
        self.pct_perfect = config.SCALE_PCT_PERFECT_CATCHES
        self.fishing_depth = config.WATER_DEPTH
        self.bait = config.BAIT_USED
        self.bait_target_id = config.BAIT_TARGET_ID
        self.fishing_rod = config.ROD_USED
        self.lure = config.LURE_USED
