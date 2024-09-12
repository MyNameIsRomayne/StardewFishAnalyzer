"""
Config file for setting up some variables which will be commonly used.
Please keep the spacing equal for constant variable groups for readability.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import constants
from stardewfish import utils

# If false, every object will load what is subjectively irrelevant for this code. 
# This is stuff like ignoring sale in random shops, sprite ID, etc.
# This reduces file size / ever so slightly increases load speed
IGNORE_IRRELEVANT_JSON = True

# Enable some subjective code which will scale the % perfect catches for a fish depending
# on its own difficulty.
DO_PERFECTION_DIFFICULTY_SCALE = True

SHOW_FISH     = True # whether to show individual catchable info for each location
FISHING_LEVEL = 8 # player fishing level
SEASON        = constants.SEASON_FALL
WEATHER       = constants.WEATHER_SUNNY
TIME          = utils.classic_to_military("10:00PM") # game time
LOCATIONS     = [ # locations to check
    constants.LOCATION_BEACH,
    constants.LOCATION_FOREST,
    constants.LOCATION_TOWN,
    constants.LOCATION_MOUNTAIN
]

SCALE_PCT_PERFECT_CATCHES = 0.17 # the percentage of catches which will be perfect. (0-1)
ROD_USED                  = constants.FISHING_ROD_IRIDIUM
BAIT_USED                 = constants.FISHING_BAIT_NONE
LURE_USED                 = constants.FISHING_LURE_NONE
BAIT_TARGET_ID            = "131" # (sardine) the current object ID of the targeted bait (if any) being used.
WATER_DEPTH               = 5 # fishing zone (0, 1, 2, 3, 5)
