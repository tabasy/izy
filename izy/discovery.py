"""Utils for discovering contents, structure, specs of complex objects

>>> x = [
...    (1, 2, 3, 4),
...    {1: range(3), 2: range(2, 40, 2), 5: 6, 7: 8},
...    range(1000),
...    (7, 8, 9, 10),
...    *range(10)
...    ]

>>> head(x)
[(1, 2, 3), {1: (0, 1, 2), 2: (2, 4, 6), 5: 6, 7: 8}, (0, 1, 2)]

>>> head(x, n=2, ellipsis=True)
[(1, 2, ...), {1: (0, 1, ...), 2: (2, 4, ...), ...: ...}, ...]

>>> print(phead(x))
[ (1, 2, 3, ...),
  {1: (0, 1, 2), 2: (2, 4, 6, ...), 5: 6, ...: ...},
  (0, 1, 2, ...),
  ...]

>>> hprint(x, n=5, width=32, indent=4)
[   (1, 2, 3, 4),
    {   1: (0, 1, 2),
        2: (   2,
               4,
               6,
               8,
               10,
               ...),
        5: 6,
        7: 8},
    (0, 1, 2, 3, 4, ...),
    (7, 8, 9, 10),
    0,
    ...]
"""


from pprint import pprint, pformat
from typing import Iterable, Mapping, Sequence, MutableSequence, MutableSet

__all__ = ['head', 'phead', 'hprint']


class Etc:
    """A decorative object to append to truncated iterables.
    """

    def __bool__(self):
        return False

    def __eq__(self, other):
        return other == Ellipsis

    def __repr__(self):
        return '...'

    def __str__(self):
        return '...'

    def __hash__(self):
        return 0

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return True

    def __cmp__(self, other):
        return 1


def head(x, n=3, ellipsis=False):
    """Recuresivly iterates over a (possibly nested and infinite) iterable, and truncates each
    iterable to a limited length.

    Args:
        x: The input iterable
        n (int, optional): Length of head for each iterable. Defaults to 3.
        ellipsis (bool, optional): Add an ellipsis to the end of each truncated iterator. Defaults to False.

    Returns:
        Iterable: The truncated iterable, with same structure as the input.
    """

    if not isinstance(x, Iterable):
        return x

    if isinstance(x, str):
        return x

    items = []

    if isinstance(x, Mapping):

        for idx, k in enumerate(x):
            if idx == n:
                if ellipsis:
                    items.append((Etc(), Etc()))
                    break
            items.append((k, head(x[k], n, ellipsis)))
        return dict(items)

    else:
        for idx, item in enumerate(x):
            if idx == n:
                if ellipsis:
                    items.append(Etc())
                break
            items.append(head(item, n, ellipsis))
        if isinstance(x, MutableSequence):
            return list(items)
        elif isinstance(x, Sequence):
            return tuple(items)
        elif isinstance(x, MutableSet):
            return set(items)
        else:
            return items


def phead(x, n=3, depth=None, width=80, indent=2, **kwargs):
    """Returns pretty-formatted head of the (possibly nested and infinite) input iterable.
    Args:
        x (int): The input iterable
        n (int, optional): Length of head for each iterable. Defaults to 3.
        depth (int, optional): Max recursion depth. Defaults to None.
        width (int, optional): Max width for each output line. Defaults to 80.
        indent (int, optional): The amount of indentation added for each recursive level. Defaults to 2.

    Returns:
        str: Pretty-formatted head of the input iterable.
    """

    x_head = head(x, n, ellipsis=True)
    return pformat(x_head, depth=depth, width=width, indent=indent, **kwargs)


def hprint(x, n=3, depth=None, width=80, indent=2, **kwargs):
    """Prints prettified head of the (possibly nested and infinite) input iterable.
    Args:
        x (int): The input iterable
        n (int, optional): Length of head for each iterable. Defaults to 3.
        depth (int, optional): Max recursion depth. Defaults to None.
        width (int, optional): Max width for each output line. Defaults to 80.
        indent (int, optional): The amount of indentation added for each recursive level. Defaults to 2.

    Returns:
        Truncated head of the input iterable.
    """

    x_head = head(x, n, ellipsis=True)
    pprint(x_head, depth=depth, width=width, indent=indent, **kwargs)


# def methods(obj, args=None, kwargs=None):
#     ...


# def attributes(obj, types=None):
#     ...


# def parents(obj):
#     ...


# def brief(x):
#     # path, file
#     # function
#     # generator
#     # iterable
#     # custom instance
#     ...


if __name__ == '__main__':

    import doctest
    doctest.testmod()
