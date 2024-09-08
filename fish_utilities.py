"""
Primary file for getting fish stuff.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import numpy as np

from config import objects_json, fish_json
from ProbsAlgorithm import get_probs

from CatchableData import CatchableData
from FishLocation import FishLocation
from GameLocation import GameLocation
from BaseObject import BaseObject

def get_fish_into_subareas(location:GameLocation) -> dict[str, list[FishLocation]]:
    """
    Get the fish in the area keyed by the FishAreaId they have.
    Any fish with null fish ID go into a subarea called "null".
    Fish are excluded from any given list if they are:
    - Part of the LEGENDARY_FAMILY quest
    - Are a legendary fish
    - Have a null itemids parameter
    - Have a reward which is not an object
    """
    # Handle custom keys, any location with a null key goes into "null". which i *know* is stupid but i donmt care
    locations = {"null": []}
    for key in location.areas:
        locations[key] = []
    # Hand pick the fishing spots to consider
    for fish in location.fish:
        if fish.isbossfish: continue # exclude legendaries
        if (fish.condition) and ("LEGENDARY_FAMILY" in fish.condition): continue # exclude Mr Qi quests
        if None in fish.itemids: continue # exclude weird things
        if any([(reward.id not in objects_json.keys()) for reward in fish.itemids]): continue # exclude non-objects
        # if "RANDOM_FISH" in fish.itemids:
        #     
        # Passed, add to appropriate location
        if fish.fishareaid == None:
            locations["null"].append(fish)
        else:
            locations[fish.fishareaid].append(fish)
    return locations

def get_items_from(locations:list[FishLocation], loc):
    items = []
    location = locations[loc]
    for fishloc in location:
        items += fishloc.itemids
    return items

def get_condition(conditions:str|None, target):
    if conditions == None:
        return False
    all_conditions = conditions.split(",")
    for condition in all_conditions:
        if target in condition:
            return condition
    return False

def fish_satisfies_subdata(fish_loc:FishLocation, season:str, weather:str, time:int):
    presumed_item = fish_loc.itemids[0]
    # Satisfies by default if is trap/not in fish data
    if not presumed_item.id in fish_json.keys():
        return True
    fish_raw_data = str(fish_json[presumed_item.id]).split("/")
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
        if time < interval_start:
            continue
        # Exclusive, time may not equal end time
        if time >= interval_end:
            continue
        passed_any_interval = True
        break
    if not passed_any_interval:
        return False
    # Checks for time over, check season
    seasons = fish_raw_data[INDEX_SEASONS].split(" ")
    if season not in seasons:
        return False
    return True

def get_subloc_fish_comp(subloc_fish:list[FishLocation], season:str=None, weather:str=None, time:int=None, usingMagicBait:bool=False):
    passed_fish:list[FishLocation] = []
    for fish_loc in subloc_fish:
        # Ignore QI beans
        if (fish_loc.condition) and ("DROP_QI_BEANS" in fish_loc.condition):
            continue
        # Filter for Data/Fish
        if (not fish_loc.ignoresubdata) and (not fish_satisfies_subdata(fish_loc, season, weather, time)):
                continue
        # Filter magic bait
        if (fish_loc.requiremagicbait) and (not usingMagicBait):
            continue
        # Filter by season
        if (season != None):
            season_lowercase = season.lower()
            # The season param is one thing, but the conditions also need parsing to check for LOCATION_SEASON
            if ((fish_loc.season != None) and (fish_loc.season != season)):
                continue
            # "LOCATION_SEASON Here spring fall" fuckin why
            condition_season = get_condition(fish_loc.condition, "LOCATION_SEASON")
            if condition_season != False:
                # Get all arguments as lowercase strings. helps for case-insensitive season checking.
                tokens = [str(token).lower() for token in condition_season.split(" ")]
                # It should look something like ["location_season", "here", "spring", "fall"] now
                if season_lowercase not in tokens:
                    continue
        # Filter by weather
        if (weather != None):
            weather_lowercase = weather.lower()
            # WEATHER Here Rain Storm
            condition_weather = get_condition(fish_loc.condition, "WEATHER")
            if condition_weather != False:
                # Get all arguments as lowercase strings. helps for case-insensitive season checking.
                tokens = [str(token).lower() for token in condition_season.split(" ")]
                # It should look something like ["weather", "here", "rain", "storm"] now
                if weather_lowercase not in tokens:
                    continue
        # Filter by time is done in fish_satisfies_subdata
        # Filtering complete by location/season/weather/time, add as one of those which pass
        passed_fish.append(fish_loc)
    return passed_fish

def get_fish_composition(locations:dict[str, GameLocation], location_objs: dict[str, GameLocation], fish_objs:dict[str, CatchableData],
                         objects_json:dict[str, BaseObject], season:str, weather:str, time:int):
    loc_dicts:dict[str, dict[str, dict[str, list[GameLocation]]]] = {}

    # Setup all the sublocs with fish into the above dict by location, sublocation, and then precedence
    for key in locations:
        location = location_objs[key]
        # Go over each sublocation in the location and process *those* individually
        sublocations = get_fish_into_subareas(location)
        loc_dicts[key] = {}
        for sublocation in sublocations.keys():

            fish_locations:list[FishLocation] = [e for e in sublocations[sublocation]]
            if key != "Default":
                # Everyone except default get a copy of default
                fish_locations += [loc for loc in location_objs["Default"].fish]
            catchables = get_subloc_fish_comp(fish_locations, season, weather, time)
            subloc_by_precedence:dict[str, list[FishLocation]] = {}
            for c in catchables:
                matching_key = str(c.precedence)
                if matching_key not in subloc_by_precedence:
                    subloc_by_precedence[matching_key] = []
                subloc_by_precedence[matching_key].append(c)

            loc_dicts[key][sublocation] = subloc_by_precedence
    
    # Repack everything back into lists from precedence
    loc_dicts_refined:dict[str, dict[str, list[FishLocation]]] = {}
    for primary_loc_key in loc_dicts.keys():
        loc_dicts_refined[primary_loc_key] = {}
        for sub_loc_key in loc_dicts[primary_loc_key].keys():
            loc_dicts_refined[primary_loc_key][sub_loc_key] = {}
            precedence_markers = [int(e) for e in loc_dicts[primary_loc_key][sub_loc_key]]
            precedence_markers.sort()
            # Setup initial lists for subloc
            loc_dicts_refined[primary_loc_key][sub_loc_key]["weights"] = []
            loc_dicts_refined[primary_loc_key][sub_loc_key]["fish"] = []
            loc_dicts_refined[primary_loc_key][sub_loc_key]["xp"] = []
            loc_dicts_refined[primary_loc_key][sub_loc_key]["coins"] = []
            # This is just for ease of reading
            fish_list:list = loc_dicts_refined[primary_loc_key][sub_loc_key]["fish"]
            weights_list:list = loc_dicts_refined[primary_loc_key][sub_loc_key]["weights"]
            chance_fail_all_previous = 1
            for marker in precedence_markers:
                marker = str(marker)
                fish_list += loc_dicts[primary_loc_key][sub_loc_key][marker]
                chance_list = []
                for loc in loc_dicts[primary_loc_key][sub_loc_key][marker]:
                    loc:FishLocation
                    loc_chance = loc.chance
                    # Yes, it also calculates this. ugh..
                    specific_fish_chance = 1
                    fish_id = loc.itemids[0].id
                    if fish_id in fish_objs.keys():
                        fish_object = fish_objs[fish_id]
                        specific_fish_chance = fish_object.get_average_chance()
                    chance_list.append(loc_chance * specific_fish_chance)
                current_weights = get_probs(np.array(chance_list))
                sum_current_weights = sum(current_weights)
                reduced_weights = [weight * chance_fail_all_previous for weight in current_weights]
                weights_list += reduced_weights
                chance_fail_all_previous *= (1 - sum_current_weights)
    
            # Add price/xp stats
            coins_list:list = loc_dicts_refined[primary_loc_key][sub_loc_key]["coins"]
            xp_list:list = loc_dicts_refined[primary_loc_key][sub_loc_key]["xp"]
            for fish in loc_dicts_refined[primary_loc_key][sub_loc_key]["fish"]:
                fish:FishLocation
                sum_coins = 0
                sum_xp = 0
                # Handle getting all the objects to use
                for loot_id in [obj.id for obj in fish.itemids]:
                    value, xp = 0, 0
                    # Coins might be yoinkable from here first if it isnt a fish
                    if loot_id in objects_json.keys():
                        value = objects_json[loot_id].price
                    # If it is, we can get coins AND xp
                    if loot_id in fish_objs.keys():
                        value = fish_objs[loot_id].get_average_value()
                        xp = fish_objs[loot_id].get_average_xp()
                    # Finally, add it to the sum
                    sum_coins += value
                    sum_xp += xp
                # Got all the catchables, add relevant data to lists
                coins_list.append(sum_coins/len(fish.itemids))
                xp_list.append(sum_xp/len(fish.itemids))

    return loc_dicts_refined
