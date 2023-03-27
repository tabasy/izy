"""Decorator function zoo.
"""

import logging
import warnings
import functools
from typing import Mapping
from collections import namedtuple
from datetime import datetime

from .misc import setup_logger


__all__ = ['returns', 'yields', 'fix_this',
           'ignores', 'fallsback', 'returns_time', 'logs']


def returns(*field_names, type_name=None, **name2description):
    def decorator(f):
        output_type_name = type_name or f.__name__ + '_output'
        output_field_names = field_names + tuple(name2description.keys())
        FuncOutput = namedtuple(output_type_name, output_field_names)

        doc = f.__doc__ + '\n' if f.__doc__ else ''
        doc += 'Returns:\n'
        for name in field_names:
            doc += f'\t{name}\n'
        for name in name2description:
            doc += f'\t{name}: {name2description[name]}\n'
        f.__doc__ = doc

        @functools.wraps(f)
        def wrapper(*args, **kw):
            output = f(*args, **kw)
            if isinstance(output, Mapping) and set(output.keys()) == set(field_names):
                return FuncOutput(**output)
            elif isinstance(output, tuple):
                return FuncOutput(*output)
            else:
                return FuncOutput(output)

        return wrapper
    return decorator


def yields(*field_names, type_name=None, **name2description):

    def decorator(f):
        output_type_name = type_name or f.__name__ + '_output'
        output_field_names = field_names + tuple(name2description.keys())
        FuncOutput = namedtuple(output_type_name, output_field_names)

        doc = f.__doc__ + '\n' if f.__doc__ else ''
        doc += 'Yields:\n'
        for name in field_names:
            doc += f'\t{name}\n'
        for name in name2description:
            doc += f'\t{name}: {name2description[name]}\n'
        f.__doc__ = doc

        @functools.wraps(f)
        def wrapper(*args, **kw):
            for item in f(*args, **kw):
                if isinstance(item, Mapping):
                    yield FuncOutput(**item)
                elif isinstance(item, tuple):
                    yield FuncOutput(*item)
                else:
                    yield FuncOutput(item)

        return wrapper
    return decorator


def repr_signature(*args, **kwargs):
    args_repr = [repr(a) for a in args]
    kwargs_repr = [f'{k}={v!r}' for k, v in kwargs.items()]
    return ', '.join(args_repr + kwargs_repr)


def repr_call(func, *args, **kwargs):
    return f'{func.__name__}({repr_signature(*args, **kwargs)})'


# inspired by https://ankitbko.github.io/blog/2021/04/logging-in-python/
def logs(logger=None, to_file=None, file_mode='a',
         before=logging.DEBUG, after=logging.DEBUG, exception=logging.ERROR):
    def decorator(f):
        logger_name = logger if isinstance(logger, str) else f.__name__
        mylogger = setup_logger(
            base=logger, name=logger_name, log_file=to_file, mode=file_mode)

        @functools.wraps(f)
        def wrapper(*args, **kw):
            t_before = datetime.now()
            if before:

                signature = repr_signature(*args, **kw)
                mylogger.log(
                    before, f"Function `{f.__name__}` called with args: ({signature})")
            try:
                result = f(*args, **kw)
                t_after = datetime.now()
                if after:
                    mylogger.log(
                        after, f"Function `{f.__name__}` returned after {str(t_after-t_before)} with output: {result}")
                return result
            except Exception as e:
                t_exception = datetime.now()
                if exception:
                    mylogger.log(
                        exception, f"{e!r} raised in `{f.__name__}` after {str(t_exception-t_before)}!\n{str(e)}".strip())
                raise e
        return wrapper
    return decorator


def returns_time(milis=False, seconds=False):    # defaults to timedelta format

    def decorator(f):
        FuncOutput = namedtuple(f.__name__ + '_output', ('output', 'time'))

        @functools.wraps(f)
        def wrapper(*args, **kw):
            t_before = datetime.now()
            result = f(*args, **kw)
            t_delta = datetime.now() - t_before
            if seconds:
                t_delta = t_delta.total_seconds()
            elif milis:
                t_delta = int(t_delta.total_seconds() * 1000)

            return FuncOutput(result, t_delta)

        return wrapper
    return decorator


def fix_this(msg=None, warn_each_call=True):
    def decorator(f):
        message = f'You need to fix `{f.__name__}`! '
        if msg:
            message += msg
        warnings.warn(message=message)

        @functools.wraps(f)
        def wrapper(*args, **kw):
            if warn_each_call:
                warnings.warn(message=message)
            return f(*args, **kw)

        return wrapper
    return decorator


def ignores(*exceptions):
    def decorator(f):

        @functools.wraps(f)
        def wrapper(*args, **kw):
            try:
                return f(*args, **kw)
            except Exception as e:
                for ignored_ex in exceptions:
                    if isinstance(e, ignored_ex):
                        break
                else:
                    raise e

        return wrapper
    return decorator


def fallsback(exception, fallback):
    def decorator(f):

        @functools.wraps(f)
        def wrapper(*args, **kw):
            try:
                return f(*args, **kw)
            except exception as e:
                if callable(fallback):
                    return fallback(*args, **kw)
                else:
                    return fallback

        return wrapper
    return decorator


if __name__ == '__main__':

    @returns('x', 'y')
    def myfunction(x):
        return x, x+1

    @yields('a', 'b')
    def mygenerator(x):
        for i in range(x):
            yield i, i*2

    @fix_this('It always prints ValueError, errors should be raised!')
    def please(x):
        print('ValueError')
