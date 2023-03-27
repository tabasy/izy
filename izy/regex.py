"""Regular expression helper functions.

>>> p = make_regex(
...    following('then '),      # lookbehind
...    charset('a-z '), '+',
...    followed_by(r' end')     # lookahead
...    )
>>> p.pattern
'(?<=then )[a-z ]+(?= end)'
>>> p.search('if condition then do something end; etc')
<re.Match object; span=(18, 30), match='do something'>

>>> p = make_regex(
...    any_of('ali', 'hossein', 'javad'),
...    '\s+',
...    grouped(any_of('goodarzi', 'sharafi'), name='family')
...    )
>>> p.pattern
'(?:hossein|javad|ali)\\\\s+(?P<family>(?:goodarzi|sharafi))'
>>> match = p.search('his name is hossein sharafi.')
>>> match
<re.Match object; span=(12, 27), match='hossein sharafi'>
>>> match.group('family')
'sharafi'
"""

import re
from operator import ior
from typing import Mapping
from functools import reduce


__all__ = ['make_regex', 'grouped', 'if_matched',
           'followed_by', 'not_followed_by',
           'following', 'not_following', 
           'preceded_by', 'not_preceded_by', 
           'lookahead', 'neg_lookahead',
           'lookbehind', 'neg_lookbehind',
           'wordbounded', 'any_of', 'charset', 'any_char_but',
           'bag_of_patterns',
           'map2repl', 'func2repl', 'repl', 
           ]

def join_patterns(*patterns, joiner=''):
    if len(patterns) == 1 and not isinstance(patterns[0], str):
        patterns = patterns[0]
    return joiner.join(patterns)


def make_regex(*patterns, ascii=False, debug=False, ignorecase=False,
               locale=False, multiline=False, dotall=False, verbose=False):
    """Compiles the given pattern(s) into a regular expression object, using `re` flags as kwargs.

    Returns:
        re.Pattern: The compiled regex pattern object
    """
    flags = [
        re.ASCII if ascii else 0,
        re.DEBUG if debug else 0,
        re.IGNORECASE if ignorecase else 0,
        re.LOCALE if locale else 0,
        re.MULTILINE if multiline else 0,
        re.DOTALL if dotall else 0,
        re.VERBOSE if verbose else 0]
    return re.compile(join_patterns(patterns), flags=reduce(ior, flags))


def grouped(*pattern, name=None, no_capture=False):
    pattern = join_patterns(pattern)
    if name:
        return fr'(?P<{name}>{pattern})'
    if no_capture:
        return fr'(?:{pattern})'

    return fr'({pattern})'


def followed_by(*pattern, immediately=True):
    pattern = join_patterns(pattern)
    prefix = '' if immediately else '.*'
    return fr'(?={prefix}{pattern})'


def not_followed_by(*pattern, immediately=True):
    pattern = join_patterns(pattern)
    prefix = '' if immediately else '.*'
    return fr'(?!{prefix}{pattern})'


def following(*pattern):
    pattern = join_patterns(pattern)
    return fr'(?<={pattern})'


def not_following(*pattern):
    pattern = join_patterns(pattern)
    return fr'(?<!{pattern})'


preceded_by = following
not_preceded_by = not_following

lookahead = followed_by
neg_lookahead = not_followed_by
lookbehind = preceded_by
neg_lookbehind = not_preceded_by


def wordbounded(*pattern):
    pattern = join_patterns(pattern)
    return fr'\b{pattern}\b'


def if_matched(group_name, *, then, otherwise=''):
    pattern = join_patterns(pattern)
    return fr'(?({group_name}){then}|{otherwise})'


def any_of(*patterns, sort=True):
    """Makes the pattern to match any of the input patterns (using `|`). Optionally,
    sorts the patterns starting from the longest to prioritize for the longest. But
    this only works for fixed-length patterns, as the lenght of dynamic patterns 
    cannot be determined.

    Args:
        patterns (Iterable): The input patterns.
        sort (bool, optional): Whether or not to sort the patterns starting from the longest. Defaults to True.
    """
    if len(patterns) == 1 and not isinstance(patterns[0], str):
        patterns = patterns[0]
    if sort:
        patterns = sorted(patterns, key=len, reverse=True)
    return grouped(r'|'.join(patterns), no_capture=True)


def charset(characters: str):
    return fr'[{characters}]'


def any_char_but(characters: str):
    return fr'[^{characters}]'


def bag_of_patterns(*patterns):
    """Makes a pattern that matches if all of the input patterns,
    are matched anywhere in the following string.

    Args:
        patterns (Iterable): The input patterns.
    """
    if len(patterns) == 1 and not isinstance(patterns[0], str):
        patterns = patterns[0]
    return ''.join(followed_by(p, immediately=False) for p in patterns)



def func2repl(fn, group=0):
    """Converts a str to str function, to a valid `repl` argument for `re.sub()`.

    Args:
        fn (function): A str to str function.
        group (int, optional): The match group to pass to the function. Defaults to 0.
    """
    def repl_func(match):
        return fn(match.group(group))
    return repl_func


def map2repl(mapping: Mapping, group=0, default_str=''):
    """Converts a str to str mapping, to a valid `repl` argument for `re.sub()`.

    Args:
        mapping (_type_): _description_
        group (int, optional): The match group to pass to the function. Defaults to 0.
        default_str (str, optional): _description_. Defaults to ''.
    """
    def repl_func(match):
        return mapping.get(match.group(group), default_str)
    return repl_func


def repl(rep, group=0):
    if isinstance(rep, Mapping):
        return map2repl(rep, group=group)
    elif callable(rep):
        func2repl(rep, group=group)
    else:
        raise ValueError(
            'Provide a `Callable` or `Mapping` to make a repl function')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
