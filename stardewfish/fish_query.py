"""
File which handles querying information about some given fish/ID
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

from stardewfish.game_object import game
from stardewfish.base_object import BaseObject
from stardewfish.game_object import CatchableData, scale_price_by_quality
from stardewfish.utils       import format2DListAsTable, military_to_classic

import config
import constants

def handle_fish_query(value:str):
    game.post_init()

    target:BaseObject = None
    # If its all numbers, its an object ID -- so try and look it up
    if (value.isnumeric()):
        if (value in game.base_objects.keys()):
            target = game.base_objects[value]
        else:
            print(f"Item ID {value} not found.")
            return
    else:
        # Go through all names and check if it matches any, then ask between matches
        value = value.lower()
        matches:list[BaseObject] = []
        for object in [game.base_objects[key] for key in game.base_objects.keys()]:
            if value in object.name.lower():
                matches.append(object)
        if (len(matches) == 0):
            print(f"Name {value} not found.")
            return
        elif len(matches) == 1:
            target = matches[0]
        else:
            print(f"Mutliple matches of {value} found. Please select appropriate target manually:")
            [print(f"({i}): {fish.name}") for i, fish in enumerate(matches)]
            selection = input()
            try:
                target = matches[int(selection)]
            except IndexError:
                print("Invalid selection.")
                quit()


    # At this point, we have target -- so get some dang info on it!    
    try:
        catchable = game.fish_objects[target.id]
    except KeyError:
        print("ERROR: Not a fish. Aborting")
        quit()

    # Print out preliminary info now that we have the target
    print("Game and Player context:")
    BAIT_TARGET_NAME = (game.base_objects[config.BAIT_TARGET_ID].name) if (config.BAIT_USED == constants.FISHING_BAIT_TARGETED) else ("none")
    # Print out initial data
    initial_data = [
        [f"Season: {game.season}", f"Weather: {game.weather}", f"Time: {military_to_classic(config.TIME)}"],
        [f"Depth: {config.WATER_DEPTH}", f"Bait: {config.BAIT_USED}", f"Bait Target: {BAIT_TARGET_NAME}"],
        [f"Fishing Level: {config.FISHING_LEVEL}", f"Perfect catches: {config.SCALE_PCT_PERFECT_CATCHES*100}%", f"Rod used: {config.ROD_USED}"]
    ]
    print(format2DListAsTable(initial_data, column_delimiter="   "), end="\n\n")

    # Min/max size relative to player data
    min_size_rel, max_size_rel = catchable.get_fish_size_ranges()
    min_size_rel, max_size_rel = min_size_rel*float(catchable.min_size), max_size_rel*float(catchable.max_size)

    quality_proportions_unformatted = catchable.get_quality_proportions()
    formatpct = lambda k: f"{round(quality_proportions_unformatted[k]*100, 2)}%"

    scaled_values = [scale_price_by_quality(target.price, quality) for quality in quality_proportions_unformatted.keys()]
    scaled_xp     = []
    scaled_pct_perfect = f"{round(100*catchable.get_pct_perfect(), 2)}%"

    data = [
        [f"Name: {target.name}",  f"Object ID: {target.id}", f"Avg. XP: {catchable.get_average_xp()}", f"Avg. Coins: {catchable.get_average_value()}", f"Scaled % Perfect: {scaled_pct_perfect}\n"],
        ["Absolute min. size",    "Absolute max. size",      "Practical min. size",                    "Practical max. size",                          ""],
        [f"{catchable.min_size}", f"{catchable.max_size}",   f"{min_size_rel}",                        f"{max_size_rel}",                              "\n"],
        [ "",                     "Normal",                  "Silver",                                 "Gold",                                         "Iridium"],
        [ "Quality:",             f"{formatpct(0)}",         f"{formatpct(1)}",                        f"{formatpct(2)}",                              f"{formatpct(4)}"],
        [ "Value:",               f"{scaled_values[0]}",     f"{scaled_values[1]}",                    f"{scaled_values[2]}",                          f"{scaled_values[3]}"]
    ]
    print("Fish context:")
    print(format2DListAsTable(data, column_delimiter="   "))
