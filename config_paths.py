"""
Config file for setting up and asserting that necessary paths for the project exist.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import os
from utils import Path, read_file_json, ensure_file_exists

"""
Constants for Directory Paths. These should follow the convention of
DIRECTORY_{dirname} with longer paths either providing _{subdir}_{subdir}... or just saying where it goes to
"""
DIRECTORY_PROJECT = Path(os.path.dirname(__file__))
DIRECTORY_DATA    = DIRECTORY_PROJECT + Path("data")

# Private JSON needs to be setup here specifically as it has data which pertains to paths configuration
_private_json:dict = read_file_json(DIRECTORY_DATA + Path("private_config.json"))
USER               = _private_json["User"]
PATH_DECOMPILE     = _private_json["Path_Decompile"]

DIRECTORY_USER                  = Path(f"C:/Users/{USER}")
DIRECTORY_STARDEW_VALLEY        = Path("C:/Program Files (x86)/Steam/steamapps/common/Stardew Valley")
DIRECTORY_CONTENT_UNPACKED_DATA = DIRECTORY_STARDEW_VALLEY + Path("Content (unpacked)/Data")
DIRECTORY_DECOMPILE             = Path(PATH_DECOMPILE)

"""
Constants for File Paths. These should follow a similar format, but also explain the data type.
E.G. FILE_JSON_TESTDATA
     FILE_PYOBJECTS_FISH
"""
FILE_DECOMPILE_ASSEMBLYINFO = DIRECTORY_DECOMPILE + Path("Properties/AssemblyInfo.cs")

FILE_JSON_OBJECTS   = DIRECTORY_CONTENT_UNPACKED_DATA + Path("Objects.json")
FILE_JSON_FISH      = DIRECTORY_CONTENT_UNPACKED_DATA + Path("Fish.json")
FILE_JSON_LOCATIONS = DIRECTORY_CONTENT_UNPACKED_DATA + Path("Locations.json")
FILE_JSON_FURNITURE = DIRECTORY_CONTENT_UNPACKED_DATA + Path("Furniture.json")

FILE_PYOBJECTS_BASEOBJECT   = DIRECTORY_DATA + Path("object_data.dat")
FILE_PYOBJECTS_FISH         = DIRECTORY_DATA + Path("fish_data.dat")
FILE_PYOBJECTS_GAMELOCATION = DIRECTORY_DATA + Path("location_data.dat")
FILE_PYOBJECTS_FURNITURE    = DIRECTORY_DATA + Path("furniture_data.dat")

# Assert all paths exist

# quick helper
def ensure(file_or_dir:str|Path):
    if not ensure_file_exists(file_or_dir):
        raise FileNotFoundError(f"Did not find required file/dir {file_or_dir}. Please check the configuration in {DIRECTORY_PROJECT}/config_paths.py")

ensure(DIRECTORY_PROJECT)
ensure(DIRECTORY_DATA)
ensure(DIRECTORY_USER)
ensure(DIRECTORY_STARDEW_VALLEY)
ensure(DIRECTORY_CONTENT_UNPACKED_DATA)
ensure(DIRECTORY_DECOMPILE)

ensure(FILE_DECOMPILE_ASSEMBLYINFO)
ensure(FILE_JSON_OBJECTS)
ensure(FILE_JSON_FISH)
ensure(FILE_JSON_FURNITURE)
ensure(FILE_PYOBJECTS_BASEOBJECT)
ensure(FILE_PYOBJECTS_FISH)
ensure(FILE_PYOBJECTS_GAMELOCATION)
ensure(FILE_PYOBJECTS_FURNITURE)
