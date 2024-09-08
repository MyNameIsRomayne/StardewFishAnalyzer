"""
Config file for setting up some variables which will be commonly used.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import os
from util import Path, read_file_json, ensure_file_exists

# If false, every object will load what is subjectively irrelevant for this code. 
# This is stuff like ignoring sale in random shops, sprite ID, etc.
# This reduces file size / ever so slightly increases load speed
IGNORE_IRRELEVANT_JSON = True

QUALITY_NORMAL = 0
QUALITY_SILVER = 1
QUALITY_GOLD = 2
QUALITY_IRIDIUM = 4

PRICE_SCALE_NORMAL = 1
PRICE_SCALE_SILVER = 1.25
PRICE_SCALE_GOLD = 1.5
PRICE_SCALE_IRIDIUM = 2

SKILL_NONE = 1
SKILL_FISHER = 1.25
SKILL_ANGLER = 1.5

current_dir = Path(os.getcwd())
data_dir = current_dir + Path("data")
private_config_data = read_file_json(data_dir + Path("private_config.json"))

user_path = Path(f"C:/Users/{private_config_data['User']}")

# Setup dirs
base_dir = Path("C:/Program Files (x86)/Steam/steamapps/common/Stardew Valley")
unpacked_data = base_dir + Path("Content (unpacked)/Data")

decompiled_content = Path(private_config_data["Path_Decompile"])
decompile_properties_file = decompiled_content + Path("Properties/AssemblyInfo.cs")

assert ensure_file_exists(user_path) == True
assert ensure_file_exists(base_dir) == True
assert ensure_file_exists(unpacked_data) == True
assert ensure_file_exists(decompile_properties_file) == True

objects_file   = unpacked_data + Path("Objects.json")
fish_file      = unpacked_data + Path("Fish.json")
locations_file = unpacked_data + Path("Locations.json")
furniture_file = unpacked_data + Path("Furniture.json")

objects_file_py   = data_dir + Path("object_data.dat")
fish_file_py      = data_dir + Path("fish_data.dat")
locations_file_py = data_dir + Path("location_data.dat")
furniture_file_py = data_dir + Path("furniture_data.dat")

# Setup object data
fish_json      = read_file_json(fish_file)
objects_json   = read_file_json(objects_file)
furniture_json = read_file_json(furniture_file)
locations_json = read_file_json(locations_file)

item_type_jsons = {
    "(O)": objects_json,
    "(F)": furniture_json,
}

# Locations of which to check for fish data readouts.
whitelist_fish_locations = ["Default", "Town"]
