"""
Stuff from my local utilities file required to be kept for the project to work.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import os
from math import floor
from os.path import exists
import json

import pathlib

class Path(pathlib.Path):
    """A brief extension of the Path class from pathlib to allow for addition operations."""
    def __add__(self, otherPath:str|pathlib.Path) -> "Path":
        return Path(f"{self}/{otherPath}")

# Returns whether the given file exists. If create is True, creates the file
# Returns True if the file already existed, False otherwise.
def ensure_file_exists(file_path:str, create = False) -> bool:
    """
    Ensure a certain file exists, and create it if it doesn't and `create` is True.
    file_path: Some string-compatible path.
    create: Whether to create the file if it does not yet exist. Default False
    Note: Will not create intermediary directories.
    Returns whether the file existed BEFORE this function potentially created it.
    """
    if exists(file_path):
        return True
    else:
        if create:
            with open(file_path, "x"):
                pass
        return False

def read_file_contents(file_path:str,
                       lines = False,
                       encoding = "utf-8",
                       read_mode = "r") -> list[str|bytes]|str|bytes|None:
    """
    Read the contents of some file, and return them as str/bytes depending on read_mode
    file_path: Some string-convertible path to the file.
    lines: whether or not to output the lines of the file as a list instead of a newline-delimited string. Default False
    encoding: the encoding to use for the file. Default "utf-8"
    read_mode: the mode to write with. Supports args same as open()'s mode arg does. Default "r"
    Returns None if the file does not exist, a list of strings/bytes if lines is True, otherwise a string or bytes object representing
    the file contents.
    """
    if not ensure_file_exists(file_path):
        return None
    if "b" in read_mode:
        encoding = None # Binary files do not take encoding arguments
    file = open(file = file_path, mode = read_mode, encoding = encoding)
    if lines:
        return file.readlines()
    else:
        return file.read()

def read_file_json(file_path:str|Path) -> dict:
    """
    Read the contents of a file, and have them returned as JSON.
    Returns a dict if successful, if any JSON errors occur, returns an empty dict.
    file_path: Some string-convertible path to the file.
    """
    if not ensure_file_exists(file_path):
        return {}
    try:
        return json.loads(open(str(file_path), "r").read())
    except TypeError:
        return {}

def write_file_contents(file_path:str|Path,
                        contents:str,
                        write_mode = "w") -> None:
    """
    Write out some string to the file path given. This will create the file if it does not yet exist.
    file_path: Some string-convertible path to the file.
    contents: the contents to write.
    write_mode: the mode to write with. Supports args same as open()'s mode arg does.
    """
    file_path = str(file_path)
    ensure_file_exists(file_path, create = True)
    if (not "w" in write_mode) and (not "a" in write_mode):
        print(f"WARN: No valid 'w' or 'a' mode passed to write_mode {write_mode}. File writing will probably fail!")
    with open(file = file_path, mode = write_mode) as file:
        file.write(contents)

def plural(n:int|float) -> str:
    """
    Small function to get whether something should be plural.
    Returns 's' if n is not 1, otherwise returns an empty string.
    """
    return "s" if n != 1 else ''

def format_seconds_to_times(seconds:float|int) -> str:
    """
    Formats seconds to some sequence of years/hours/days.. depending on the input seconds.
    seconds: a float or int to use for the time.
    """
    # Largest to smallest denominator
    seconds_in_one_minute = 1 * 60
    seconds_in_one_hour = 60 * seconds_in_one_minute
    seconds_in_one_day = seconds_in_one_hour * 24
    seconds_in_one_week = seconds_in_one_day * 7
    seconds_in_one_year = seconds_in_one_day * 365.25 # Slightly innacurate, but i dont care
    seconds_in_one_month = seconds_in_one_day * (365.25/12) # Also slightly innacurate, and i still dont care

    years = floor(seconds/seconds_in_one_year)
    seconds -= years * seconds_in_one_year

    months = floor(seconds/seconds_in_one_month)
    seconds -= months * seconds_in_one_month

    weeks = floor(seconds/seconds_in_one_week)
    seconds -= weeks * seconds_in_one_week

    days = floor(seconds/seconds_in_one_day)
    seconds -= days * seconds_in_one_day

    hours = floor(seconds/seconds_in_one_hour)
    seconds -= hours * seconds_in_one_hour

    minutes = floor(seconds/seconds_in_one_minute)
    seconds -= minutes * seconds_in_one_minute

    # and then seconds is left as it ought to be
    seconds = floor(seconds)

    toformat = [[years, "year"], [months, "month"], [weeks, "week"], [days, "day"], [hours, "hour"], [minutes, "minute"], [seconds, "second"]]
    output_str = ""
    for num_unit, unit in toformat:
        if num_unit == 0:
            continue
        output_str += f"{num_unit} {unit}{plural(num_unit)}, "
    output_str = output_str.rstrip(", ")
    return output_str

def profile(func, *args, **kwargs) -> float:
    """
    Small wrapper function to get the time it takes to run a particular function.
    Not perfect, but gets the job done for most cases.
    func: A callable function to benchmark.
    *args: Any positional args for the function.
    **kwargs: Any keyword args for the function.
    Returns a float representing the time in seconds it took to run.
    """
    import time
    start = time.perf_counter()
    func(*args, **kwargs)
    return time.perf_counter() - start

def format2DListAsTable(l_2d:list[str], char_limit:int=900, column_delimiter="|") -> str:
    """Pass in a square 2D list, get out a large f-string representing a neat table"""
    if not len(l_2d): return ""
    amount_columns = len(l_2d[0]) # assume square
    length_columns = [0]*amount_columns
    # Get largest index out of each column
    for column in range(amount_columns):
        largest_index = 0
        for row in l_2d:
            largest_index = max(largest_index, len(row[column]))
        # Constrain to character limit
        largest_index = min(char_limit, largest_index)
        length_columns[column] = max(length_columns[column], largest_index)
    # Pad columns in each row according to the columns list that was built
    padded = []
    # Go through each row to change it to a padded string
    for row in l_2d:
        padded_row = []
        # Go through each column in the row to pad it
        for column in range(amount_columns):
            column_width = length_columns[column]
            unadjusted_cell = row[column]
            if len(row[column]) > char_limit:
                unadjusted_cell = unadjusted_cell[0:char_limit-2] + ".."
            padded_row.append(unadjusted_cell.ljust(column_width))
        padded.append(f" {column_delimiter} ".join(padded_row))
    return "\n".join(padded)

def classic_to_military(classical_time:str) -> int:
    """Turn times like 6:59 AM into 659, and 6:59 PM to 1859 (24 hr time)"""
    final_time = 0
    hours, minutes = classical_time.split(":")
    minutes, am_or_pm = minutes[0:2], minutes[2:].lower()
    hours, minutes = int(hours), int(minutes)
    # Add base time
    final_time += (hours * 100)
    final_time += (minutes * 1)
    # Factor in AM/PM
    if (am_or_pm == "pm"):
        final_time += 1200
    return final_time

def military_to_classic(internal_time:int) -> str:
    """Turn times like 659 into 6:59AM, and 1859 to 6:59PM"""
    hours = int(internal_time/100)
    minutes = int(internal_time%100)
    am_or_pm = ("AM") if (internal_time < 1200) else ("PM")
    hours = (hours - 12) if (internal_time > 1200) else (hours)
    return f"{hours}:{minutes}{am_or_pm}"

def get_dir_total_file_lines() -> int:
    """Get the total amount of lines in the current directory. IDK, its just cool."""
    current_dir_files = [file for file in os.listdir(os.getcwd()) if not os.path.isdir(file)]
    return sum([len(open(file).readlines()) for file in current_dir_files])

if __name__ == "__main__":
    print(get_dir_total_file_lines())
