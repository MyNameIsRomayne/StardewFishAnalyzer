"""
A helpful class which converts some JSON object into a readable python object.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

from FishLocation import FishLocation

class GameLocation():

    def __init__(self, id:str, json_data:dict):
        self.id = id
        self.fish:list[FishLocation] = [FishLocation(data_json) for data_json in json_data["Fish"]]
        # FishAreas is a dict keyed by location ID, we just need to show location IDs to users. Noone cares about crab pots/bounds right? >:3
        self.areas = [key for key in json_data["FishAreas"].keys()]
        