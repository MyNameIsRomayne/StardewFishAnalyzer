"""
File which holds handle_config_query, for getting/setting public config data.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import json

import config
import config_paths
import stardewfish.utils as utils

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
        if args_key not in config._default_config.keys():
            print(f"Key {args_key} not recognized.")
        config._public_config[args_key] = args_val
        utils.write_file_contents(config_paths.FILE_JSON_PUBLIC_CONFIG, json.dumps(config._public_config))
        return
    
    elif args[0] == "get":
        args_key = args[1].lower()
        if args_key not in config._default_config.keys():
            print(f"Key {args_key} not recognized.")
        print(f"{args_key} = {config._default_config[args_key]}")
        return
