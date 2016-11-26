__author__ = 'dmitrybelyakov'

""" Timers
This is a reusable module to benchmark python code that provides
several functions for timing execution and leverages both
built-in and homegrown tactics
"""
import time, sys


def simple_timer(func, *args):
    """
    A simple timer
    Runs provided function with arbitrary positional arguments 1000 times
    and returns timing.
    :param func: A function to run
    :param args: collected  positional arguments
    :return: float of milliseconds
    """
    start = time.clock()
    for i in range(1000):
        func(*args)
    end = time.clock()
    return end - start


# get best timer available for platform
def get_timer():
    """
    Get timer
    Depending on python version and platform returns most suitable
    and precise timer function, that is:
    On pythons > 3.3 uses the new available perf_counter otherwise
    uses time.time on unix or time.clock on windows.
    :return: int
    """
    is_new = sys.version_info[0] > 3 and sys.version_info[1] > 3
    is_win = sys.platform[3] == 'win'

    if is_new:
        return time.perf_counter
    elif is_win:
        return time.clock
    else:
        return time.time


def total(func, *args, **kwargs):
    """
    Total time to run a function.
    Returns a tuple of (total time, last result)

    :param func:            a function to run
    :param args:            positionals
    :param kwargs:          keyword arguments
    :return:                float
    """
    timer = get_timer()
    repetitions = kwargs.pop('reps', 1000)
    repetitions = list(range(repetitions))
    start = timer()
    result = None
    for i in repetitions:
        result = func(*args, **kwargs)
    end = timer()
    elapsed = end - start
    return elapsed


def best(func, *args, **kwargs):
    """
    Best time
    Returns quickest run among repetition runs. Returned result is
    a tuple of (best time, last result)
    :param func:            a function to run
    :param args:            positionals
    :param kwargs:          keyword arguments
    :return:                float
    """
    timer = get_timer()
    best_time = 2 ** 32
    repetitions = kwargs.pop('reps', 5)
    repetitions = list(range(repetitions))
    for i in repetitions:
        start=timer()
        result = func(*args, **kwargs)
        end = timer()
        elapsed = end - start

        if elapsed < best_time:
            best_time = elapsed

        return best_time


def best_of_total(func, *args, **kwargs):
    """
    Best of total
    Returns best run of repetitions1 repetitions of running total()
    a repetitions2 number of times.

    :param repetitions1:    a number of repetitions to run total()
    :param total:           a total function to run
    :param func:            a function to run
    :param args:            positionals
    :param kwargs:          keyword arguments
    :return:                float
    """
    repetitions1 = kwargs.pop('reps1', 5)
    return min(total(func, *args, **kwargs) for i in range(repetitions1))


def run_tests(tests, *args, reps1=4, reps=1000, **kwargs):
    """
    Run tests
    Runs a list of test functions and computes best of reps1 repetitions
    each taking reps iterations

    :param tests:       a list of tests to run
    :param args:        collected test args
    :param reps1:       best of this much tests
    :param reps:        each test will do this much iterations
    :param kwargs:      collected test kwargs
    :return:            None
    """
    results = dict()
    for test in tests:
        test_result = best_of_total(
            test, *args, reps1=reps1, reps=reps, **kwargs
        )
        results[test_result] = test.__name__

    for timed in sorted(results.keys()):
        print('{}: {}'.format(timed, results[timed]))



def timer(label = '', trace = True):
    """
    Timing decorator
    :param label:       a label to print to stdout
    :param trace:       do printing?
    :return:            mixed, original function result
    """
    def decorator(func):
        alltime = 0
        def execute_func(*args, **kwargs):
            nonlocal alltime
            start = time.clock()
            result = func(*args, **kwargs)
            end = time.clock()
            elapsed = end - start
            alltime += elapsed
            execute_func.alltime = alltime

            if trace:
                format = '%s %s: %.5f, %.5f'
                values = (label, func.__name__, elapsed, alltime)
                print(format % values)

            return result
        return execute_func
    return decorator