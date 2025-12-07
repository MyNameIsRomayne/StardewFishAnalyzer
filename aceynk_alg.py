from functools import lru_cache, reduce
from math import factorial, ceil, floor
from typing import TypeVar, overload, TypeAlias
from collections.abc import Callable, Iterable
from enum import Enum

SupportsSumT = TypeVar('SupportsSumT')
SupportsMultT = TypeVar('SupportsMultT')
SupportsRightSubT = TypeVar('SupportsRightSubT')
T = TypeVar('T')
IterableT: TypeAlias = Iterable[T]


class BasicFunctions(Enum):
    """Enum for basic functions."""
    IDENTITY = 1
    SQUARE = 2
    CUBE = 3

@overload
def sigma(upper: int, lower: int, f: Callable[[int], SupportsSumT]) -> SupportsSumT:
    """Mathematical summation operator.

    Args:
        upper (int): The upper bound of the summation.
        lower (int): The lower bound of the summation.
        f (Callable[[int], SupportsSumT]): The function to apply to each element of the summation.

    Returns:
        SupportsSumT: The completed sum.
    """
    ...
@overload
def sigma(this_set: Iterable[int], condition: Callable[[int], bool], f: Callable[[int], SupportsSumT]) -> SupportsSumT:
    """Mathematical summation operator.

    Args:
        this_set (Iterable[int]): Set to iterate through.
        condition (Callable[[int], bool]): Condition to filter the set.
        f (Callable[[int], SupportsSumT]): The function to apply to each element of the summation.

    Returns:
        SupportsSumT: The completed sum.
    """
    ...
@overload
def sigma(upper: int, lower: int, f: BasicFunctions) -> float:
    """Mathematical summation operator.

    Args:
        upper (int): The upper bound of the summation.
        lower (int): The lower bound of the summation.
        f (BasicFunctions): The basic function to apply to each element of the summation.

    Returns:
        float: The completed sum.
    """
    ...


def prod(arr: Iterable[T]) -> T:
    """Calculates the product of an iterable of numbers.

    Args:
        arr (Iterable[int]): Iterable of numbers to multiply.

    Returns:
        float: The product of the numbers.
    """
    return reduce(lambda x, y: x * y, arr, 1)


def linear_invert(arr: IterableT[T]) -> IterableT[T]:
    """Applies an inversion to an iterable of some numeric type.
    This inversion is defined as ``(1 - x)`` for ``x`` an element.

    Args:
        arr (Iterable[int]): Iterable of numbers to invert.

    Returns:
        Iterable[float]: Iterable of inverted integers.
    """
    
    return arr.__class__(1 - x for x in arr)


def sigma(*args):
    if (
        args[0].__class__ is int and
        args[1].__class__ is int and
        args[2].__class__ is BasicFunctions
    ):
        upper, lower, f = args[:3]
        
        match f:
            case BasicFunctions.IDENTITY:
                return (upper * (upper + 1) - lower * (lower - 1)) / 2
            case BasicFunctions.SQUARE:
                return (upper * (upper + 1) * (2 * upper + 1) - lower * (lower - 1) * (2 * lower - 1)) / 6
            case BasicFunctions.CUBE:
                return (upper ** 2 * (upper + 1) ** 2 - lower ** 2 * (lower - 1) ** 2) / 4

    elif (
        args[0].__class__ is int and
        args[1].__class__ is int and
        callable(args[2])
    ):
        upper, lower, f = args[:3]
        return sum(f(x) for x in range(lower, upper + 1))
    
    elif (
        args[0].__class__ is Iterable and
        callable(args[1]) and
        callable(args[2])
    ):
        this_set, condition, f = args[:3]
        return sum(f(x) for x in this_set if condition(x))
    
    raise ValueError(f"Error when processing sigma overload. {args} does not match any existing overload.")


fac = lru_cache(maxsize = 512)(factorial)
prod = lru_cache(maxsize = 512)(prod)


@lru_cache(maxsize = 512)
def inPr(n: int, k: int) -> int:
    if k > n: return 0
    return fac(k) * fac(n - k) / fac(n)


@lru_cache(maxsize = 512)
def _elem_symm_poly(arr: tuple[float], deg: int) -> float:
    if deg == len(arr): return prod(arr)
    if deg == 0: return 1
    if deg == 1: return sum(arr)
    if deg > len(arr): return 0

    return sum(arr[i] * _elem_symm_poly(arr[i + 1:], deg - 1) for i in range(len(arr)))


def _permutation_sum_solve(arr: list[float], i: int) -> float:
    arr_without_i = tuple(arr[:i] + arr[i + 1:])
    n = len(arr)
    this = arr[i]
    inv_arrwi = linear_invert(arr_without_i)

    sumfunc = lambda j : inPr(n, j + 1) / (j + 1) * (_elem_symm_poly(inv_arrwi,j) + _elem_symm_poly(inv_arrwi, n - j - 1))

    init_sum = this * sigma(floor(.5 * n) - 1, 0, sumfunc)

    if n % 2 == 1:
        return init_sum + this * inPr(n, floor(n/2) + 1) / (ceil(n/2)) * _elem_symm_poly(inv_arrwi, floor(.5 * n))
    
    return init_sum

def increment(arr: IterableT[T]) -> IterableT[T]:
    """Increments each element of an iterable of numbers by 1.

    Args:
        arr (Iterable[int]): Iterable of numbers to increment.

    Returns:
        Iterable[float]: Iterable of incremented integers.
    """
    return arr.__class__(x + 1 for x in arr)

def _random_shuffle_solve(
        arr: list[float], 
        i: int, 
        inv: list[float],
        init_sum: float,
        coeff_lookup: dict[frozenset[int], float]
    ) -> float:
    n = len(arr)
    this = arr[i]
    inv_arrwi = tuple(inv[:i] + inv[i + 1:])

    init_sum = init_sum / (2 - this)

    def sigma_func(j: int) -> float:
        if coeff_lookup[frozenset({j, n - j - 1})] == 0: return 0

        return coeff_lookup[frozenset({j, n - j - 1})] * _elem_symm_poly(inv_arrwi, j)

    return this * (init_sum + sigma(n - 1, 0, sigma_func))

def random_shuffle_prob(arr: tuple[float]) -> list[float]:
    """
    Given a list of floats between 0 and 1,\n
    Iterated through with a random value until the value is less than the current value,\n
    Return the probability of each item in the list.

    Args:
        arr (list[float]): The input array of floats between 0 and 1.

    Returns:
        list[float]: The probability of each item in the list.
    """

    n = len(arr)
    inv_arrwi = linear_invert(arr)
    base = fac(floor((n - 1) / 2)) * fac(ceil((n - 1) / 2))
    init_sum = base * prod(increment(tuple(inv_arrwi)))
    coeff_lookup = {frozenset({x, n - x - 1}): fac(x) * fac(n - x - 1) - base for x in range(ceil(n / 2))}

    return [_random_shuffle_solve(arr, i, inv_arrwi, init_sum, coeff_lookup) / fac(len(arr)) for i in range(len(arr))]

def permutation_sum(arr: list[float]) -> list[float]:
    """
    Given a list of floats between 0 and 1,\n
    Iterated through with a random value until the value is less than the current value,\n
    Return the probability of each item in the list.

    Args:
        arr (list[float]): The input array of floats between 0 and 1.

    Returns:
        list[float]: The probability of each item in the list.
    """

    return [_permutation_sum_solve(arr, i) for i in range(len(arr))]

if __name__ == "__main__":
    print(permutation_sum([0, 1, 0.25, 0.5]))
    print(random_shuffle_prob([0, 1, 0.25, 0.5]))
