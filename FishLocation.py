"""
A helpful class which converts some JSON object into a readable python object.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

from BaseObject import BaseObject
from FurnitureObject import FurnitureObject
from config import item_type_jsons

class FishLocation():
    
    def __init__(self, json_data:dict):
        itemids = parse_item_ids(json_data)
        if "RANDOM_FISH" not in itemids:
            itemids = [get_object_from_id(itemid, item_type_jsons) for itemid in itemids]
        self.chance = json_data["Chance"]
        self.season = json_data["Season"]
        self.fishareaid = json_data["FishAreaId"]
        self.precedence = json_data["Precedence"]
        self.isbossfish = json_data["IsBossFish"]
        self.requiremagicbait = json_data["RequireMagicBait"]
        self.chancemodifiers = json_data["ChanceModifiers"]
        self.chancemodifiermode = json_data["ChanceModifierMode"]
        self.chanceboostperlucklevel = json_data["ChanceBoostPerLuckLevel"]
        self.itemids:list[BaseObject] = itemids
        self.quality = json_data["Quality"]
        self.condition = json_data["Condition"]
        self.ignoresubdata = json_data["IgnoreFishDataRequirements"]
    
    def __str__(self):
        return self.itemids[0].name

def get_object_from_id(object_id:str, item_type_jsons:dict):
    object_type, object_id = process_raw_id(object_id)
    try:
        object_json = item_type_jsons[object_type][object_id]
    except KeyError: # fuck (H)
        return None
    return get_object(object_type, object_json, object_id)

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
