"""
Main file to get and interpret fish data.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

from util import format2DListAsTable
import config

def classic_to_internal(classical_time:str) -> int:
    """Turn times like 6:59 AM into 659, and 6:59 PM to 1859 (24 hr time)"""
    final_time = 0
    hours, minutes = classical_time.split(":")
    minutes, am_or_pm = minutes[0:2], minutes[2:].lower()
    hours, minutes = int(hours), int(minutes)
    # Add base time
    final_time += (hours * 100)
    final_time += (minutes * 1)
    # Factor in AM/PM
    if (am_or_pm == "pm"):
        final_time += 1200
    return final_time

def main():
    from GameObject import game

    # Setup some internal config
    SHOW_FISH = True
    FISHING_LEVEL = 1
    SEASON = config.SEASON_SPRING
    WEATHER = config.WEATHER_SUNNY
    TIME = classic_to_internal("6:00AM")
    LOCATIONS = [config.LOCATION_BEACH]
    SCALE_PCT_PERFECT_CATCHES = 0.5
    BAIT_USED = config.FISHING_BAIT_NONE
    BAIT_TARGET_ID = "128" # pufferfish
    WATER_DEPTH = 4

    # Act upon above info
    game.post_init()
    game.season = SEASON
    game.weather = WEATHER
    game.time = TIME

    game_player = game.player
    game_player.fishing_level = FISHING_LEVEL
    game_player.pct_perfect = SCALE_PCT_PERFECT_CATCHES
    game_player.bait = BAIT_USED
    game_player.bait_target_id = BAIT_TARGET_ID
    game_player.fishing_depth = WATER_DEPTH

    results = [game.location_objects[key].get_fish_composition() for key in LOCATIONS]

    printable_location_data:list[list[str]] = []
    row_len = 4
    column_char_limit = 20

    for iter, location in enumerate(results):
        if (location == None):
            continue
        location_name = LOCATIONS[iter]
        for sublocation in location:
            # Get format data & average XP/Coin data
            subloc_blurb = f" ({sublocation})" if (sublocation != "null" and sublocation != location) else ""
            proportional_xp = [ratio * xp for ratio, xp in zip(location[sublocation]["weights"], location[sublocation]["xp"])]
            avg_xp = round( sum(proportional_xp), 2 )
            proportional_coins = [ratio * coins for ratio, coins in zip(location[sublocation]["weights"], location[sublocation]["coins"])]
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
                proportion  = location[sublocation]["weights"][i]
                proportion  = f"{round(proportion*100, 2)}%".rjust(6, " ")
                subloc_coin = location[sublocation]["coins"][i]
                subloc_xp   = location[sublocation]["xp"][i]
                if SHOW_FISH:
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