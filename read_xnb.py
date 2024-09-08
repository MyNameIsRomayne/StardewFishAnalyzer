"""
Main file to get and interpret fish data.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""
import config
import fish_utilities as util

def main():
    from GameObject import game

    base_objects      = game.base_objects
    fish_objects      = game.fish_objects
    location_objects  = game.location_objects
    furniture_objects = game.furniture_objects

    show_fish_data = True
    # Now that we have populated objects of each whitelisted fish location in a dict, get the stats of them
    season = "summer" #"spring"
    weather = "Sunny"
    time = 650 # 1200
    results = util.get_fish_composition(config.whitelist_fish_locations, season, weather, time)
    for location in results:
        for sublocation in results[location]:
            subloc_blurb = f" ({sublocation})" if (sublocation != "null" and sublocation != location) else ""
            avg_xp = round( sum(results[location][sublocation]["xp"])/len(results[location][sublocation]["xp"]), 2)
            avg_coin = round( sum(results[location][sublocation]["coins"])/len(results[location][sublocation]["coins"]), 2)
            print(f"{location}{subloc_blurb}:")
            print(f"Avg XP: {avg_xp} | Avg Coin: {avg_coin} | Total Catchables: {len(results[location][sublocation]["fish"])}")
            for i, fish in enumerate(results[location][sublocation]["fish"]):
                names = ", ".join([obj.name for obj in fish.itemids])
                proportion  = results[location][sublocation]["weights"][i]
                proportion  = f"{round(proportion*100, 2)}%".rjust(6, " ")
                subloc_coin = results[location][sublocation]["coins"][i]
                subloc_xp   = results[location][sublocation]["xp"][i]
                if show_fish_data:
                    print(f"Reward(s): {names} | Proportion: {proportion} | Average value: {round(subloc_coin, 2)} coins | Average xp: {round(subloc_xp, 2)}")

if __name__ == "__main__":
    main()

# Errors/null mean fish trash (167-173)
# line 492 FishingRod.cs
# Item o = location.getFish(this.fishingNibbleAccumulator, bait?.QualifiedItemId, this.clearWaterDistance + (splashPoint ? 1 : 0), who, baitPotency + (splashPoint ? 0.4 : 0.0), bobberTile);
# Lower (negative) precedence is closer to front of the list, and vice versa