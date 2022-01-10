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
        return OrderedDict({key: x[key] for key in indices})        # dict() is ordered too, by OrderedDict() is more explicit

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

    mylist = [4, 10, -8, 0, 4, 33, 6, 97, 1, 6., 41, -6, 0.0]

    # print(f'{mylist = }\n')
    # print(f'{topk(mylist, 4) = }')
    # print(f'{topk(mylist, -3) = }\n')
    
    # print(f'{argmax(mylist) = }')
    # print(f'{argmin(mylist) = }\n')
    
    # print(f'{argsort(mylist) = }')
    # print(f'{argsort(mylist, reverse=True) = }\n')

    # print(f'{argtopk(mylist, 3) = }')
    # print(f'{argtopk(mylist, 4, reverse=True) = }\n')

    # print(f'{ascending(mylist) = }')
    # print(f'{descending(mylist) = }\n')

    # print(f'{reorder(mylist, argsort(mylist)) = }\n')

    # mydict = {'a': 1, 'b': 4, 'c': -1}

    # print('\nfor dicts, keys are considered as indices:')
    # print(f'{mydict = }\n')
    
    # print(f'{argmin(mydict) = }\n')
    # print(f'{argmax(mydict) = }\n')
    # print(f'{argsort(mydict) = }\n')
    # print(f'{reorder(mydict, argsort(mydict)) = }')
    # print(f'{reorder(mydict, argsort(mydict)) = }')
    # print(f'{ordered(mydict) = }')
    # print(f'{ordered(mydict, by_keys=True) = }')
