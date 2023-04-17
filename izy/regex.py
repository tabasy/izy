"""Regular expression helper functions.

>>> p = make_regex(
...    following('then '),      # lookbehind
...    grouped(r'[a-z ]+', name='code'),
...    followed_by(r' end'),     # lookahead
...    )
>>> p.pattern
'(?<=then )(?P<code>[a-z ]+)(?= end)'
>>> p.search('if condition then do something end; etc')
<re.Match object; span=(18, 30), match='do something'>

>>> p = make_regex(
...    any_of('ali', 'hossein', 'javad'),
...    SPACES,
...    any_of('goodarzi', 'sharafi', name='family')
...    )
>>> p.pattern
'(?:hossein|javad|ali)\\\\s+(?P<family>goodarzi|sharafi)'
>>> match = p.search('his name is hossein sharafi.')
>>> match
<re.Match object; span=(12, 27), match='hossein sharafi'>
>>> match.group('family')
'sharafi'

>>> p = make_regex(
...    any_of(
...        grouped('<p>', name='p'),
...        grouped('<div>', name='div'),
...        name='tag'
...    ),
...    repeated('.', greedy=False, name='inside'), 
...    if_matched('p', then='</p>', otherwise='</div>')
...    )
>>> p.pattern        # this is really hard to read
'(?P<tag>(?P<div><div>)|(?P<p><p>))(?P<inside>(?:.)+?)(?(p)</p>|</div>)'
>>> text = '<div><p>hello world!</p></div><p>good morning...</p><div>bye!</div>'
>>> for m in p.finditer(text):
...     print(m.group('tag'), m.group('inside'))
<div> <p>hello world!</p>
<p> good morning...
<div> bye!

>>> p = make_regex('[0-9]')
>>> p.sub(repl({'1': 'one', '2': 'two'}), '2 and a half.')
'two and a half.'

>>> p = make_regex('[0-9()\-+/*]{3,}')
>>> p.sub(repl(eval), 'It costs 25*4+10 for you.')
'It costs 110 for you.'
"""

import re
from operator import ior
from typing import Mapping
from functools import reduce


__all__ = ['join_patterns', 'make_regex', 'grouped', 
           'atomic', 'if_matched',
           'followed_by', 'not_followed_by',
           'following', 'not_following', 
           'preceded_by', 'not_preceded_by', 
           'lookahead', 'neg_lookahead',
           'lookbehind', 'neg_lookbehind',
           'repeated', 'possibly',
           'wordbounded', 'any_of', 'charset', 'any_char_but',
           'bag_of_patterns',
           'map2repl', 'func2repl', 'repl', 
           'SPACES', 'DIGITS', 'DOT', 'BOS', 'EOS', 'BOL', 'EOL',
           ]


SPACES = r'\s+'
DIGITS = r'\d+'

DOT = r'\.'
BOS = r'\A'
EOS = r'\Z'
BOL = r'^'
EOL = r'$'


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

# special groups

def atomic(*pattern):
    pattern = join_patterns(pattern)
    return fr'(?>{pattern})'


def if_matched(group_name, *, then, otherwise=''):
    return fr'(?({group_name}){then}|{otherwise})'


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


# extras

def repeated(*pattern, n=None, min=1, max=None, greedy=True, possessive=False, name=None):
    """Repeated pattern

    Args:
        n (int, optional): Exact number of repetitions. If provided, `min`, `max` are ignored. Defaults to None.
        min (int, optional): Minimum number of repetitions. Defaults to 1.
        max (int, optional): Maximum number of repetitions. Defaults to None.
        greedy (bool, optional): Match as much as possible? Defaults to True.
        possessive (bool, optional): Do not backtrack after maching greedily? Defaults to False.
        name (str, optional): The name of pattern group. if None, a non-capturing group is used. Defaults to None.

    """
    if n is not None:
        return grouped(*pattern, name=name, no_capture=True) + fr'{{{n}}}'
    
    min_reps = str(min) if min else ''
    max_reps = str(max) if max else ''
    
    special = ''
    if not greedy:
        special = '?'
    elif possessive:
        special = '+'
    
    repeats = fr'{{{min_reps},{max_reps}}}'
    repeats = repeats.replace('{1,}', '+')
    repeats = repeats.replace('{,}', '*')
    repeats = repeats.replace('{,1}', '?')
    
    pattern = grouped(*pattern, no_capture=True) + fr'{repeats}{special}'
    
    if name:
        return grouped(pattern, name=name)
    return pattern


def possibly(*pattern, name=None):
    return grouped(pattern, name=name, no_capture=True) + '?'


def wordbounded(*pattern, name=None):
    pattern = join_patterns(r'\b', *pattern, r'\b')
    if name:
        return grouped(pattern, name=name)
    return pattern


def any_of(*patterns, sort=True, name=None):
    """Makes the pattern to match any of the input patterns (using `|`). Optionally,
    sorts the patterns starting from the longest to prioritize for the longest. But
    this only works for fixed-length patterns, as the lenght of dynamic patterns 
    cannot be determined.

    Args:
        patterns (Iterable): The input patterns.
        sort (bool, optional): Whether or not to sort the patterns starting from the longest. Defaults to True.
        name (str, optional): The name of pattern group. if None, a non-capturing group is used. Defaults to None.
    """
    if len(patterns) == 1 and not isinstance(patterns[0], str):
        patterns = patterns[0]
    if sort:
        patterns = sorted(patterns, key=len, reverse=True)

    return grouped(r'|'.join(patterns), name=name, no_capture=True)


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


# repl maker

def func2repl(fn, group=0):
    """Converts a str-to-str function, to a valid `repl` argument for `re.sub()`.

    Args:
        fn (function): A str to str function.
        group (int, optional): The match group to pass to the function. Defaults to 0.
    """
    def repl_func(match):
        return str(fn(match.group(group)))
    return repl_func


def map2repl(mapping: Mapping, group=0, default_str=''):
    """Converts a str-to-str mapping, to a valid `repl` argument for `re.sub()`.

    Args:
        mapping (_type_): _description_
        group (int, optional): The match group to pass to the function. Defaults to 0.
        default_str (str, optional): _description_. Defaults to ''.
    """
    def repl_func(match):
        return str(mapping.get(match.group(group), default_str))
    return repl_func


def repl(rep, group=0):
    if isinstance(rep, Mapping):
        return map2repl(rep, group=group)
    elif callable(rep):
        return func2repl(rep, group=group)
    else:
        raise ValueError(
            'Provide a `Callable` or `Mapping` to make a repl function')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
