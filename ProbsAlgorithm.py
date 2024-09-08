"""
Previous testing file which now just contains some unused helper functions, but more importantly, get_probs.
Copyright (C) 2024 Romayne (Contact @ https://github.com/MyNameIsRomayne)
"""

import itertools
from math import factorial
import numpy as np

def get_probs(prob_list:np.ndarray):
    """
    WARNING: Highly unoptimized, will take extremely long for len>10.
    That being said, this gets the average chance elements in prob_list at any position n
    will succeed, given that prob_list is shuffled randomly.
    """
    sum_probs = [0]*len(prob_list)
    prob_list_inverted = 1 - prob_list

    for permutation in itertools.permutations(range(len(prob_list))):
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

def get_subsets(nparray, sublen):
    """(Buggy, unused) get the subsets of some nparray by sublen."""
    limit = len(nparray) - sublen
    for i in range(len(nparray)):
        # Pull from start as well if we are otherwise going OOB
        if i > limit: 
            yield np.concatenate([nparray[i:i+sublen], nparray[0:i-limit]])
            continue
        yield nparray[i:i+sublen]
