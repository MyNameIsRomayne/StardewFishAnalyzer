"""
Config file for setting up some variables which will be commonly used.
Please keep the spacing equal for constant variable groups for readability.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import constants
import config_paths
from stardewfish import utils

# If false, every object will load what is subjectively irrelevant for this code. 
# This is stuff like ignoring sale in random shops, sprite ID, etc.
# This reduces file size / ever so slightly increases load speed
IGNORE_IRRELEVANT_JSON = True

_public_config:dict = utils.read_file_json(config_paths.FILE_JSON_PUBLIC_CONFIG)

# Setup default values
_default_config = {
    "scaleperfect"  : True,
    "showfish"      : True,
    "fishinglevel"  : 10,
    "season"        : constants.SEASON_SPRING,
    "weather"       : constants.WEATHER_SUNNY,
    "time"          : utils.classic_to_military("6:00AM"),
    "pctperfect"    : 1,
    "rod"           : constants.FISHING_ROD_IRIDIUM,
    "bait"          : constants.FISHING_BAIT_NONE,
    "lure"          : constants.FISHING_LURE_NONE,
    "baitid"        : None,
    "depth"         : 5,
    "ignorelegends" : True,
    "ignoreqi"      : True,
    "locations"     : [
    constants.LOCATION_BEACH,
    constants.LOCATION_FOREST,
    constants.LOCATION_TOWN,
    constants.LOCATION_MOUNTAIN,
    constants.LOCATION_WOODS,
    constants.LOCATION_BACKWOODS
    ],
}

# Override defaults with explicit values from public_config.json
for config_key in _default_config.keys():
    if config_key in _public_config.keys():
        _default_config[config_key] = _public_config[config_key]

# Take values from default config and put them into variables for easy use elsewhere.
DO_PERFECTION_DIFFICULTY_SCALE = _default_config["scaleperfect"] # enable scaling fish perfection % based off factors like its difficulty

SHOW_FISH     = _default_config["showfish"] # whether to show individual catchable info for each location
FISHING_LEVEL = _default_config["fishinglevel"]
SEASON        = _default_config["season"]
WEATHER       = _default_config["weather"]
TIME          = _default_config["time"]
LOCATIONS     = _default_config["locations"]

SCALE_PCT_PERFECT_CATCHES = _default_config["pctperfect"] # the percentage of catches which will be perfect. (0-1)
ROD_USED                  = _default_config["rod"]
BAIT_USED                 = _default_config["bait"]
LURE_USED                 = _default_config["lure"]
BAIT_TARGET_ID            = _default_config["baitid"] # (sardine) the current object ID of the targeted bait (if any) being used.
WATER_DEPTH               = _default_config["depth"] # fishing zone (0, 1, 2, 3, 5)
IGNORE_LEGENDARY_FISH     = _default_config["ignorelegends"]
IGNORE_MR_QI              = _default_config["ignoreqi"]
