"""
Main file for reading and handling command line arguments.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import sys, os

def fail_query(message="Invalid Syntax."):
    print(message)
    quit()

def main():
    args = sys.argv

    query_type = args[1]
    allowed_queries = ["location", "fish"]
    if query_type not in allowed_queries:
        fail_query()
    
    if query_type == "location":
        from utils.location_query import main
        main()
        quit()

if __name__ == "__main__":
    main()
