from collections.abc import Mapping
import operator as op
import heapq


class Scorer(dict):
    '''Dict subclass for scoring hashable items. Derived from
    builtin python Counter class. Elements are stored as dictionary
    keys and their scores are stored as dictionary values.

    >>> s1 = Scorer({'a': 1, 'b': 2, 'c': 5})
    >>> s1['d'] = 3
    >>> s1
    Scorer({c: 5, d: 3, b: 2, a: 1})

    >>> s2 = Scorer('abc', [-2, 3, 4])
    >>> s2
    Scorer({c: 4, b: 3, a: -2})

    # to support partial add, etc. we carry non-common items from the first scorer unchanged,
    # but those from the second operand are ignored.
    >>> s1 + s2         # binary mathematical operators: +, -, *, /, //, %, **
    Scorer({c: 9, b: 5, d: 3, a: -1})

    >>> s1 / 4          # mathematical operators apply to scalar values
    Scorer({c: 1.25, d: 0.75, b: 0.5, a: 0.25})

    >>> s1 & s2         # ~ min (drops non-common items)
    Scorer({c: 4, b: 2, a: -2})

    >>> s1 & 2          # drops items with score less than 2
    Scorer({c: 5, d: 3, b: 2})

    # ss = (s1 | (s1 & s2)) gives the subset of s1 which also exists in s2
    # you can use this to force math operations to return common items only
    >>> s1 | s2         # ~ max (also aplicable to scalars)
    Scorer({c: 5, b: 3, d: 3, a: 1})

    >>> abs(s2)         # overriden functions: abs(), round()
    Scorer({c: 4, b: 3, a: 2})

    >>> +s2             # special unary oprator (drops items with scores <= 0)
    Scorer({c: 4, b: 3})

    >>> s1 + (+s2)      # not equivalent to s1 + s2
    Scorer({c: 9, b: 5, d: 3, a: 1})
    '''

    def __init__(self, *args, missing_value=0, **kwds):
        '''Initialize a Scorer object with optionally given values.
        '''
        self.missing_value = missing_value
        if len(args) > 2:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        super(Scorer, self).__init__()
        self.update(*args, **kwds)

    def __missing__(self, key):
        return self.missing_value

    def bottomk(self, k):
        if k in [None, 0, float('inf')]:
            return self.topk(float('-inf'))
        return self.topk(-k)

    def middlek(self, k):
        raise NotImplementedError

    def best(self):
        return max(self.items(), key=op.itemgetter(1))
    
    def worst(self):
        return min(self.items(), key=op.itemgetter(1))

    def ascending(self):
        return sorted(self.items(), key=op.itemgetter(1), reverse=False)

    def descending(self):
        return sorted(self.items(), key=op.itemgetter(1), reverse=True)

    def median(self):
        if len(self) == 0:
            return None
        med_idx = (len(self)+1) // 2
        return self.topk(med_idx + 1)[med_idx]

    def topk(self, k=1):
        '''List the top k items and their scores.
        If k is negative, then list the bottom k worst items ~ `bottomk(abs(k))`.
        elif k is None, zero or inf, then list all items starting from the top ~ `descending()`,
        elif k is -inf, then list all items starting from the bottom ~ `ascending()`.
        '''
        if k in [None, 0, float('inf')]:
            return self.descending()
        if k == float('-inf'):
            return self.ascending()
        if k < 0:
            return heapq.nsmallest(abs(k), self.items(), key=op.itemgetter(1))
        else:
            return heapq.nlargest(k, self.items(), key=op.itemgetter(1))

    # Override dict methods where necessary

    def update(self, *args, **kwds):
        '''Like dict.update() but add scores instead of replacing them.
        Source can be an iterable, a dictionary, or another Scorer instance.
        '''

        if len(args) > 2:
            raise TypeError('expected at most 2 arguments, got %d' % len(args))
        # print(args)
        if len(args) == 2:
            new_scores = dict(zip(args[0], args[1]))
        elif len(args) == 1:
            new_scores = dict(args[0])  # expected list of tuples
        else:
            new_scores = None
        
        if new_scores is not None:
            if self:
                for elem, score in new_scores.iteritems():
                    self[elem] = self[elem] + score
            else:
                super(Scorer, self).update(new_scores)      # fast path when scorer is empty
        if kwds:
            self.update(kwds)

    def subtract(self, other):
        return self - other

    def copy(self):
        'Return a shallow copy.'
        return self.__class__(self)

    def __reduce__(self):
        return self.__class__, (dict(self),)

    def __delitem__(self, elem):
        'Like dict.__delitem__() but does not raise KeyError for missing values.'
        if elem in self:
            super(Scorer, self).__delitem__(elem)

    def __repr__(self):
        if not self:
            return f'{self.__class__.__name__}()'
        max_num = 9
        space = ' '
        if len(self) <= max_num:
            items = f',{space}'.join(map(lambda x: f'{x[0]}: {x[1]}', self.topk(k=max_num)))
        if len(self) > max_num:
            top = f',{space}'.join(map(lambda x: f'{x[0]}: {x[1]}', self.topk(k=max_num//2)))
            median =  '{}: {}'.format(*self.median())
            bottom = f',{space}'.join(map(lambda x: f'{x[0]}: {x[1]}', self.topk(k=-(max_num//2))))
            items = f'{top},{space}...,{space}{median},{space}..,{space}{bottom}'
        return f'{self.__class__.__name__}({{{items}}})'

    def _binary_operator(self, other, operator):
        result = self.copy()
        if isinstance(other, Mapping):
            for elem, score in self.items():  # not efficient!
                if elem in other:
                    result[elem] = operator(score, other[elem])
        elif isinstance(other, (int, float)):
            for elem, score in self.items():
                result[elem] = operator(score, other)
        else:
            raise ValueError
        return result

    def _unary_operator(self, operator):
        result = Scorer()
        for elem, score in self.items():
            result[elem] = operator(score)
        return result

    def __pos__(self):
        result = Scorer()
        for elem, score in self.items():
            if score > 0:
                result[elem] = score
        return result

    def __neg__(self):
        return self._unary_operator(op.__neg__)
    def __abs__(self):
        return self._unary_operator(op.__abs__)

    def __add__(self, other):
        return self._binary_operator(other, op.__add__)
    def __sub__(self, other):
        return self._binary_operator(other, op.__sub__)
    def __round__(self, other):
        return self._binary_operator(other, round)

    def __mul__(self, other):
        return self._binary_operator(other, op.__mul__)
    def __truediv__(self, other):
        return self._binary_operator(other, op.__truediv__)
    def __floordiv__(self, other):
        return self._binary_operator(other, op.__floordiv__)
    def __pow__(self, other):
        return self._binary_operator(other, op.__pow__)
    def __mod__(self, other):
        return self._binary_operator(other, op.__mod__)

    def __or__(self, other):
        '''Maximum of value in either of the Scorers.
        The other value can be a scalar with the same behavior.
        '''
        result = self.copy()
        if isinstance(other, Scorer):
            for elem, score in other.items():
                if elem in self:
                    result[elem] = max(self[elem], score)
                else:
                    result[elem] = score
        elif isinstance(other, (int, float)):
            for elem, score in self.items():
                result[elem] = max(score, other)
        else:
            raise NotImplementedError

        return result

    def __and__(self, other):
        '''Minimum of corresponding scores among two Scorers.
        If other is a scalar, drops items with score < other.
        '''
        result = Scorer()
        if isinstance(other, Scorer):
            for elem, score in self.items():
                if elem in other:
                    result[elem] = min(score, other[elem])
        elif isinstance(other, (int, float)):
            for elem, score in self.items():
                if score >= other:
                    result[elem] = score
        else:
            raise NotImplementedError
        return result


if __name__ == '__main__':
    
    import doctest
    doctest.testmod()