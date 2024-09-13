"""
File which holds handle_config_query, for getting/setting public config data.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import json

import config
import config_paths
import stardewfish.utils as utils

def try_convert_value(user_value:str) -> str|float|int|bool:
    try:
        return int(user_value)
    except ValueError:
        pass # it could be a flaot still
    try:
        return float(user_value)
    except ValueError:
        pass # it is definitely not a float or int, but could be bool
    if user_value.lower() == "false":
        return False
    elif user_value.lower() == "true":
        return True
    else:
        return user_value # ok its a string

def handle_config_query(args:list[str]):
    
    if args[0] == "help":
        # list out all the vars
        all_keys = config._default_config.keys()
        print("Usable keys:\n")
        for key in all_keys:
            print(key)
        return

    elif args[0] == "set":
        args_key, args_val = args[1].lower(), args[2]
        args_val = try_convert_value(args_val)
        if args_key not in config._default_config.keys():
            print(f"Key {args_key} not recognized.")
            return
        config._public_config[args_key] = args_val
        utils.write_file_contents(config_paths.FILE_JSON_PUBLIC_CONFIG, json.dumps(config._public_config))
        return
    
    elif args[0] == "get":
        args_key = args[1].lower()
        if args_key not in config._default_config.keys():
            print(f"Key {args_key} not recognized.")
            return
        print(f"{args_key} = {config._default_config[args_key]}")
        return
