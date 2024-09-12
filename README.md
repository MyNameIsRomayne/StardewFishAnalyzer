# Stardew Valley Fish Data Analyzer

## Preamble

This is a personal project currently owned and contributed by one person (me, Romayne). This project is far from being complete or accurate, but is somewhat usable in its current state. All contributions and issues are welcome, as well as feature requests. The intent of open-sourcing this project is to garner feedback and contributions, with such contributions ideally being in parts of the project which I have been unable to complete myself. That being said, I hope you can enjoy the project as it is now.

## What is this?

The Stardew Fish Data Analyzer (SFDA?) is a command-line utility program which aims to ease lookups of fish information and relevant fishing spot information by allowing the use of simple positional arguments to find such information. Currently supported is the ability to look up individual fish and entire locations, the statistics reported of each depending on the internal configuration.

## Installing

The project can be installed as-is from the source code, so long as you have the sufficient Python interpreter installed to do so -- anecotaly, I use **Python Version 3.12.4** as of writing -- other versions should work fine, too. Additionally, requirements can be installed from `requirements.txt`, which currently only consists of numpy.

You can check your python version with:
`python --version`

To install this repository and its packages, navigate to the directory you would like it to be in, and execute the following commands:
`git clone https://github.com/MyNameIsRomayne/StardewFishAnalyzer.git`
`python -m pip install -r requirements.txt`

This should always complete successfully. If you get an error, please check your python version / packages again.

## Usage

Usage is simple -- nagivate to the root directory of the project, and execute a command in the format of
`python main.py [args]`

This project currently only supports positional arguments. The following are able to be used:

```
python main.py locations [location1] [location2] [...]
Print out the stats of each location as input, writing out their sublocations too if applicable. If no locations are specified, prints out locations from `config.py`

Example:
python main.py locations Beach Town

Season: fall     | Weather: sunny         | Time: 10:00PM
Depth: 5         | Bait: none             | Bait Target: none
Fishing Level: 8 | Perfect catches: 17.0% | Rod used: iridium

Beach                    Total Catchables: 7      Avg Coin: 106.29         Avg XP: 6.7
--------------------     --------------------     --------------------     --------------------
Anchovy                  Proportion: 21.55%       Value: 47.0 coins        XP: 8.0
Seaweed                  Proportion: 24.81%       Value: 32.0 coins        XP: 5.0
Super Cucumber           Proportion: 12.76%       Value: 388.0 coins       XP: 8.0
Albacore                 Proportion: 24.81%       Value: 117.0 coins       XP: 9.0
Sea Jelly                Proportion:  4.61%       Value: 200.0 coins       XP: 3.0
Secret Note              Proportion:  0.92%       Value: 1.0 coins         XP: 3.0
Joja Cola, Trash, ..     Proportion: 10.54%       Value: 4.17 coins        XP: 3.0

Town                     Total Catchables: 6      Avg Coin: 60.04          Avg XP: 6.73
--------------------     --------------------     --------------------     --------------------
Smallmouth Bass          Proportion: 32.77%       Value: 79.0 coins        XP: 8.0
Bream                    Proportion: 32.77%       Value: 71.0 coins        XP: 8.0
Green Algae              Proportion: 22.79%       Value: 23.0 coins        XP: 5.0
River Jelly              Proportion:  4.28%       Value: 125.0 coins       XP: 3.0
Secret Note              Proportion:  0.59%       Value: 1.0 coins         XP: 3.0
Joja Cola, Trash, ..     Proportion:   6.8%       Value: 4.17 coins        XP: 3.0

Town (Fountain)          Total Catchables: 4      Avg Coin: 1.8            Avg XP: 3.0
--------------------     --------------------     --------------------     --------------------
Decorative Trash Can     Proportion:  10.0%       Value: 0.0 coins         XP: 3.0
Wood, Stone              Proportion:  90.0%       Value: 2.0 coins         XP: 3.0
Secret Note              Proportion:   0.0%       Value: 1.0 coins         XP: 3.0
Joja Cola, Trash, ..     Proportion:   0.0%       Value: 4.17 coins        XP: 3.0
```

```
python main.py fish [fish or id]
Print out the stats of a particular fish, searching by either its name or item ID. If multiple results are found, you must choose one by selecting the associated number.

Example:
python main.py fish Carp
Mutliple matches of carp found. Please select appropriate target manually:
(0): Carp
(1): Scorpion Carp
(2): Carp Surprise
(3): Mutant Carp
(4): Midnight Carp
(5): Radioactive Carp
4
Game and Player context:
Season: fall         Weather: sunny             Time: 10:00PM
Depth: 5             Bait: none                 Bait Target: none
Fishing Level: 8     Perfect catches: 17.0%     Rod used: iridium

Fish context:
Name: Midnight Carp     Object ID: 269         Avg. XP: 9              Avg. Coins: 235         Scaled % Perfect: 14.54%

Absolute min. size      Absolute max. size     Practical min. size     Practical max. size

12                      52                     10.8                    68.64

                        Normal                 Silver                  Gold                    Iridium

Quality:                0%                     0.0%                    85.47%                  14.54%

Value:                  150                    187                     225                     300
```

## Contributing

All feature requests, issue reports, and PRs are welcome, so long as they are in good faith. What constitutes good faith is subjective, but it is assumed by default that all contributors are acting in good faith.
You do not need to do anything special to contribute! Just fork this repository, clone it onto your device, create a branch off your fork, and get to work. If you do not know how to do this, there are plenty of great guides online which teach you how -- any should work.

## Using this project

This project is open-source and free to use, but please consider that it is licensed under the AGPL-3.0 License. The intention of using this particular license is to ensure that due credit is given by any derivative works, and that such works must also be open source under the same terms.

Note that the above statement does not reflect the actual terms of the AGPL-3.0 License agreement, and rather states the intention of why this project uses that particular license.
