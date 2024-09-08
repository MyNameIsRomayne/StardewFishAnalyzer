"""
Main file to get and interpret fish data.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

from util import format2DListAsTable

def main():
    from GameObject import game

    game.post_init()

    show_fish_data = True

    game.set_season("summer")
    game.set_weather("sunny")
    game.set_time(650)

    to_analyze = ["Default", "Town"]
    results = [game.location_objects[key].get_fish_composition() for key in to_analyze]

    printable_location_data:list[list[str]] = []
    row_len = 4

    for iter, location in enumerate(results):
        if (location == None):
            continue
        location_name = to_analyze[iter]
        for sublocation in location:
            # Get format data & average XP/Coin data
            subloc_blurb = f" ({sublocation})" if (sublocation != "null" and sublocation != location) else ""
            proportional_xp = [ratio * xp for ratio, xp in zip(location[sublocation]["weights"], location[sublocation]["xp"])]
            avg_xp = round( sum(proportional_xp), 2 )
            proportional_coins = [ratio * coins for ratio, coins in zip(location[sublocation]["weights"], location[sublocation]["coins"])]
            avg_coin = round( sum(proportional_coins), 2 )
            # Add name info to location data
            location_data = [""]*row_len
            location_data[0] = f"{location_name}{subloc_blurb}"
            printable_location_data.append(location_data)
            # Add location summary data to location data
            location_data = [""]*row_len
            location_data[0] = f"Avg XP: {avg_xp}"
            location_data[1] = f"Avg Coin: {avg_coin}"
            location_data[2] = f"Total Catchables: {len(location[sublocation]["fish"])}"
            printable_location_data.append(location_data)
            # Add location data for each fish
            for i, fish in enumerate(location[sublocation]["fish"]):
                names = ", ".join([obj.name for obj in fish.itemids])
                proportion  = location[sublocation]["weights"][i]
                proportion  = f"{round(proportion*100, 2)}%".rjust(6, " ")
                subloc_coin = location[sublocation]["coins"][i]
                subloc_xp   = location[sublocation]["xp"][i]
                if show_fish_data:
                    location_data = [""]*row_len
                    location_data[0] = f"{names}"
                    location_data[1] = f"Proportion: {proportion}"
                    location_data[2] = f"Value: {round(subloc_coin, 2)} coins"
                    location_data[3] = f"XP: {round(subloc_xp, 2)}"
                    printable_location_data.append(location_data)
    
    print(format2DListAsTable(printable_location_data, char_limit=20))

if __name__ == "__main__":
    main()

# Errors/null mean fish trash (167-173)
# line 492 FishingRod.cs
# Item o = location.getFish(this.fishingNibbleAccumulator, bait?.QualifiedItemId, this.clearWaterDistance + (splashPoint ? 1 : 0), who, baitPotency + (splashPoint ? 0.4 : 0.0), bobberTile);
# Lower (negative) precedence is closer to front of the list, and vice versa