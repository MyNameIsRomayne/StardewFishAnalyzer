"""
Previous testing file which now just contains some unused helper functions, but more importantly, get_probs.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import itertools
from math import factorial
import numpy as np
import multiprocessing

def process_permutation(prob_list, prob_list_inverted, permutations):
    sum_probs = [0]*len(prob_list)

    for permutation in permutations:
        for iter, i in enumerate(permutation):
            if iter == 0:
                sum_probs[i] += prob_list[i]
                continue
            values_before_element = permutation[0:iter]
            inverted_before_element = [prob_list_inverted[e] for e in values_before_element]
            current_prob = prob_list[i] * np.prod(inverted_before_element)
            sum_probs[i] += current_prob

    total_permutations = factorial(len(prob_list))
    final_sums = [i/total_permutations for i in sum_probs]
    return final_sums

def ranges(N, nb):
    step = N / nb
    return [range(round(step*i), round(step*(i+1))) for i in range(nb)]

def get_probs(prob_list:np.ndarray):
    """
    WARNING: Highly unoptimized, will take extremely long for len>10.
    That being said, this gets the average chance elements in prob_list at any position n
    will succeed, given that prob_list is shuffled randomly.
    """

    if len(prob_list) >= 9:
        print(f"WARN: Prob list of length {len(prob_list)} entered into get_probs, this will take a while!")
    elif len(prob_list) > 10:
        raise TimeoutError("I refuse to let you take what will be approximately 5 minutes for this.")

    # Helper var to reduce the amount of times prob_list needs to be inverted
    prob_list_inverted = 1 - prob_list
    
    if len(prob_list) < 7:
        # Below 5, its reasonable to just use the current process rather than deal with multiprocessing overhead
        return process_permutation(prob_list, prob_list_inverted, itertools.permutations(range(len(prob_list))))

    # Setup variables before sending off the worker processes
    # Final collection list for the results
    sum_probs = [0]*len(prob_list)
    total_permutations = factorial(len(prob_list))
    # Amount of processes should exceed total cores here
    use_cores = 12
    # Setup the ranges of permutations for our results to use
    all_ranges = ranges(total_permutations, use_cores)
    pending_results:list = []
    pool = multiprocessing.Pool(processes=use_cores)
    # Permutations need to be generated iteratively first, unfortunately, so do that
    permutation_iterator = itertools.permutations(range(len(prob_list)))
    for subrange in all_ranges:
        split_permutation = []
        for _ in subrange:
            split_permutation.append(permutation_iterator.__next__())
        async_result = pool.apply_async(process_permutation, (prob_list, prob_list_inverted, split_permutation))
        pending_results.append( async_result )
    
    for result in pending_results:
        sum_probs = [a + b for a, b in zip(sum_probs, result.get())]

    return sum_probs

def get_probs_with_target(prob_list:np.ndarray, target:int, rerolls:int = 2):
    raise NotImplementedError

def get_subsets(nparray, sublen):
    """(Buggy, unused) get the subsets of some nparray by sublen."""
    limit = len(nparray) - sublen
    for i in range(len(nparray)):
        # Pull from start as well if we are otherwise going OOB
        if i > limit: 
            yield np.concatenate([nparray[i:i+sublen], nparray[0:i-limit]])
            continue
        yield nparray[i:i+sublen]

# Test for limits
if __name__ == "__main__":
    test = np.array(
        [1/8, 1/4, 1/2, 1/1]
    )
    print(test)
    print(get_probs(test))
    quit()

    import time
    for j in range(11):
        start = time.perf_counter()
        get_probs(np.array([0.25]*j))
        print(f"{j}: {time.perf_counter() - start}")
