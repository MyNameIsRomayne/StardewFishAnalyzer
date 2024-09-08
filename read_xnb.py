"""
Main file to get and interpret fish data.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""
import config

def main():
    from GameObject import game

    game.post_init()

    show_fish_data = True

    game.set_season("summer")
    game.set_weather("sunny")
    game.set_time(650)

    to_analyze = ["Default", "Forest"]
    results = [game.location_objects[key].get_fish_composition() for key in to_analyze]

    for iter, location in enumerate(results):
        location_name = to_analyze[iter]
        for sublocation in location:
            subloc_blurb = f" ({sublocation})" if (sublocation != "null" and sublocation != location) else ""
            avg_xp = round( sum(location[sublocation]["xp"])/len(location[sublocation]["xp"]), 2)
            avg_coin = round( sum(location[sublocation]["coins"])/len(location[sublocation]["coins"]), 2)
            print(f"{location_name}{subloc_blurb}:")
            print(f"Avg XP: {avg_xp} | Avg Coin: {avg_coin} | Total Catchables: {len(location[sublocation]["fish"])}")
            for i, fish in enumerate(location[sublocation]["fish"]):
                names = ", ".join([obj.name for obj in fish.itemids])
                proportion  = location[sublocation]["weights"][i]
                proportion  = f"{round(proportion*100, 2)}%".rjust(6, " ")
                subloc_coin = location[sublocation]["coins"][i]
                subloc_xp   = location[sublocation]["xp"][i]
                if show_fish_data:
                    print(f"Reward(s): {names} | Proportion: {proportion} | Average value: {round(subloc_coin, 2)} coins | Average xp: {round(subloc_xp, 2)}")

if __name__ == "__main__":
    main()

# Errors/null mean fish trash (167-173)
# line 492 FishingRod.cs
# Item o = location.getFish(this.fishingNibbleAccumulator, bait?.QualifiedItemId, this.clearWaterDistance + (splashPoint ? 1 : 0), who, baitPotency + (splashPoint ? 0.4 : 0.0), bobberTile);
# Lower (negative) precedence is closer to front of the list, and vice versa