import constants

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

    if constants.IGNORE_IRRELEVANT_JSON: return

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