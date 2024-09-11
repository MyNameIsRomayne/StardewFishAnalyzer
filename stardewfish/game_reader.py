"""
File for reading and storing the data turned XNB.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import config_paths
from stardewfish.utils import read_file_contents, read_file_json, ensure_file_exists
import pickle

def get_version() -> str:
    """
    Get the current version of the unpacked content.
    returns: A string representing the build number, e.g. "1.6.8.24119"
    """
    contents = read_file_contents(config_paths.FILE_DECOMPILE_ASSEMBLYINFO, lines=True)
    for line in contents:
        if "AssemblyFileVersion" in line:
            # Get the version, which is between some string quotes
            line = str(line)
            left_index = (line.find('"')+1)
            right_index = (line.rfind('"'))
            return line[left_index:right_index]

def save_objects(objects:dict[str], file_path:str) -> None:
    """
    Saves all XNBObjects of the dictionary passed in into the respective file, pickled as a list.
    objects: the dictionary of objects to save.
    """
    current_version = get_version()
    # Create file if it doesn't exist yet
    ensure_file_exists(file_path, create=True)
    with open(file_path, "wb") as file:
        as_list:list = [objects[key] for key in objects.keys()]
        # Append version data
        as_list.append(current_version)
        pickle.dump(as_list, file)

def load_objects(file_path:str) -> tuple[ dict[str]|None, str ]:
    """
    Loads all pickled XNBObjects from the appropriate file.
    Plucks the version stored at the end and returns that as well.
    Returns: A tuple containing the dictionary of objects, and a string of the version number.
    If the file is missing, returns None and an empty string.
    """
    version = ""
    object_list:list
    object_dict:dict[str] = {}
    # It dont exist
    if not ensure_file_exists(file_path, create=False):
        return None, version
    # It do exist
    with open(file_path, "rb") as file:
        object_list = pickle.load(file)
    # Get the version (always at last)
    version = object_list.pop()
    for item in object_list:
        object_dict[item.id] = item
    return object_dict, version

def get_objects(file_path:str, file_path_py:str, class_type:type) -> dict[str]:
    """
    Get all the objects into a dictionary keyed by their ID.
    If there is a .dat file storing these objects from the appropriate version,
    this function will take from there instead.
    Returns: A dictionary keyed by item IDs, corresponding to objects instantiated with class_type.
    """
    # Try to load from file first.
    # The performance hit from version mismatch is minor due to how infrequently it will change
    current_version = get_version()
    file_objects, version = load_objects(file_path_py)
    if version == current_version:
        return file_objects
    # It failed, read from JSON file
    as_json = read_file_json(file_path)
    new_objects:dict[str, class_type] = {}
    for object_key in as_json.keys():
        new_objects[object_key] = class_type(object_key, as_json[object_key])
    # Lastly, make sure we have that file for later
    save_objects(new_objects, file_path_py)
    return new_objects
