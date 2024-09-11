import constants

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
        if constants.IGNORE_IRRELEVANT_JSON: return
        
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