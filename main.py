"""
Main file for reading and handling command line arguments.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import sys

from stardewfish.location_query import get_location_stats
from stardewfish.fish_query     import handle_fish_query
from stardewfish.config_query   import handle_config_query

def fail_query(message="Invalid Syntax."):
    print(message)
    quit()

def main():
    args = sys.argv

    query_type = args[1]
    allowed_queries = ["locations", "fish", "context"]
    if query_type not in allowed_queries:
        fail_query()
    
    if query_type == "locations":
        # Everything afterwards is taken is args
        locations = [name.lower().title() for name in args[2:]]
        get_location_stats(locations)
        quit()
    
    elif query_type == "fish":
        fish_name = args[2]
        handle_fish_query(fish_name)
        quit()

    elif query_type == "context":
        handle_config_query(args[2:])
        quit()

if __name__ == "__main__":
    main()
