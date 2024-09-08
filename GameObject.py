
import config
import GameReader as gr
from math import floor

class GameObject():
    
    def __init__(self):
        # Setup object data
        self.base_objects:dict[str, BaseObject]           = gr.get_objects(config.objects_file,   config.objects_file_py,   BaseObject)
        self.fish_objects:dict[str, CatchableData]        = gr.get_objects(config.fish_file,      config.fish_file_py,      CatchableData)
        self.location_objects:dict[str, GameLocation]     = gr.get_objects(config.locations_file, config.locations_file_py, GameLocation)
        self.furniture_objects:dict[str, FurnitureObject] = gr.get_objects(config.furniture_file, config.furniture_file_py, FurnitureObject)   

class GameLocation():

    def __init__(self, id:str, json_data:dict):
        self.id = id
        self.fish:list[FishLocation] = [FishLocation(data_json) for data_json in json_data["Fish"]]
        # FishAreas is a dict keyed by location ID, we just need to show location IDs to users. Noone cares about crab pots/bounds right? >:3
        self.areas = [key for key in json_data["FishAreas"].keys()]

class FurnitureObject():

    def __init__(self, id:str, data:str):
        split_data:list[str] = data.split("/")
        TOTAL_ARGS = len(split_data)
        # Setup index descriptors for readability's sake
        INDEX_NAME = 0
        INDEX_TYPE = 1
        # Setup vars

        # Internal item ID
        self.id = id
        # Internal item name / Display name in English
        self.name:str = split_data[INDEX_NAME]
        
        # Don't worry about anything beyond this point unless you need any of the below.
        # If you need anything marked irrelevant, just change the code so it's up here.
        if config.IGNORE_IRRELEVANT_JSON: return
        
        INDEX_TILESHEET_SIZE = 2
        INDEX_BOUNDING_BOX_SIZE = 3
        INDEX_ROTATIONS_POSSIBLE = 4
        INDEX_SHOP_PRICE = 5
        INDEX_PLACEMENT_RESTRICTION = 6
        INDEX_DISPLAY_NAME = 7
        INDEX_SPRITE_INDEX = 8
        INDEX_TEXTURE = 9
        INDEX_RESTRICT_RANDOM_SALE = 10
        INDEX_CONTEXT_TAGS = 11
            
        # Furniture type. This may either be its corresponding name (str) or a stringified num (0-17 inclusive)
        self.type:str = split_data[INDEX_TYPE]
        # Size of tilesheet. This can be [width, height] or [-1] for default of type.
        self.tilesheet_size:list[int] = str(split_data[INDEX_TILESHEET_SIZE]).split(" ")
        # Size of bounding box, in tiles. [width, height] or [-1] for default of type.
        self.bounding_box_size:list[int] = str(split_data[INDEX_BOUNDING_BOX_SIZE]).split(" ")
        # How many times it can be rotated, if at all. If not rotatable, value is 1, if two ways, 2, if four ways, 4.
        self.rotations_possible:int = int(split_data[INDEX_ROTATIONS_POSSIBLE])
        # The price, NOT WHEN SOLD, but when BOUGHT, from a shop.
        self.shop_price:int = int(split_data[INDEX_SHOP_PRICE])
        # Placement restriction for default (-1), indoors only (0), outdoors only (1), or both (2).
        self.placement_restriction:int = int(split_data[INDEX_PLACEMENT_RESTRICTION])
        # The tokenized string for the display name, before localization.
        self.display_name:str = str(split_data[INDEX_DISPLAY_NAME])
        # At this point, future values may not exist. Check for limit on each of these
        # The sprite index. Default 0
        if TOTAL_ARGS < 8:
            self.sprite_index:int = 0
            self.texture:str = "TileSheets/furniture"
            self.restrict_random_sale:bool = False
            self.context_tags:list[str]|None = None
            return
        self.sprite_index:int = int(split_data[INDEX_SPRITE_INDEX]) if (split_data[INDEX_SPRITE_INDEX] != '') else 0
        # The texture path. Default "TileSheets/furniture"
        if TOTAL_ARGS < 9:
            self.texture:str = "TileSheets/furniture"
            self.restrict_random_sale:bool = False
            self.context_tags:list[str]|None = None
        self.texture:str = split_data[INDEX_TEXTURE] if (split_data[INDEX_TEXTURE] != '') else "TileSheets/furniture"
        # Whether to restrict it randomly appearing for sale in shops. Default False
        if TOTAL_ARGS < 10:
            self.restrict_random_sale:bool = False
            self.context_tags:list[str]|None = None
            return
        self.restrict_random_sale:bool = bool(split_data[INDEX_RESTRICT_RANDOM_SALE]) if (split_data[INDEX_RESTRICT_RANDOM_SALE] != '') else False
        # Any modded context tags. Default None
        if TOTAL_ARGS < 11:
            self.context_tags:dict|None = None
        self.context_tags:list[str]|None = split_data[INDEX_CONTEXT_TAGS].split(" ") if (split_data[INDEX_CONTEXT_TAGS] != '') else None

class FishLocation():
    
    def __init__(self, json_data:dict):
        self.setup_itemids = False
        self.chance = json_data["Chance"]
        self.season = json_data["Season"]
        self.fishareaid = json_data["FishAreaId"]
        self.precedence = json_data["Precedence"]
        self.isbossfish = json_data["IsBossFish"]
        self.requiremagicbait = json_data["RequireMagicBait"]
        self.chancemodifiers = json_data["ChanceModifiers"]
        self.chancemodifiermode = json_data["ChanceModifierMode"]
        self.chanceboostperlucklevel = json_data["ChanceBoostPerLuckLevel"]
        self.itemids:list[BaseObject] = parse_item_ids(json_data)
        self.quality = json_data["Quality"]
        self.condition = json_data["Condition"]
        self.ignoresubdata = json_data["IgnoreFishDataRequirements"]
    
    def __str__(self):
        return self.itemids[0].name

    def get_itemids(self):
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

    def refresh_fish_obj(self) -> None:
        self.fish_object = game.base_objects[self.id]

    def is_trap(self) -> bool:
        """Getter for whether or not this is found in crab pot traps."""
        return self.istrap

    def is_legendary(self) -> bool:
        """Gets whether this fish is a legendary fish."""
        self.refresh_fish_obj()
        return (self.fish_object.context_tags != None) and ("fish_legendary" in self.fish_object.context_tags)

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
            return config.QUALITY_NORMAL
        if size < 0.66:
            return config.QUALITY_SILVER
        return config.QUALITY_GOLD

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

    def get_average_value(self, fish_quality:int = None, skill_bonus = config.SKILL_NONE):
        self.refresh_fish_obj()
        fish_quality = self.get_average_quality() if (fish_quality == None) else fish_quality
        base_price = self.fish_object.price
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

    def has_subdata(self):
        return (self.id in game.fish_objects.keys())

    def fish_satisfies_subdata(self, current_season, current_weather, current_time):
        # Satisfies by default if is trap/not in fish data
        if not self.has_subdata():
            return True
        fish_raw_data = str(game.fish_objects[self.id]).split("/")
        if fish_raw_data[1] == "trap":
            return True
        # Check time
        INDEX_TIME_DATA = 5
        INDEX_SEASONS = 6
        times = fish_raw_data[INDEX_TIME_DATA].split(" ")
        # 1 2 3 4 is two checks for between 1 and 2, or between 3 and 4
        amt_intervals = int(len(times)/2)
        passed_any_interval = False
        for interval in range(amt_intervals):
            interval_start = int(times[(interval * 2) + 0])
            interval_end = int(times[(interval * 2) + 1])
            # Inclusive, time may equal start time
            if current_time < interval_start:
                continue
            # Exclusive, time may not equal end time
            if current_time >= interval_end:
                continue
            passed_any_interval = True
            break
        if not passed_any_interval:
            return False
        # Checks for time over, check season
        seasons = fish_raw_data[INDEX_SEASONS].split(" ")
        if current_season not in seasons:
            return False
        return True

class BaseObject():
  
  def __init__(self, id:str, json:dict[str]):
    # The ID of this item, of which was used to look it up in Objects.json
    self.id = id
    # The internal name of the item, typically just its name in english.
    self.name:str = json["Name"]
    # The price of this when sold (not bought). Defaults to 0
    self.price:int = json["Price"]
    # Any context for the object. color, season, caught location, etc.
    self.context_tags:list|None = json["ContextTags"]

    if config.IGNORE_IRRELEVANT_JSON: return

    # The name, formatted as a localization query
    self.display_name:str = json["DisplayName"]
    # Description of the item, formatted as a localization query
    self.description:str = json["Description"]
    # The type of this object, represented by a (usually) human readable name
    self.type:str = json["Type"]
    # Some item category represented by a number.
    self.category:int = json["Category"]
    # Texture file, which defaults to Maps/springobjects.
    self.texture:str|None = json["Texture"]
    # Index of this in the sprite sheet, where 0 is the top-left
    self.spriteindex:int = json["SpriteIndex"]
    # Edibility value for how much energy/health (this*2.5, this*1.125) is restored when eaten.
    # -300 means inedible, default is also -300
    self.edibility:int = json["Edibility"]
    # Whether to drink instead of eating. Deault false
    self.isdrink:bool = json["IsDrink"]
    # List of buffs given to the player, if applicable
    self.buffs:list|None = json["Buffs"]
    self.geode_drops_default_items:bool = json["GeodeDropsDefaultItems"]
    # List of potential geode drops, if applicable
    self.geode_drops:list|None = json["GeodeDrops"]
    # Chance for an artifact (this) to spawn if checked (0-1)
    self.artifact_spot_chance:float = json["ArtifactSpotChances"]
    # Whether to excluse it from the fishing collection, default False
    self.exclude_from_fishing_collection:bool = json["ExcludeFromFishingCollection"]
    # Whether to exclude this item from the shipping collection, default false
    self.exclude_from_shipping_collection:bool = json["ExcludeFromShippingCollection"]
    # Whether to exclude this item from being sold at random in shops, default False
    self.exclude_from_random_sale:bool = json["ExcludeFromRandomSale"]
    # Optional custom fields used by modders. default None
    self.custom_fields:dict|None = json["CustomFields"]

# Static functions (helpers)


def get_object_from_id(object_id:str, item_type_jsons:dict):
    object_type, object_id = process_raw_id(object_id)
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
    if quality < config.QUALITY_NORMAL: quality = config.QUALITY_NORMAL
    if quality > config.QUALITY_IRIDIUM: quality = config.QUALITY_IRIDIUM
    # scaling
    if quality == config.QUALITY_NORMAL: return floor(price * config.PRICE_SCALE_NORMAL)
    if quality == config.QUALITY_SILVER: return floor(price * config.PRICE_SCALE_SILVER)
    if quality == config.QUALITY_GOLD: return floor(price * config.PRICE_SCALE_GOLD)
    if quality == config.QUALITY_IRIDIUM: return floor(price * config.PRICE_SCALE_IRIDIUM)

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
        if quality > config.QUALITY_IRIDIUM: return config.QUALITY_IRIDIUM
        if quality == config.QUALITY_IRIDIUM: return config.QUALITY_IRIDIUM # cap at iridium
        if quality == config.QUALITY_GOLD: return config.QUALITY_IRIDIUM
        if quality == config.QUALITY_SILVER: return config.QUALITY_GOLD
        if quality == config.QUALITY_NORMAL: return config.QUALITY_SILVER
        if quality < config.QUALITY_NORMAL: return config.QUALITY_SILVER
    # Handle quality decreases
    if factor < 0:
        if quality < config.QUALITY_NORMAL: return config.QUALITY_NORMAL
        if quality == config.QUALITY_NORMAL: return config.QUALITY_NORMAL # cap at normal
        if quality == config.QUALITY_SILVER: return config.QUALITY_NORMAL
        if quality == config.QUALITY_GOLD: return config.QUALITY_SILVER
        if quality == config.QUALITY_IRIDIUM: return config.QUALITY_GOLD
        if quality > config.QUALITY_IRIDIUM: return config.QUALITY_GOLD

# Static vars (more helpers)

game = GameObject()

item_type_objects = {
    "(O)": game.base_objects,
    "(F)": game.furniture_objects,
}
