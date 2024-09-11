"""
Main file to get and interpret fish data.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

from utils import format2DListAsTable
import constants
import config

def main():
    from game_object import game
    
    game.post_init()
    game.season  = config.SEASON
    game.weather = config.WEATHER
    game.time    = config.TIME

    # Setup the player values
    game_player = game.player
    game_player.fishing_level  = config.FISHING_LEVEL
    game_player.pct_perfect    = config.SCALE_PCT_PERFECT_CATCHES
    game_player.fishing_rod    = config.ROD_USED
    game_player.bait           = config.BAIT_USED
    game_player.bait_target_id = config.BAIT_TARGET_ID
    game_player.fishing_depth  = config.WATER_DEPTH

    BAIT_TARGET_NAME = (game.base_objects[config.BAIT_TARGET_ID].name) if (config.BAIT_USED == constants.FISHING_BAIT_TARGETED) else ("none")
    # Print out initial data
    initial_data = [
        [f"Season: {game.season}", f"Weather: {game.weather}", f"Time: {config.internal_to_classic(config.TIME)}"],
        [f"Depth: {config.WATER_DEPTH}", f"Bait: {config.BAIT_USED}", f"Bait Target: {BAIT_TARGET_NAME}"],
        [f"Fishing Level: {config.FISHING_LEVEL}", f"Perfect catches: {config.SCALE_PCT_PERFECT_CATCHES*100}%", f"Rod used: {config.ROD_USED}"]
    ]
    print(format2DListAsTable(initial_data, char_limit=30))

    results = [game.location_objects[key].get_composition() for key in config.LOCATIONS]

    printable_location_data:list[list[str]] = []
    row_len = 4
    column_char_limit = 20

    for iter, location in enumerate(results):
        if (location == None):
            continue
        location_name = config.LOCATIONS[iter]
        for sublocation in location:
            # Get format data & average XP/Coin data
            if location[sublocation] == None:
                continue
            subloc_blurb = f" ({sublocation})" if (sublocation != "none" and sublocation != location) else ""
            proportional_xp = [ratio * xp for ratio, xp in zip(location[sublocation]["chances"], location[sublocation]["xp"])]
            avg_xp = round( sum(proportional_xp), 2 )
            proportional_coins = [ratio * coins for ratio, coins in zip(location[sublocation]["chances"], location[sublocation]["coins"])]
            avg_coin = round( sum(proportional_coins), 2 )
            # Add location summary data to location data
            location_data = [""]*row_len
            printable_location_data.append([""]*row_len)
            location_data[0] = f"{location_name}{subloc_blurb}"
            location_data[1] = f"Total Catchables: {len(location[sublocation]["fish"])}"
            location_data[2] = f"Avg Coin: {avg_coin}"
            location_data[3] = f"Avg XP: {avg_xp}"
            printable_location_data.append(location_data)
            printable_location_data.append(["-"*column_char_limit]*row_len)
            # Add location data for each fish
            for i, fish in enumerate(location[sublocation]["fish"]):
                names = ", ".join([obj.name for obj in fish.itemids])
                proportion  = location[sublocation]["chances"][i]
                proportion  = f"{round(proportion*100, 2)}%".rjust(6, " ")
                subloc_coin = location[sublocation]["coins"][i]
                subloc_xp   = location[sublocation]["xp"][i]
                if config.SHOW_FISH:
                    location_data = [""]*row_len
                    location_data[0] = f"{names}"
                    location_data[1] = f"Proportion: {proportion}"
                    location_data[2] = f"Value: {round(subloc_coin, 2)} coins"
                    location_data[3] = f"XP: {round(subloc_xp, 2)}"
                    printable_location_data.append(location_data)
    
    print(format2DListAsTable(printable_location_data, char_limit=column_char_limit, column_delimiter="   "))

if __name__ == "__main__":
    main()

# Errors/null mean fish trash (167-173)
# line 492 FishingRod.cs
# Item o = location.getFish(this.fishingNibbleAccumulator, bait?.QualifiedItemId, this.clearWaterDistance + (splashPoint ? 1 : 0), who, baitPotency + (splashPoint ? 0.4 : 0.0), bobberTile);
# Lower (negative) precedence is closer to front of the list, and vice versa