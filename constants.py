"""
Config file for setting up some variables which will be commonly used.
Please keep the spacing equal for constant variable groups for readability.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

# Locations
LOCATION_DEFAULT   = "Default"
LOCATION_TOWN      = "Town"
LOCATION_BEACH     = "Beach"
LOCATION_MOUNTAIN  = "Mountain"
LOCATION_FOREST    = "Forest"
LOCATION_MINE      = "Mine"
LOCATION_DESERT    = "Desert"
LOCATION_WOODS     = "Woods"
LOCATION_BACKWOODS = "Backwoods"

ALL_LOCATIONS = [
    LOCATION_DEFAULT,
    LOCATION_TOWN,
    LOCATION_BEACH,
    LOCATION_MOUNTAIN,
    LOCATION_FOREST,
    LOCATION_MINE,
    LOCATION_DESERT,
    LOCATION_WOODS,
    LOCATION_BACKWOODS,
]

# Seasons
SEASON_SPRING = "spring"
SEASON_SUMMER = "summer"
SEASON_FALL   = "fall"
SEASON_WINTER = "winter"

# Weather
WEATHER_SUNNY      = "sunny"
WEATHER_RAIN       = "rain"
WEATHER_GREEN_RAIN = "greenRain"

# Fishing Rods
FISHING_ROD_TRAINING   = "training"
FISHING_ROD_BAMBOO     = "normal"
FISHING_ROD_FIBERGLASS = "fiberglass"
FISHING_ROD_IRIDIUM    = "iridium"
FISHING_ROD_MASTERY    = "iridium+"

# Fishing Lures
FISHING_LURE_NONE      = "none"
FISHING_LURE_CURIOSITY = "curiosity"

# Fishing Bait
FISHING_BAIT_NONE     = "none"
FISHING_BAIT_TARGETED = "targeted"
FISHING_BAIT_MAGIC    = "magic"

# Quality Levels
QUALITY_NORMAL  = 0
QUALITY_SILVER  = 1
QUALITY_GOLD    = 2
QUALITY_IRIDIUM = 4

# Fish Quality Price Scaling
PRICE_SCALE_NORMAL  = 1
PRICE_SCALE_SILVER  = 1.25
PRICE_SCALE_GOLD    = 1.5
PRICE_SCALE_IRIDIUM = 2

# Skill Price Scaling
SKILL_NONE   = 1
SKILL_FISHER = 1.25
SKILL_ANGLER = 1.5
