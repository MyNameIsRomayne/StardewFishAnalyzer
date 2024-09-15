"""
File for setting up some coupled class objects such as:
GameObject - Initializes and holds game information about all of the below, as well as base objects from Objects.json and furniture from Furniture.Json
GameLocation - Initializes and holds information about a game location (only the fish relevant stuff) from Locations.json
FishLocation - Intitializes and holds information about a fishing location from part of Locations.json
CatchableData - Initializes and holds information about fish from Fish.json
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

from math import floor
import numpy as np

import constants
import config
import config_paths

import stardewfish.game_reader as gr

from stardewfish.base_object      import BaseObject
from stardewfish.furniture_object import FurnitureObject
from stardewfish.probs_algorithm  import get_probs, get_probs_with_target
from stardewfish.player_object    import Player
from stardewfish.utils            import clamp

class GameObject():
    
    def __init__(self, player:Player = None):
        # Setup object data
        self.season  = config.SEASON
        self.weather = config.WEATHER
        self.time    = config.TIME
        self.player = (player) if (player != None) else (Player())
        self.daily_luck = 0

        self.base_objects:dict[str, BaseObject]           = gr.get_objects(config_paths.FILE_JSON_OBJECTS,   config_paths.FILE_PYOBJECTS_BASEOBJECT,   BaseObject)
        self.fish_objects:dict[str, CatchableData]        = gr.get_objects(config_paths.FILE_JSON_FISH,      config_paths.FILE_PYOBJECTS_FISH,      CatchableData)
        self.location_objects:dict[str, GameLocation]     = gr.get_objects(config_paths.FILE_JSON_LOCATIONS, config_paths.FILE_PYOBJECTS_GAMELOCATION, GameLocation)
        self.furniture_objects:dict[str, FurnitureObject] = gr.get_objects(config_paths.FILE_JSON_FURNITURE, config_paths.FILE_PYOBJECTS_FURNITURE, FurnitureObject)

    def post_init(self):
        """Handles the post-init phase, for creating associations between object classes after they are all initialized."""
        [self.fish_objects[key].post_setup() for key in self.fish_objects]
        for location in [self.location_objects[key] for key in self.location_objects]:
            [fish_loc.post_setup() for fish_loc in location.fish]
            
class GameLocation():

    def __init__(self, id:str, json_data:dict):
        self.id = id
        self.fish:list[FishLocation] = [FishLocation(data_json) for data_json in json_data["Fish"]]
        # FishAreas is a dict keyed by location ID, we just need to show location IDs to users. Noone cares about crab pots/bounds right? >:3
        self.areas = [key for key in json_data["FishAreas"].keys()]

    def get_fish_in_subarea(self, target_id:str|None) -> list["FishLocation"]:
        """
        Get all the fish which are associated with a certain area_id.
        If the target_id is None, all fish with no particular area ID will be returned.
        """
        fish_in_area:list[FishLocation] = []
        for fish in self.fish:
            if fish.fishareaid == target_id:
                fish_in_area.append(fish)
        return fish_in_area

    def get_area_composition(self, target_id:str|None):
        """
        Get the composition of catchable fish in this area which correspond to a particular area ID.
        If target_id is None, all fish with no particular area ID will be used.
        """
        # All of the fish within the area
        fish_in_area:list[FishLocation] = self.get_fish_in_subarea(target_id)
        # All of the fish which can be caught in the area, according to player and game data
        fish_catchable_in_area = filter_catchable_fish(fish_in_area)
        # The catchable fish in the area, placed into a dictionary keyed by their precedence values.
        # This is done to properly get the weights of each, as fish order is first done by precedence and then randomly.
        fish_by_precedence:dict[str, list[FishLocation]] = {}

        if (not len(fish_catchable_in_area)):
            # nothing catchable here except maybe trash, not worth reporting
            return {}
        
        # If the area isn't the default, it will inherit catchables from the Default location
        # I guess technically default could inherit itself but it just makes a mess for no reason to not do this check
        if (self.id != "Default"):
            fish_catchable_in_area += filter_catchable_fish([loc for loc in game.location_objects["Default"].fish])
        
        # Sort the fish by precedence into fish_by_precedence
        for catchable in fish_catchable_in_area:
            group = str(catchable.precedence)
            # Setup list for this if it doesn't exist yet
            if group not in fish_by_precedence:
                fish_by_precedence[group] = []
            fish_by_precedence[group].append(catchable)
        
        # Ensure we go through the precedence groups as the game would (low to hi)
        precedence_groups = [int(e) for e in fish_by_precedence.keys()]
        precedence_groups.sort()
        precedence_groups = [str(e) for e in precedence_groups]

        composition_data:dict[str, list] = {
            "fish"    : fish_catchable_in_area,
            "chances" : [],
            "xp"      : [],
            "coins"   : []
        }

        # Variables for easy reference to the above
        chances_list:list[float]     = composition_data["chances"]
        xp_list:list[float]          = composition_data["xp"]
        coins_list:list[float]       = composition_data["coins"]

        # Keep a running total of how likely it is we get to the current 
        chance_pass_all_previous = 1

        using_targeted_bait = game.player.bait == constants.FISHING_BAIT_TARGETED
        targeted_bait_id = game.player.bait_target_id

        # Get the chance for each fish within a precedence group
        for group in precedence_groups:
            chance_list = [] # temporary storage for the chance of each fish in the group
            target_fish_index = None # index of our targeted fish, if we have one in here
            for index, fish_loc in enumerate(fish_by_precedence[group]):
                if (fish_loc.itemids[0].id == targeted_bait_id):
                    target_fish_index = index
                specific_fish_chance = 1
                fish_id = fish_loc.itemids[0].id
                if fish_id in game.fish_objects.keys():
                    fish_object = game.fish_objects[fish_id]
                    specific_fish_chance = fish_object.get_average_chance(fish_loc)
                chance_list.append(fish_loc.chance * specific_fish_chance)
            
            if ((using_targeted_bait) and (target_fish_index != None)):
                current_weights = get_probs_with_target(np.array(chance_list), target=target_fish_index, rerolls=2)
            else:
                # Normal weights with untargeted bait. Also targeted bait with fish not in this segment (it has the same result)
                current_weights = get_probs(np.array(chance_list))
            sum_current_weights = sum(current_weights)
            reduced_weights = [weight * chance_pass_all_previous for weight in current_weights]

            chances_list += reduced_weights
            chance_pass_all_previous *= (1 - sum_current_weights)
    
            # Add price/xp stats
            for fish in fish_by_precedence[group]:
                sum_coins = 0
                sum_xp = 0
                # Handle getting all the objects to use
                for loot_id in [obj.id for obj in fish.itemids]:
                    value, xp = 0, 3
                    # Coins might be yoinkable from here first if it isnt a fish
                    if loot_id in game.base_objects.keys():
                        value = game.base_objects[loot_id].price
                    # If it is, we can get coins AND xp
                    if loot_id in game.fish_objects.keys():
                        value = game.fish_objects[loot_id].get_average_value()
                        xp = game.fish_objects[loot_id].get_average_xp()
                    # Finally, add it to the sum
                    sum_coins += value
                    sum_xp += xp
                # Got all the catchables, add relevant data to lists
                coins_list.append(sum_coins/len(fish.itemids))
                xp_list.append(sum_xp/len(fish.itemids))
            
        return composition_data

    def get_composition(self):
        """
        Get some information about the location's sublocation compositions
        """
        loc_dict:dict[str, dict[str, list[GameLocation]]] = {}

        # Go over each sublocation in the location and process *those* individually
        loc_dict["none"] = self.get_area_composition(None)

        for area in self.areas:
            area_data = self.get_area_composition(area)
            # Empty, dont care about it
            if area_data == {}:
                continue
            loc_dict[area] = area_data
        
        return loc_dict

class FishLocation():
    
    def __init__(self, json_data:dict):
        self.setup_itemids = False
        self.chance                   = json_data["Chance"]
        self.season                   = json_data["Season"]
        self.fishareaid               = json_data["FishAreaId"]
        self.min_fishing_level        = json_data["MinFishingLevel"]
        self.apply_daily_luck         = json_data["ApplyDailyLuck"]
        self.curiosity_lure_buff      = json_data["CuriosityLureBuff"]
        self.specific_bait_buff       = json_data["SpecificBaitBuff"]
        self.specific_bait_multiplier = json_data["SpecificBaitMultiplier"]
        self.isbossfish               = json_data["IsBossFish"]
        self.requiremagicbait         = json_data["RequireMagicBait"]
        self.min_distance_from_shore  = json_data["MinDistanceFromShore"]
        self.max_distance_from_shore  = json_data["MaxDistanceFromShore"]
        self.precedence               = json_data["Precedence"]
        self.ignoresubdata            = json_data["IgnoreFishDataRequirements"]
        self.can_be_inherited         = json_data["CanBeInherited"]
        self.set_flag_on_catch        = json_data["SetFlagOnCatch"]
        self.chancemodifiers          = json_data["ChanceModifiers"]
        self.chancemodifiermode       = json_data["ChanceModifierMode"]
        self.chanceboostperlucklevel  = json_data["ChanceBoostPerLuckLevel"]
        self.quality                  = json_data["Quality"]
        self.condition                = json_data["Condition"]

        self.itemids:list[BaseObject] = parse_item_ids(json_data)
    
        if not config.IGNORE_IRRELEVANT_JSON: return
            
        self.bobber_position          = json_data["BobberPosition"]
        self.player_position          = json_data["PlayerPosition"]
        self.catch_limit              = json_data["CatchLimit"]
        self.can_use_training_rod     = json_data["CanUseTrainingRod"]
    
    def __str__(self):
        return self.itemids[0].name

    def post_setup(self):
        """
        Gets the objects from the itemids parsed after initial setup.
        """
        if self.setup_itemids: return self.itemids
        if "RANDOM_FISH" not in self.itemids:
            self.itemids = [get_object_from_id(itemid, item_type_objects) for itemid in self.itemids]
        self.setup_itemids = True
        return self.itemids

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
            self.fish_object = None
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
            if config.IGNORE_IRRELEVANT_JSON: return

            INDEX_SEASON            = 6
            INDEX_LOCATIONS         = 8
            INDEX_TUTORIAL_ELIGIBLE = 13

            self.season:str         = split_data[INDEX_SEASON]
            self.locations          = split_data[INDEX_LOCATIONS]
            self.tutorial_eligible  = split_data[INDEX_TUTORIAL_ELIGIBLE]

    def post_setup(self) -> None:
        """
        Gets the game object associated with this catchable after initial setup.
        """
        self.fish_object = game.base_objects[self.id]

    def get_seasons(self) -> list[str]:
        """Get all seasons this fish is catchable."""
        related_object = game.base_objects[self.id]
        season_context_tags = [str(tag) for tag in related_object.context_tags if "season_" in tag]
        season_context_tags = [tag.replace("season_", '').title() for tag in season_context_tags]
        return season_context_tags

    def get_locations(self) -> list[str]:
        """Get all locations where this fish is catchable."""
        related_object = game.base_objects[self.id]
        location_context_tags = [str(tag) for tag in related_object.context_tags if "fish_" in tag]
        location_context_tags = [tag.replace("fish_", " ").replace("_", '').title().strip() for tag in location_context_tags]
        location_context_tags = [tag for tag in location_context_tags if tag in constants.ALL_LOCATIONS]
        return location_context_tags

    def is_trap(self) -> bool:
        """Getter for whether or not this is found in crab pot traps."""
        return self.istrap

    def is_legendary(self) -> bool:
        """Gets whether this fish is a legendary fish."""
        return (self.fish_object.context_tags != None) and ("fish_legendary" in self.fish_object.context_tags)

    def get_fish_size_ranges(self) -> tuple[float, float]:
        """
        Gets the range of sizes this fish may be within for the current player conditions.
        """
        """
        Ok now that the doc comment is over, dev's note: i hate this. it was supposed to just be
        (fishing_zone/5) * (fishing_skill+2)/10 * AVERAGE_RANDOM/100 (avg_random = 1) but NOOO
        it has to be all COMPLICATED and now we need the proprotions of shit. oh my goddd
        AND WAIT IT GETS WORSE BECAUSE THE WIKI IS WRONG!!!
        its not skill+2 /10, its RAND(min(5, floor(skill+2/10)), 5) / 5f (rand is inclusive)
        basically this whole function is just me coping with [worst_case*range*worst_case, best_case*range*best_case]
        """
        # Level contributions to fish size
        min_level_contribution = 1 + floor(game.player.fishing_level / 2)
        max_level_contribution = max(6, min_level_contribution) / 5
        min_level_contribution /= 5
        # RNG contributions to fish size
        min_rng_contribution = 0.9
        max_rng_contribution = 1.1
        # Zone contribution to fish size
        baseFishSize = (game.player.fishing_depth/5)
        # Min/max size based off worst/best case scenarios
        minFishSize, maxFishSize = (min_level_contribution * baseFishSize * min_rng_contribution), (max_level_contribution * baseFishSize * max_rng_contribution)
        return minFishSize, maxFishSize

    def get_absolute_fish_quality(self, size:float) -> int:
        """Internal helper function, gets the quality of some size."""
        if   size < 0.33: return constants.QUALITY_NORMAL
        elif size < 0.66: return constants.QUALITY_SILVER
        else:             return constants.QUALITY_GOLD

    def get_pct_perfect(self) -> float:
        """Get the percent of perfects for this fish.
        Returns game.player.pct_perfect directly if DO_PERFECTION_DIFFICULTY_SCALE is false.
        """
        if not config.DO_PERFECTION_DIFFICULTY_SCALE:
            return game.player.pct_perfect
        # A level 1 player will do worse a la fishing bar size than a level 10, account for this. Slightly.
        # 10 is the ideal value here, with each level below subtracting a (subjective) 5% (level 14 does 1.2x, which, sure, i guess.)
        scaled_pct_level      = 0.5 + (0.05 * game.player.fishing_level)
        # 50 should be the 'tipping point' of which below perfection should be easier, and above harder.
        # Specifically, a carp gets a 1.3x, and a glacierfish gets a 0.5x. Not perfect, but better than nothing
        scaled_pct_difficulty = (1.5 - self.difficulty/100)
        return clamp(game.player.pct_perfect*scaled_pct_difficulty*scaled_pct_level, 0, 1)

    def get_quality_proportions(self) -> dict[int, float]:
        """
        Gets the percent of fish that should be of a certain quality. It returns in the order of 
        QUALITY_NORMAL, QUALITY_SILVER, QUALITY_GOLD, QUALITY_IRIDIUM as (float, float, float, float).
        """
        qualities = {
            constants.QUALITY_NORMAL  : 0,
            constants.QUALITY_SILVER  : 0,
            constants.QUALITY_GOLD    : 0,
            constants.QUALITY_IRIDIUM : 0
        }
        min_size, max_size = self.get_fish_size_ranges()
        min_quality, max_quality = self.get_absolute_fish_quality(min_size), self.get_absolute_fish_quality(max_size)
        if min_quality == max_quality:
            # shortcuts~
            qualities[min_quality] = 1
        else:
            # no shortcut :(
            bounds = [
                [-9999, 0.33],
                [0.33,  0.66],
                [0.66,  9999]
            ]
            size_range = max_size - min_size
            for iter, bounds in enumerate(bounds):
                # For the sake of normal/silver/gold, we can couple iter to quality
                bounds_min, bounds_max = bounds
                a = min(max_size, bounds_max)
                b = max(min_size, bounds_min)
                qualities[iter] = max(0, (a - b) / size_range)

        scaled_pct_perfect = self.get_pct_perfect()

        if scaled_pct_perfect == 0:
            return qualities # because yuss
        
        # only silver/gold get quality increases like this, so its sane to handle manually
        # split proportion of perfects from gold
        split_from_gold = qualities[constants.QUALITY_GOLD] * scaled_pct_perfect
        qualities[constants.QUALITY_GOLD] -= split_from_gold
        # split proportion of perfects from silver
        split_from_silver = qualities[constants.QUALITY_SILVER] * scaled_pct_perfect
        qualities[constants.QUALITY_SILVER] -= split_from_silver
        # add back to their respective qualities
        qualities[constants.QUALITY_GOLD] += split_from_silver
        qualities[constants.QUALITY_IRIDIUM] += split_from_gold
        return qualities

    def get_average_chance(self, location_data:FishLocation=None):
        """
        Gets the average chance that this particular fish should be caught, given some parameters.
        Namely, it uses the same exact calculations found in GameLocation.cs, line 13937-13974.
        """

        # Handle using location data, if applicable
        apply_daily_luck    = False
        chance_mode         = "stack" # default
        chance_modifiers    = None
        curiosity_lure_buff = 0
        fishing_level       = game.player.fishing_level
        water_depth         = game.player.fishing_depth
        is_training_rod     = (game.player.fishing_rod == constants.FISHING_ROD_TRAINING)
        curiosity_lure      = (game.player.lure == constants.FISHING_LURE_CURIOSITY)
        bait_targets_fish   = (game.player.bait == constants.FISHING_BAIT_TARGETED
                               and game.player.bait_target_id == self.id)

        if location_data != None:
            chance_mode         = location_data.chancemodifiermode
            chance_modifiers    = location_data.chancemodifiers
            apply_daily_luck    = location_data.apply_daily_luck
            curiosity_lure_buff = location_data.curiosity_lure_buff

        if self.is_trap(): return self.chance

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
        chance = (chance * (4/3)) if (bait_targets_fish) else (chance)
        chance = (chance + game.daily_luck) if (apply_daily_luck) else (chance)
        if (chance_modifiers == None) or (not len(chance_modifiers)):
            return chance
        return apply_chance_modifiers(chance, chance_modifiers, chance_mode)

    def get_average_value(self, skill_bonus = constants.SKILL_NONE):
        fish_quality = self.get_quality_proportions()
        base_price = self.fish_object.price
        scaled_final_prices = []
        for quality in fish_quality.keys():
            scaled_final_prices.append(scale_price_by_quality(base_price, quality) * fish_quality[quality])
        final_price = sum(scaled_final_prices)
        return floor(final_price * skill_bonus)
    
    def get_average_xp(self, treasure = False):
        # https://stardewvalleywiki.com/Fishing#Experience_Points 1.6.8
        if self.is_trap(): return 5 # Crab pots always net 5xp, no matter what

        fish_quality = self.get_quality_proportions()
        scaled_quality_xp = []
        for quality in fish_quality.keys():
            scaled_quality_xp.append( floor((quality + 1) * 3 * fish_quality[quality]) )
        resultant_xp = sum(scaled_quality_xp)
        resultant_xp = floor(resultant_xp + (float(self.difficulty) / 3))
        # Handle proportional adjustment to XP gains
        perfect_xp = 2.4 * self.get_pct_perfect()
        resultant_xp = floor(resultant_xp * perfect_xp)
        if treasure: resultant_xp = floor(resultant_xp * 2.2)
        if self.is_legendary(): resultant_xp = floor(resultant_xp * 5)
        return resultant_xp

    def has_subdata(self):
        return (self.id in game.fish_objects.keys())

    def fish_satisfies_subdata(self):
        # Satisfies by default if is trap/not in fish data
        if not self.has_subdata():
            return True
        if self.is_trap():
            return True
        # Check time. 1 2 3 4 is two checks for between 1 and 2, or between 3 and 4
        amt_intervals = int(len(self.catch_time)/2)
        passed_any_interval = False
        for interval in range(amt_intervals):
            interval_start = int(self.catch_time[(interval * 2) + 0])
            interval_end = int(self.catch_time[(interval * 2) + 1])
            # Inclusive, time may equal start time
            if game.time < interval_start:
                continue
            # Exclusive, time may not equal end time
            if game.time >= interval_end:
                continue
            passed_any_interval = True
            break
        if not passed_any_interval:
            return False
        # Seasons are unused, weather is still used
        if self.weather == "both":
            # Any weather, I guess? greenRain is new but idk.
            return True
        elif self.weather != game.weather:
            return False
        else:
            # weather == game weather
            return True

# Static functions (helpers)


def get_object_from_id(object_id:str, item_type_jsons:dict):
    object_type, object_id = process_raw_id(object_id)
    # Only supported object types
    if object_type not in ["(F)", "(O)"]:
        return None
    return item_type_jsons[object_type][object_id]

# Functions
def process_raw_id(raw_id:str) -> str:
    # theres like 8 of these holy shit why
    if raw_id.find("LavaEel_Depth") != -1:
        return "(O)", "162"
    type, id = raw_id.split(")")
    return f"{type})", id

def get_object(object_type:str, object_json:dict|str, object_id:str):
    if object_type == "(O)":
        object_json:dict = object_json
        return BaseObject(object_id, object_json)
    elif object_type == "(F)":
        object_data:str = object_json
        return FurnitureObject(object_id, object_data)
    else:
        raise NotImplementedError(f"Objects of type {object_type} not supported")

def parse_item_ids(raw_json:dict) -> list[str]:
    """Parses the Id field of an object and returns 0 or more identifiers in a list of strings."""
    raw_id:str = raw_json["Id"]
    special_queries = {
        "SECRET_NOTE_OR_ITEM": ["(O)79"],
    }
    if raw_id in special_queries.keys():
        return special_queries[raw_id]
    elif "LOCATION_FISH" in raw_id:
        location = raw_id.split(" ")[1]
        return ["RANDOM_FISH", location] # fuck that
    # if | in str, id is like "Id": "(O)167|(O)168|(O)169|(O)170|(O)171|(O)172", which means it is a random pick
    if "|" in raw_id:
        return [id for id in raw_id.split("|")]
    return [raw_id]

def scale_price_by_quality(price:int, quality:int):
    # sanity
    if quality < constants.QUALITY_NORMAL: quality = constants.QUALITY_NORMAL
    if quality > constants.QUALITY_IRIDIUM: quality = constants.QUALITY_IRIDIUM
    # scaling
    if quality == constants.QUALITY_NORMAL: return floor(price * constants.PRICE_SCALE_NORMAL)
    if quality == constants.QUALITY_SILVER: return floor(price * constants.PRICE_SCALE_SILVER)
    if quality == constants.QUALITY_GOLD: return floor(price * constants.PRICE_SCALE_GOLD)
    if quality == constants.QUALITY_IRIDIUM: return floor(price * constants.PRICE_SCALE_IRIDIUM)

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
        elif chance_mode == "stack":
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
        if quality > constants.QUALITY_IRIDIUM: return constants.QUALITY_IRIDIUM
        if quality == constants.QUALITY_IRIDIUM: return constants.QUALITY_IRIDIUM # cap at iridium
        if quality == constants.QUALITY_GOLD: return constants.QUALITY_IRIDIUM
        if quality == constants.QUALITY_SILVER: return constants.QUALITY_GOLD
        if quality == constants.QUALITY_NORMAL: return constants.QUALITY_SILVER
        if quality < constants.QUALITY_NORMAL: return constants.QUALITY_SILVER
    # Handle quality decreases
    if factor < 0:
        if quality < constants.QUALITY_NORMAL: return constants.QUALITY_NORMAL
        if quality == constants.QUALITY_NORMAL: return constants.QUALITY_NORMAL # cap at normal
        if quality == constants.QUALITY_SILVER: return constants.QUALITY_NORMAL
        if quality == constants.QUALITY_GOLD: return constants.QUALITY_SILVER
        if quality == constants.QUALITY_IRIDIUM: return constants.QUALITY_GOLD
        if quality > constants.QUALITY_IRIDIUM: return constants.QUALITY_GOLD

def get_condition(conditions:str|None, target) -> str|bool:
    """
    Gets a target condition from the comma-delimited string passed in.
    If there are no conditions, returns False.
    If the target string is not in any condition, returns False.
    If the target string is in a condition, returns the first occurence.
    """
    if conditions == None:
        return False
    all_conditions = conditions.split(",")
    for condition in all_conditions:
        if target in condition:
            return condition
    return False

def try_get_catchable(itemid:str) -> bool|CatchableData:
    return (game.fish_objects[itemid]) if (itemid in game.fish_objects.keys()) else (False)


"""

        if (any([(reward.id not in game.base_objects.keys()) for reward in fish.itemids])): continue # exclude non-objects
        # Passed, add to appropriate location
"""

def filter_catchable_fish(subloc_fish:list[FishLocation]):
    passed_fish:list[FishLocation] = []
    for fish_loc in subloc_fish:
        # Ignore one-time catchables (anything that sets flag on catch does this)
        if (fish_loc.set_flag_on_catch != None):
            continue
        # Ignore boss fish
        if (config.IGNORE_LEGENDARY_FISH and fish_loc.isbossfish):
            continue
        # Ignore QI quest fish
        if (fish_loc.condition) and (config.IGNORE_MR_QI) and not fish_loc.isbossfish and ("LEGENDARY_FAMILY" in fish_loc.condition):
            continue
        # Ignore QI beans
        if (fish_loc.condition) and (config.IGNORE_MR_QI) and ("DROP_QI_BEANS" in fish_loc.condition):
            continue
        # Ignore festival fish
        if (fish_loc.condition) and ("IS_PASSIVE_FESTIVAL_OPEN" in fish_loc.condition):
            continue
        # Ignore fish which choose a random one from sublocation (TODO: Don't do that)
        if ("RANDOM_FISH" in fish_loc.itemids):
            continue
        # Ignore weird things
        if (None in fish_loc.itemids):
            continue
        # Filter for Data/Fish
        presumed_fish = try_get_catchable(fish_loc.itemids[0].id)
        if (presumed_fish) and (not fish_loc.ignoresubdata) and (not presumed_fish.fish_satisfies_subdata()):
                continue
        # Filter magic bait
        if (fish_loc.requiremagicbait) and (not game.player.bait == constants.FISHING_BAIT_MAGIC):
            continue
        # Filter by season (none in season param means any season)
        if (fish_loc.season != None) and (str(fish_loc.season).lower() != game.season):
            continue
        # The season param is one thing, but the conditions also need parsing to check for LOCATION_SEASON (grr)
        # "LOCATION_SEASON Here spring fall" fuckin why
        condition_season = get_condition(fish_loc.condition, "LOCATION_SEASON")
        if condition_season != False:
            # Get all arguments as lowercase strings. helps for case-insensitive season checking.
            tokens = [str(token).lower() for token in condition_season.split(" ")]
            # It should look something like ["location_season", "here", "spring", "fall"] now
            if (game.season not in tokens):
                continue
        # Filter by weather is done in fish_satisfies_subdata for the most part
        # WEATHER Here Rain Storm (this is used literally ONE time for legendary fish.)
        condition_weather = get_condition(fish_loc.condition, "WEATHER")
        if condition_weather != False:
            # Get all arguments as lowercase strings. helps for case-insensitive season checking.
            tokens = [str(token).lower() for token in condition_weather.split(" ")]
            # It should look something like ["weather", "here", "rain", "storm"] now
            if game.weather not in tokens:
                continue
        # Filter by time is done in fish_satisfies_subdata
        # Filtering complete by location/season/weather/time, add as one of those which pass
        passed_fish.append(fish_loc)
    return passed_fish

# Static vars (more helpers)

game = GameObject()

item_type_objects = {
    "(O)": game.base_objects,
    "(F)": game.furniture_objects,
}
