"""
Testing file for testing brute force vs aceynk's algorithm, and for benchmarking any future algorithms
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

from aceynk_alg import permutation_sum, random_shuffle_prob
from stardewfish.probs_algorithm import get_probs
from stardewfish.utils import plural
from typing import Callable
from time import perf_counter
import random
import threading
import numpy as np

import multiprocessing
from multiprocessing import Value

import csv

# used to benchmark the base of the benchmark function
def do_nothing(*args):
    return

def can_complete_within(func:Callable, test_length:int, time_limit:float, use_numpy=False) -> bool:
    test_array = []
    # Generate array with rand values from 0-1
    # This should be negligible performance impact but may matter a bit. Worth testing base
    test_array = [random.random() for _ in range(test_length)]
    if use_numpy:
        test_array = np.array(test_array)
    # Start the function with timeout
    process_thread = threading.Thread(target=func, args=(test_array,), daemon=True)
    
    start = perf_counter()
    end = start + time_limit
    max_time = end - perf_counter() 

    process_thread.start()
    process_thread.join(max_time)

    # Check if time limit is exceeed, return if so
    if process_thread.is_alive():
        return False
    
    return True

def benchmark_alg_calls(func:Callable, test_length:int, test_duration_seconds:float = 60, use_numpy=False) -> int:
    """
    Benchmark a given probs algorithm for n seconds with length l.
    Returns: Amount of completions of the algorithm within the given test duration. May return 0 if took too long

    Note: due to how processes are run, only one benchmark should be run at a time to avoid having overtime threads eat resources for the next test.
    Threads which run overtime **are not stopped until the program exits**.
    """
    # We do random here to make sure python cache doesnt get handsy with maybe returning same output for inputs
    # We do max duration here rather than x seconds for n tests because O(n!) is a bastard

    start = perf_counter()
    end = start + test_duration_seconds
    completions = 0

    test_array = []

    while end > perf_counter():
        # Get the maximum amount of time we want this to run for. Just to make sure we dont run something forever despite max time
        max_time = end - perf_counter() 
        # Generate array with rand values from 0-1
        # This should be negligible performance impact but may matter a bit. Worth testing base
        test_array = [random.random() for _ in range(test_length)]
        if use_numpy:
            test_array = np.array(test_array)
        # Start the function with timeout
        process_thread = threading.Thread(target=func, args=(test_array,), daemon=True)
        process_thread.start()
        process_thread.join(max_time)
        # Check if time limit is exceeed, return if so
        if process_thread.is_alive():
            break
        completions += 1
    
    return completions

def wrap_benchmark_worker(*args, returnable):
    result = benchmark_alg_calls(*args)
    returnable.value = result

def worker_benchmark_alg_calls(func:Callable, test_len = 20, duration_max = 10, use_numpy=False):
    # Start a new process to benchmark with, and create var returnable to get the num of iters with
    args = (func, test_len, duration_max, use_numpy)
    returnable = Value('i', 0)
    temp_process = multiprocessing.Process(target=wrap_benchmark_worker, args=args, kwargs={"returnable" : returnable})
    temp_process.start()
    temp_process.join()
    return returnable.value

def test_nothing(test_len = 20, duration_max = 10, padding_printout_left = 20):
    result = worker_benchmark_alg_calls(do_nothing, test_len, duration_max=duration_max, use_numpy=True)
    print(f"Control (no function): {result} iteration{plural(result)}".ljust(padding_printout_left))
    return result

def test_brute(test_len = 20, duration_max = 10, padding_printout_left = 20):
    result = worker_benchmark_alg_calls(get_probs, test_len, duration_max=duration_max, use_numpy=True)
    print(f"get_probs (brute force): {result} iteration{plural(result)}".ljust(padding_printout_left))
    return result

def test_aceynk(test_len = 20, duration_max = 10, padding_printout_left = 20):
    result = worker_benchmark_alg_calls(permutation_sum, test_len, duration_max=duration_max, use_numpy=False)
    print(f"aceynk (awesome): {result} itertion{plural(result)}".ljust(padding_printout_left))
    return result

def test_bounds():
    # setup consts
    TEST_DURATION = 60
    TEST_MIN = 12
    TEST_MAX = 30
    PADDING_LEFT = 20
    # Setup csv writer
    outfile = open("results.csv", "a")
    csvwriter = csv.writer(outfile, lineterminator="\n")
    # Gather the data
    for test_len in range(TEST_MIN, TEST_MAX + 1):
        result_nothing = test_nothing(test_len, TEST_DURATION, PADDING_LEFT)
        result_brute   = 0#test_brute(test_len, TEST_DURATION, PADDING_LEFT)
        result_aceynk  = test_aceynk(test_len, TEST_DURATION, PADDING_LEFT)
        csvwriter.writerow([result_nothing, result_brute, result_aceynk])

def test_limitations():
    # setup consts
    MAX_ALLOWED_TIME = 60
    test_length = 1
    start = perf_counter()
    # Setup csv writer
    outfile = open("results_limits.csv", "w")
    csvwriter = csv.writer(outfile, lineterminator="\n")
    func_to_use:Callable = random_shuffle_prob #get_probs
    while can_complete_within(func_to_use, test_length, MAX_ALLOWED_TIME, use_numpy=False):
        elapsed = round(perf_counter()-start, 2)
        print(f"passed {test_length} in {elapsed}s")
        start = perf_counter()
        csvwriter.writerow([test_length, elapsed])
        test_length += 1
    print(f"failed {test_length}")

if __name__ == "__main__":
    test_limitations()
