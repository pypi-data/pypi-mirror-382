"""
Timing utilities for measuring function execution time
"""
import time
import functools
from rich import print as rich_print

def timer(func):
    """
    Decorator that measures and prints the execution time of a function.
    
    Parameters:
    -----------
    func : callable
        The function to be timed
        
    Returns:
    --------
    callable
        A wrapped function that prints execution time
        
    Example:
    --------
    >>> @timer
    ... def slow_function():
    ...     time.sleep(1)
    ...
    >>> slow_function()
    slow_function took 1.001 seconds to execute
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        rich_print(f"{func.__name__} took {end_time - start_time:.3f} seconds to execute")
        return result
    return wrapper

__all__ = ['timer'] 