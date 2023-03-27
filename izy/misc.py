"""Miscellaneous utility functions and classes
"""

import sys
import logging
import operator
import functools

__all__ = ['Singleton', 
           'flatten', 'without_dups', 'unique', 'first',
           'setup_logger']


class Singleton(type):
    """Singleton metaclass.

    copy-pasted from https://stackoverflow.com/q/6760685/7798781

    >>> class MyClass(metaclass=Singleton):
    ...    pass
    
    >>> x = MyClass()
    >>> x is MyClass()
    True
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def flatten(iterable2d):
    """Convert a 2D nested iterable into a flat `list`.

    The approach is claimed to be one of the most efficient options. (https://stackoverflow.com/a/45323085)

    Args:
        iterable2d (iterable): The 2D iterable

    Returns:
        list: The flat list
    """
    return functools.reduce(operator.iconcat, iterable2d, [])


def without_dups(sequence):
    """Returns a copy of the given sequence without duplicate values while preserving order.
    """
    sequence.__class__(dict.fromkeys(sequence))


unique = without_dups


def first(iterable, default=None, condition=None):
    """
    Returns the first item in the `iterable` that satisfies the `condition`.
    If the condition is not given, returns the first item of the iterable.

    If the iterable is empty or no item matches the `condition`,
    the `default` argument is returned.

    simplified version of https://stackoverflow.com/a/35513376/7798781

    Args:
        iterable (iterable): The input iterable :)
        default (_type_, optional): If the iterable is empty or no item matches
            the `condition`, this value is returned. Defaults to None.
        condition (callable, optional): The condition function. Defaults to None.

    Raises:
        ValueError: If the `default` value does not satidfy the provided `condition`

    Returns:
        The first item in the `iterable` that satisfies the `condition` or the
        `default` value.
    """
    try:
        return next(x for x in iterable if condition is None or condition(x))
    except StopIteration:
        if condition is None or condition(default):
            return default
    raise ValueError('The `default` value does not satidfy the provided `condition`')


def setup_logger(base=None, name=None, log_file=None, mode='w'):
    """Initiates a simple logger with a general log format and an optional file handler.

    Args:
        base (logging.Logger, optional): Base logger. Defaults to None.
        name (str, optional): Name of the new logger, 
            if base logger is not provided. Defaults to None.
        log_file (str, optional): Path to the log file. Defaults to None.
        mode (str, optional): Log file mode. Defaults to 'w'.

    Returns:
        logging.Logger: The logger object
    """
    formatter = logging.Formatter(fmt='[{asctime}][{name}][{levelname}] - {message}',
                                  datefmt='%Y-%m-%d %H:%M:%S', style='{')
    logger = base or logging.getLogger(name)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode=mode)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    if base is None:
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger.addHandler(screen_handler)
    return logger


if __name__ == '__main__':

    import doctest
    doctest.testmod()
