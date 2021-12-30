from typing import Union, Sequence, Mapping
import heapq


__all__ = ['ascending', 'descending', 'topk', 
           'argtopk', 'argsort', 'argsorted',
           'argmin', 'argmaseq', 'reorder']

def ascending(x):
    return sorted(x, reverse=False)

def descending(x):
    return sorted(x, reverse=True)

def topk(x: Union[Sequence, Mapping], k, reverse=False, key=None):
    if reverse or k < 0:
        return heapq.nsmallest(abs(k), x, key=key)
    else:
        return heapq.nlargest(k, x, key=key)


def _getarg(x: Union[Sequence, Mapping]):
    if isinstance(x, Mapping):
        return x.keys()
    else:
        return range(len(x))


def argtopk(x: Union[Sequence, Mapping], k, reverse=False):
    return topk(_getarg(x), k, reverse=reverse, key=x.__getitem__)

def argsort(x: Union[Sequence, Mapping], reverse=False):
    return sorted(_getarg(x), key=x.__getitem__, reverse=reverse)

def argsorted(x: Union[Sequence, Mapping], reverse=False):
    return argsort(x, reverse)


def argmax(x: Union[Sequence, Mapping]):
    return max(_getarg(x), key=x.__getitem__)

def argmin(x: Union[Sequence, Mapping]):
    return min(_getarg(x), key=x.__getitem__)

def reorder(x: Union[Sequence, Mapping], indices):   # reorder tuple? dict?!
    return [x[i] for i in indices]


if __name__ == '__main__':

    mylist = [4, 10, -8, 0, 4, 33, 6, 97, 1, 6., 41, -6, 0.0]

    print(f'{mylist = }\n')
    print(f'{topk(mylist, 4) = }')
    print(f'{topk(mylist, -3) = }\n')
    
    print(f'{argmax(mylist) = }')
    print(f'{argmin(mylist) = }\n')
    
    print(f'{argsort(mylist) = }')
    print(f'{argsort(mylist, reverse=True) = }\n')

    print(f'{argtopk(mylist, 3) = }')
    print(f'{argtopk(mylist, 4, reverse=True) = }\n')

    print(f'{ascending(mylist) = }')
    print(f'{descending(mylist) = }\n')

    print(f'{reorder(mylist, argsort(mylist)) = }\n')

    mydict = {'a': 1, 'b': 4, 'c': -1}

    print('\nfor dicts, keys are considered as indices:')
    print(f'{mydict = }\n')
    
    print(f'{argmin(mydict) = }\n')
    print(f'{argmax(mydict) = }\n')
    print(f'{argsort(mydict) = }\n')
    print(f'{reorder(mydict, argsort(mydict)) = }')


