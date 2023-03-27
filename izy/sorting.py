"""Sorting-related utils.

>>> mylist = [4, 10, -8, 0, 4, 33, 6, 97, 1, 6., 41, -6, 0.0]

>>> topk(mylist, 4)
[97, 41, 33, 10]
>>> topk(mylist, -3)
[-8, -6, 0]

>>> argmax(mylist)
7
>>> argmin(mylist)
2
>>> argsort(mylist)
[2, 11, 3, 12, 8, 0, 4, 6, 9, 1, 5, 10, 7]
>>> argsort(mylist, reverse=True)
[7, 10, 5, 1, 6, 9, 0, 4, 8, 3, 12, 11, 2]
>>> argtopk(mylist, 3)
[7, 10, 5]
>>> argtopk(mylist, 4, reverse=True)
[2, 11, 3, 12]

>>> ascending(mylist)
[-8, -6, 0, 0.0, 1, 4, 4, 6, 6.0, 10, 33, 41, 97]
>>> descending(mylist)
[97, 41, 33, 10, 6, 6.0, 4, 4, 1, 0, 0.0, -6, -8]
>>> reorder(mylist, argsort(mylist))
[-8, -6, 0, 0.0, 1, 4, 4, 6, 6.0, 10, 33, 41, 97]

>>> mydict = {'a': 1, 'b': 4, 'c': -1}

# for dicts, keys are considered as indices
>>> argmin(mydict)
'c'
>>> argmax(mydict)
'b'
>>> argsort(mydict)
['c', 'a', 'b']

>>> reorder(mydict, argsort(mydict))
OrderedDict([('c', -1), ('a', 1), ('b', 4)])
>>> ordered(mydict)
OrderedDict([('c', -1), ('a', 1), ('b', 4)])
>>> ordered(mydict, by_keys=True)
OrderedDict([('a', 1), ('b', 4), ('c', -1)])

"""

from typing import AbstractSet, MutableSequence, MutableSet, AbstractSet, Union, Sequence, Mapping
from collections import OrderedDict
import heapq


__all__ = ['ascending', 'descending', 'topk',
           'argtopk', 'argsort', 'argsorted',
           'argmin', 'argmax', 'reorder', 'ordered']


Sortable = Union[Sequence, Mapping, AbstractSet]


def topk(x: Sortable, k, reverse=False, key=None):
    if reverse or k < 0:
        return heapq.nsmallest(abs(k), x, key=key)
    else:
        return heapq.nlargest(k, x, key=key)


def decide_arg(x: Sortable):
    if isinstance(x, Mapping):
        return x.keys()
    else:
        return range(len(x))


def argtopk(x: Sortable, k, reverse=False):
    return topk(decide_arg(x), k, reverse=reverse, key=x.__getitem__)


def argsort(x: Sortable, reverse=False):
    return sorted(decide_arg(x), key=x.__getitem__, reverse=reverse)


def argsorted(x: Sortable, reverse=False):
    return argsort(x, reverse)


def argmax(x: Sortable):
    return max(decide_arg(x), key=x.__getitem__)


def argmin(x: Sortable):
    return min(decide_arg(x), key=x.__getitem__)


def reorder(x: Sortable, indices):
    if isinstance(x, (Mapping)):
        # dict() is ordered too, by OrderedDict() is more explicit
        return OrderedDict({key: x[key] for key in indices})

    elif isinstance(x, (Sequence)):
        reordered_x = (x[i] for i in indices)
        if isinstance(x, (MutableSequence)):
            return list(reordered_x)
        else:
            return tuple(reordered_x)
    else:
        raise NotImplementedError


def ordered(x: Sortable, by_keys=False, reverse=False):
    if isinstance(x, (Mapping)):
        if by_keys:
            sorted_keys = sorted(x.keys(), reverse=reverse)
        else:
            sorted_keys = argsorted(x, reverse=reverse)
        return reorder(x, sorted_keys)

    elif isinstance(x, (Sequence, AbstractSet)):
        sorted_x = sorted(x, reverse=reverse)
        if isinstance(x, (MutableSequence, MutableSet)):
            return sorted_x
        else:
            return tuple(sorted_x)
    else:
        raise NotImplementedError


def ascending(x, by_keys=False):
    return ordered(x, by_keys=by_keys, reverse=False)


def descending(x, by_keys=False):
    return ordered(x, by_keys=by_keys, reverse=True)


if __name__ == '__main__':

    import doctest
    doctest.testmod()
