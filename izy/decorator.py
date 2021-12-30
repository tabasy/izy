import sys
import logging
import warnings
import functools
from typing import Mapping
from collections import namedtuple
from datetime import datetime


__all__ = ['returns', 'yields', 'fix_this', 'ignors', 'fallsback', 'timed', 'logs']


def returns(*field_names, type_name=None):
    def decorator(f):
        if type_name is None:
            # print(f.__name__, list(field_names))
            ReturnClass = namedtuple(f.__name__ + '_result', field_names)
        else:
            ReturnClass = namedtuple(type_name, field_names)

        # type_name = type_name or f.__name__

        @functools.wraps(f)
        def wrapper(*args, **kw):
            result = f(*args, **kw)
            if isinstance(result, Mapping):
                return ReturnClass(**result)
            elif isinstance(result, tuple):
                return ReturnClass(*result)
            else:
                return ReturnClass(result)
        
        return wrapper
    return decorator


def yields(*field_names, type_name=None):
    def decorator(f):
        if type_name is None:
            # print(f.__name__, list(field_names))
            ReturnClass = namedtuple(f.__name__ + '_result', field_names)
        else:
            ReturnClass = namedtuple(type_name, field_names)

        @functools.wraps(f)
        def wrapper(*args, **kw):
            for item in f(*args, **kw):
                if isinstance(item, Mapping):
                    yield ReturnClass(**item)
                elif isinstance(item, tuple):
                    yield ReturnClass(*item)
                else:
                    yield ReturnClass(item)
        
        return wrapper
    return decorator


def _setup_logger(name, log_file=None, mode='w'):
    formatter = logging.Formatter(fmt='[{asctime}][{name}][{levelname}] - {message}',
                                  datefmt='%Y-%m-%d %H:%M:%S', style='{')
    logger = logging.getLogger(name)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode=mode)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger.addHandler(screen_handler)
    return logger

# https://ankitbko.github.io/blog/2021/04/logging-in-python/
def logs(logger=None, to_file=None, file_mode='w',
         before=logging.DEBUG, after=logging.DEBUG, exception=logging.ERROR):
    def decorator(f):
        log_file = to_file 
        logger_name = f.__name__
        if isinstance(logger, str):
            if logger.lower().endswith('.txt'):
                log_file = logger
            else:
                logger_name = logger
        mylogger = logger or _setup_logger(logger_name, log_file, mode=file_mode)

        @functools.wraps(f)
        def wrapper(*args, **kw):
            t_before = datetime.now()
            if before:
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kw.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                mylogger.log(before, f"Function `{f.__name__}` called with args: ({signature})")
            try:
                result = f(*args, **kw)
                t_after = datetime.now()
                if after:
                    mylogger.log(after, f"Function `{f.__name__}` returned after {str(t_after-t_before)} with result: {result}")
                return result
            except Exception as e:
                t_exception = datetime.now()
                if exception:
                    mylogger.log(exception, f"{e!r} raised in `{f.__name__}` after {str(t_exception-t_before)}!\n{str(e)}".strip())
                raise e
        return wrapper
    return decorator


def returns_time(milis=False, seconds=False):    # defaults to timedelta format

    def decorator(f):
        ReturnClass = namedtuple(f.__name__ + '_result', ('result', 'time'))

        @functools.wraps(f)
        def wrapper(*args, **kw):
            t_before = datetime.now()
            result = f(*args, **kw)
            t_delta = datetime.now() - t_before
            if seconds:
                t_delta = t_delta.total_seconds()
            elif milis:
                t_delta = int(t_delta.total_seconds() * 1000)

            return ReturnClass(result, t_delta)

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

    @ignores(ValueError, IndexError)
    def ignorer(x):
        for i in range(x):
            raise ValueError

    @ignores(ValueError, IndexError)
    @logs()
    def cannot_ignore(x):
        for i in range(x):
            raise ZeroDivisionError

    @fallsback(ValueError, 2)
    def fall2value(x):
        raise ValueError

    @fallsback(ValueError, lambda x: x**2)
    def fall2callable(x):
        raise ValueError

    @fallsback(ZeroDivisionError, 1)
    @fallsback(ValueError, lambda x: x**2)
    def multifall2callable(x):
        if x < 0:
            raise ValueError
        else:
            raise ZeroDivisionError

    @returns_time()
    def mytimed(x):
        z = 0
        for i in range(x * 1000000):
            z += i

    @returns_time(seconds=True)
    def mytimed_seconds(x):
        z = 0
        for i in range(x * 1000000):
            z += i

    @returns('output', 'milis')
    @returns_time(milis=True)
    def mytimed_milis(x):
        z = 0
        for i in range(x * 1000000):
            z += i

    @fallsback(ValueError, 0)
    @logs(before=logging.WARN)
    def logged(x, **kw):
        for i in range(1000000):
            x += i
        raise ValueError

    print('\nnamed tuple outputs:\n')
    print(f'{myfunction(4) = }\n')
    print(f'{list(mygenerator(2)) = }\n')

    print('\nlogging:\n')
    # print(f'{logged(4, key1=5, key2=7.2) = }\n')

    print('\ntiming:\n')
    print(f'{mytimed(16) = }')
    print(f'{mytimed(64) = }')
    print(f'{mytimed_seconds(16) = }')
    print(f'{mytimed_milis(32) = }')

    print('\nexception handlers:\n')
    print(f'{please(5) = }\n')                  # raises warning
    print(f'{ignorer(5) = }\n')
    # print(f'{cannot_ignore(5) = }\n')         # raises ZeroDivisionError
    print(f'{fall2value(5) = }\n')           
    print(f'{fall2callable(5) = }\n')           # pylance thinks its unreachable :)
    print(f'{multifall2callable(0) = }\n')       
    print(f'{multifall2callable(-2) = }\n')       
