# izy
Python functions and classes that make it even *easier*! You will wonder why these are not already built-in in python! :)

> You can skip README and follow (and run) its equivalent [demo notebook](https://colab.research.google.com/github/tabasy/izy/blob/main/notebooks/demo.ipynb).

The sooner you `pip install izy`, the less time you waste! Just 3 keystrokes to install and import :)

```bash
pip install izy
```
Now that you have it, here are the functionlities:

## Sorting 

Some operations like `argsort` need 1 or 2 lines to implement in python, but the code is not pythonically readable as it should be. Some other functions like `topk` are somehow hidden in the built-in modules, which we expose with ease!

Let us have a big list of numbers and give it an `izy` try:
 
```python
>>> from izy import *
>>> mylist = [4.2, 10, -8, 0, 4, 33, 6, 97, 1, 6., 41, -6, 0.0]

>>> topk(mylist, 4)
[97, 41, 33, 10]

>> topk(mylist, -3)     # as you would expect
[-8, -6, 0]             

>>> argmax(mylist)      # not to mention argmin
7

>>> argsort(mylist)
[2, 11, 3, 12, 8, 4, 0, 6, 9, 1, 5, 10, 7]

>>> argsort(mylist, reverse=True)
[7, 10, 5, 1, 6, 9, 0, 4, 8, 3, 12, 11, 2]

>>> descending(mylist)   # I like it more than sorted(x, reverse=True)
[97, 41, 33, 10, 6, 6.0, 4.2, 4, 1, 0, 0.0, -6, -8]

>>> reorder(mylist, argsort(mylist))    # like numpy array indexing
[-8, -6, 0, 0.0, 1, 4, 4.2, 6, 6.0, 10, 33, 41, 97]
```

If you have a `dict` (or more precisely a `Mapping`), the `arg*` functions take `keys` as indices:

```python
>>> mydict = {'a': 1, 'b': 4, 'c': -1}

>>> argmin(mydict)
'c'

>>> reorder(mydict, argsort(mydict))    # sorry it cannot return a sorted dict :) 
[-1, 1, 4]                              # maybe an OrderedDict in the future...
```

## Scorer

The `Scorer` is a `dict` subclass for scoring hashable items. It generalizes functionality of built-in `Counter` to floating-point numbers with full math operation support.

```python
>>> from izy import Scorer
>>> s1 = Scorer({'a': 1, 'b': 2, 'c': 5})
>>> s1['d'] = 3
>>> s1
Scorer({c: 5, d: 3, b: 2, a: 1})

>>> s2 = Scorer('abc', [-2, 3, 4])
>>> s2
Scorer({c: 4, b: 3, a: -2})
```

Mathematical operators (`+`, `-`, `*`, `/`, `//`, `%`, `**`) are supported for both `Scorer` and scalar right-hand operands. 
```python
>>> s1 + s2         
Scorer({c: 9, b: 5, d: 3, a: -1})  

>>> s1 / 4
Scorer({c: 1.25, d: 0.75, b: 0.5, a: 0.25})
```
> ***WARNING!*** To support partial update with math operations, we carry non-common items from the first operand unchanged, but those from the second operand are ignored.

Unary math operators (`+`, `-`) are available too.
```python
>>> +s2             # special usage for useless uniary `+` (only keeps positive itmes)
Scorer({c: 4, b: 3})

>>> s1 + (+s2)      # not equivalent to s1 + s2
Scorer({c: 9, b: 5, d: 3, a: 1})
```

We also have `abs()`, `round()`:
```python
>>> abs(s2) 
Scorer({c: 4, b: 3, a: 2})
```

Logical operators `&`, `|` apply element-wise min/max and they are also applicable to scalars. As `Scorer` is not a `set` or even `multiset` (like `Counter`), we don't refer to these as intersection and union, but the functionalities are still similar. 
  
```python
>>> s1 & s2         # ~ min (drops non-common items)
Scorer({c: 4, b: 2, a: -2})

>>> s1 & 2          # drops items with score less than 2
Scorer({c: 5, d: 3, b: 2})

>>> s1 | s2         # ~ max
Scorer({c: 5, b: 3, d: 3, a: 1})
```
> About the above warning, note that `(s1 | (s1 & s2))` gives the subset of `s1` which also exists in `s2`. You can use this to force math operations to return common items only.

And finally the ultimate goal of the `Scorer` is to sort its items according to scores and give us the `best`, `topk` (or `worst`, `bottomk`). 

```python
>>> s1.best()           
('c', 5)

>>> s1.topk(3)          # alias to `s1.best` but more readable when you specify the number of items
[('c', 5), ('d', 3), ('b', 2)]

>>> s1.topk(-2)         # negative k means bottom k
[('a', 1), ('b', 2)]

>>> s1.ascending()      # prefer this to `best` or `topk` with special values of n or k (None, 0, inf)
[('a', 1), ('b', 2), ('d', 3), ('c', 5)]

>>> s1.median()         # if scorer length is even, lower median is returned
('b', 2)
```

## Decorators

Python `functools` is really interesting, but it really lacks some generally usefull decorators.

First, `@returns()` and `@yields()` make your function/generator return/yield `namedtuple`s to more pythonically access your function output. It also looks like an easy documentation to me (about the *meaning* of what function returns and not just the `type`).

```python
@returns('x', 'plus_one')
def myfunction(x):
    return x, x+1

@yields('a', 'a_doubled')
def mygenerator(x):
    for i in range(x):
        yield {'a':i, 'a_doubled': i*2}

n = myfunction(5).plus_one
```

`@returns_time()` calculates function runtime and returns it as a `datetime.timedelta` object. You can change time format to `milis` (`int`) or `seconds` (`float`). It returns a  `namedtuple` which you can rename using `@returns`.

```python
@returns_time()
def timed(x):
    z = 0
    for i in range(x * 1000000):
        z += i

@returns('output', 'milis')
@returns_time(milis=True)
def timed_milis(x):
    z = 0
    for i in range(x * 1000000):
        z += i
    return 'done'

>>> timed(64)
timed_output(output=None, time=datetime.timedelta(seconds=2, microseconds=530048))

>>> timed_milis(32)
timed_milis_output(output='done', milis=1289)
```

`@logs()` does what it says at three stages: before calling, after returning and on exceptions. You can control log level for each stage, log `to_file` using default logger (named after the function) or pass your own `logging.Logger`.

```python

@logs(before=logging.DEBUG, after=logging.INFO, to_file='logged.log')
def logged(x, **kw):
    for i in range(1000000):
        x += i

>>> logged(1, key1=5, key2=7.2)

[2021-12-31 08:56:33][logged][DEBUG] - Function `logged` called with args: (4, key1=5, key2=7.2)
[2021-12-31 08:56:33][logged][INFO] - Function `logged` returned after 0:00:00.029084 with result: None
```

`@fix_this()` reminds you to fix something in stronger way than a passive comment. It raises `UserWarning` at runtime and does this everytime :)
```python
@fix_this('It always prints ValueError, errors should be raised!')
def please(x):
    print('ValueError')
```

This one `@ignores()` given exceptions (and returns `None`). Who knows when and why you need this? :) You can stack it on top of `@logs()` to be aware of ignored exceptions.  
```python
@ignores(ValueError, IndexError)
@logs()
def ignorer(x):
    for i in range(x):
        raise ValueError
```

Want more useful exception handler? `@fallsback()` falls back on specified exception to predefined return value or another `callable`. For multiple exceptions, stack it like this:

```python
@fallsback(ZeroDivisionError, 1)
@fallsback(ValueError, lambda x: x**2)
def multifall2callable(x):
    if x < 0:
        raise ValueError
    else:
        raise ZeroDivisionError
```
