"""
A helpful class which converts some JSON object into a readable python object.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

from math import floor
from config import QUALITY_NORMAL, QUALITY_SILVER, QUALITY_GOLD, QUALITY_IRIDIUM
from config import PRICE_SCALE_NORMAL, PRICE_SCALE_SILVER, PRICE_SCALE_GOLD, PRICE_SCALE_IRIDIUM
from config import SKILL_NONE
from config import IGNORE_IRRELEVANT_JSON
from config import objects_json

class CatchableData():

    def __init__(self, id, data:str):
        """
        Setup the data for this catchable from data.
        The variables depend on whether it's a fish trap catchable or a fishing rod catchable.
        To check for this, call is_trap()
        """
        split_data:list[str] = data.split("/")
        # Setup data as a trap fish
        if (split_data[1] == "trap"):
            self.id = id
            # Clarify it is a trap fish
            self.istrap = True
            # Indices of variables in split_data for readability.
            INDEX_NAME     = 0
            INDEX_CHANCE   = 2
            INDEX_LOCATION = 4
            INDEX_MIN_SIZE = 5
            INDEX_MAX_SIZE = 6
            self.name:str     = split_data[INDEX_NAME]
            self.chance:float = float(split_data[INDEX_CHANCE])
            self.location:str = split_data[INDEX_LOCATION]
            self.min_size:int = int(split_data[INDEX_MIN_SIZE])
            self.max_size:int = int(split_data[INDEX_MAX_SIZE])
        # Setup data as a catchable fish
        else:
            # Indices of variables in split_data for readability.
            INDEX_NAME          = 0
            INDEX_DIFFICULTY    = 1
            INDEX_TYPE          = 2
            INDEX_MIN_SIZE      = 3
            INDEX_MAX_SIZE      = 4
            INDEX_CATCH_TIME    = 5
            INDEX_WEATHER       = 7
            INDEX_MAX_DEPTH     = 9
            INDEX_SPAWN_MULT    = 10
            INDEX_DEPTH_MULT    = 11
            INDEX_MIN_LEVEL     = 12
            # The internal ID of the fish
            self.id = id
            # Clarify that this is not a crab pot 'fish'
            self.istrap = False
            # The associated object with this fish's ID
            self.fish_object = objects_json[self.id]
            # The internal (english) name of the fish
            self.name        = split_data[INDEX_NAME]
            # How often the fish darts in the minigame from 15 to 100
            self.difficulty  = int(split_data[INDEX_DIFFICULTY])
            # The behavior of the fish as it darts
            self.type:str             = split_data[INDEX_TYPE]
            # The minimum and maximum sizes, respectively, for this fish
            self.min_size:int         = split_data[INDEX_MIN_SIZE]
            self.max_size:int         = split_data[INDEX_MAX_SIZE]
            # The ranges of which this fish may be caught
            self.catch_time:list[int] = [int(t) for t in split_data[INDEX_CATCH_TIME].split(" ")]
            # The weather this can be caught in. sunny, rainy, or both
            self.weather:str          = split_data[INDEX_WEATHER]
            # The minimum water depth to cast in to maximize its catch rate
            self.max_depth:int        = int(split_data[INDEX_MAX_DEPTH])
            # The spawn multiplier for spawn rate calculations
            self.spawn_mult:float     = float(split_data[INDEX_SPAWN_MULT])
            # The depth multiplier for spawn rate calculations
            self.depth_mult:float     = float(split_data[INDEX_DEPTH_MULT])
            # The minimum fishing level required to catch this fish
            self.min_level:int        = int(split_data[INDEX_MIN_LEVEL])

            # Rewrite from the below if you need em'
            if IGNORE_IRRELEVANT_JSON: return

            INDEX_SEASON            = 6
            INDEX_LOCATIONS         = 8
            INDEX_TUTORIAL_ELIGIBLE = 13

            self.season:str         = split_data[INDEX_SEASON]
            self.locations          = split_data[INDEX_LOCATIONS]
            self.tutorial_eligible  = split_data[INDEX_TUTORIAL_ELIGIBLE]

    def is_trap(self) -> bool:
        """Getter for whether or not this is found in crab pot traps."""
        return self.istrap

    def is_legendary(self) -> bool:
        """Gets whether this fish is a legendary fish."""
        return "fish_legendary" in self.fish_object["ContextTags"]

    def get_average_size(self, fishing_zone = 4, fishing_skill = 10) -> float:
        """Gets the average size of this fish, dependent on the fishing zone and fishing skill."""
        # fishSize = Zone/5 * (Skill+2)/10 * Random/100
        # For the sake of "Average", random will be 50
        AVERAGE_RANDOM = 50
        return (fishing_zone/5) * (fishing_skill+2)/10 * AVERAGE_RANDOM/100

    def get_average_quality(self) -> int:
        """
        Get the average quality of the fish, depending on its size.
        This will be an exact quality based off the average size,
        so as far as getting average price goes it may be slightly skewed.
        """
        size = self.get_average_size()
        if size < 0.33:
            return QUALITY_NORMAL
        if size < 0.66:
            return QUALITY_SILVER
        return QUALITY_GOLD

    def get_average_chance(self, water_depth=4, fishing_level=6, is_training_rod=False,
                           curiosity_lure=False, curiosity_lure_buff=0, bait_targets_fish=False,
                           apply_daily_luck=False, daily_luck=0, chance_modifiers:list[tuple[float, str]]=[],
                           chance_mode:str=None):
        """
        Gets the average chance that this particular fish should be caught, given some parameters.
        Namely, it uses the same exact calculations found in GameLocation.cs, line 13937-13974.
        """
        chance = self.spawn_mult
        dropOff = self.spawn_mult * self.depth_mult
        chance -= max(0, self.max_depth - water_depth) * dropOff
        chance += fishing_level / 50
        chance = (chance * 1.1) if (is_training_rod) else (chance)
        chance = min(0.9, chance)
        if (chance < 0.25) and (curiosity_lure):
            if (curiosity_lure_buff > -1):
                chance += curiosity_lure_buff
            else:
                max_val = 0.25
                min_val = 0.08
                chance = (max_val - min_val) / max_val * chance + (max_val - min_val) / 2
        chance = (chance * 1.6) if (bait_targets_fish) else (chance)
        chance = (chance + daily_luck) if (apply_daily_luck) else (chance)
        if not len(chance_modifiers):
            return chance
        return apply_chance_modifiers(chance, chance_modifiers, chance_mode)

    def get_average_value(self, fish_quality:int = None, skill_bonus = SKILL_NONE):
        fish_quality = self.get_average_quality() if (fish_quality == None) else fish_quality
        base_price = self.fish_object["Price"]
        final_price = scale_price_by_quality(base_price, fish_quality)
        return floor(final_price * skill_bonus)
    
    def get_average_xp(self, fish_quality:int = None, perfect = False, treasure = False):
        # https://stardewvalleywiki.com/Fishing#Experience_Points 1.6.8
        fish_quality = self.get_average_quality() if (fish_quality == None) else fish_quality
        if perfect: fish_quality = adjust_quality(fish_quality, 1)
        resultant_xp = floor((fish_quality + 1) * 3)
        resultant_xp = floor(resultant_xp + (float(self.difficulty) / 3))
        if perfect: resultant_xp = floor(resultant_xp * 2.4)
        if treasure: resultant_xp = floor(resultant_xp * 2.2)
        if self.is_legendary(): resultant_xp = floor(resultant_xp * 5)
        return resultant_xp

def scale_price_by_quality(price:int, quality:int):
    # sanity
    if quality < QUALITY_NORMAL: quality = QUALITY_NORMAL
    if quality > QUALITY_IRIDIUM: quality = QUALITY_IRIDIUM
    # scaling
    if quality == QUALITY_NORMAL: return floor(price * PRICE_SCALE_NORMAL)
    if quality == QUALITY_SILVER: return floor(price * PRICE_SCALE_SILVER)
    if quality == QUALITY_GOLD: return floor(price * PRICE_SCALE_GOLD)
    if quality == QUALITY_IRIDIUM: return floor(price * PRICE_SCALE_IRIDIUM)

def apply_chance_modifiers(chance:float, modifiers:list[tuple[float, str]], chance_mode:str):
    """
    Apply chance modifiers to a chance depending on chance_mode.
    modifiers: a list of tuples corresponding to (chance, mode), where modifier modes can be:
    "add", "subtract", "multiply", "divide", "set".
    The first four are self-explanatory, but to elaborate on set, it just sets the value to whatever it is.
    chance_mode: the chance mode to use, which is one of the following:
    Minimum: Take the least of two chances being applied.
    Maximum: Take the most of two chances being applied:
    Set (default): Just apply each chance iteratively.
    """
    chance_mode = chance_mode.lower()
    for modifier in modifiers:
        modifier_chance, mode = modifier[0], modifier[1].lower()
        # Handle modifier's mode
        new_chance = chance
        if mode == "add":
            new_chance += modifier_chance
        elif mode == "subtract":
            new_chance -= modifier_chance
        elif mode == "multiply":
            new_chance *= modifier_chance
        elif mode == "divide":
            new_chance /= modifier_chance
        elif mode == "set":
            new_chance  = modifier_chance
        else:
            raise NotImplementedError
        # Handle arg's chance mode
        if chance_mode == "minimum":
            chance = min(chance, new_chance)
        elif chance_mode == "maximum":
            chance = max(chance, new_chance)
        elif chance_mode == "set":
            chance = new_chance
        else:
            raise NotImplementedError
    return chance
        
def adjust_quality(quality, factor:int):
    """Adjust quality up or down n times"""
    # Recurse back to make life easier. Everything below deals in increments of 1
    if factor > 1: quality = adjust_quality(quality, factor - 1)
    if factor < -1: quality = adjust_quality(quality, factor + 1)
    # Edge case
    if factor == 0: return quality
    # Handle quality increases
    if factor > 0:
        if quality > QUALITY_IRIDIUM: return QUALITY_IRIDIUM
        if quality == QUALITY_IRIDIUM: return QUALITY_IRIDIUM # cap at iridium
        if quality == QUALITY_GOLD: return QUALITY_IRIDIUM
        if quality == QUALITY_SILVER: return QUALITY_GOLD
        if quality == QUALITY_NORMAL: return QUALITY_SILVER
        if quality < QUALITY_NORMAL: return QUALITY_SILVER
    # Handle quality decreases
    if factor < 0:
        if quality < QUALITY_NORMAL: return QUALITY_NORMAL
        if quality == QUALITY_NORMAL: return QUALITY_NORMAL # cap at normal
        if quality == QUALITY_SILVER: return QUALITY_NORMAL
        if quality == QUALITY_GOLD: return QUALITY_SILVER
        if quality == QUALITY_IRIDIUM: return QUALITY_GOLD
        if quality > QUALITY_IRIDIUM: return QUALITY_GOLD