
# izy

Python functions and classes that make it even *easier*! You will wonder why these are not already built-in in python! :)

> You can skip README and follow (and run) its equivalent [demo notebook](https://colab.research.google.com/github/tabasy/izy/blob/main/notebooks/demo.ipynb).

The sooner you `pip install izy`, the less time you waste! Just 3 keystrokes to install and import :)

```bash
pip install izy
```
Now that you have it, here are the functionalities:

# Sorting

Some operations like `argsort` need 1 or 2 lines to implement in python, but the code is not pythonically readable as it should be. Some other functions like `topk` are somehow hidden in the built-in modules, which we expose with ease!

Let us have a big list of numbers and give it an `izy` try:


```python
from izy import *

mylist = [4.2, 10, -8, 0, 4, 33, 6, 97, 1, 6., 41, -6, 0.0]

>>> topk(mylist, 4)
[97, 41, 33, 10]

>>> topk(mylist, -3)     # as you would expect
[-8, -6, 0]

>>> argmin(mylist), argmax(mylist)
(2, 7)

>>> argsort(mylist)
[2, 11, 3, 12, 8, 4, 0, 6, 9, 1, 5, 10, 7]

>>> descending(mylist)   # I like it more than sorted(x, reverse=True)
[97, 41, 33, 10, 6, 6.0, 4.2, 4, 1, 0, 0.0, -6, -8]

>>> reorder(mylist, argsort(mylist))    # like numpy array indexing
[-8, -6, 0, 0.0, 1, 4, 4.2, 6, 6.0, 10, 33, 41, 97]
```


If you have a `dict` (or more precisely a `Mapping`), the `arg*` functions take `keys` as indices:


```python
mydict = {'a': 1, 'b': 4, 'c': -1}

>>> argmin(mydict)
'c'

>>> reorder(mydict, argsort(mydict))    # as it should be
OrderedDict([('c', -1), ('a', 1), ('b', 4)])
```

If you liked what `reorder()` did to a dictionary, consider `ordered()` as an alternative to built-in `sorted()`. `ordered()` tries to return the sorted (ordered) variant of the input, while preserving its key properties. The behavior is as follows:
* `Mapping`-> `OrderedDict` which is a `Mapping` too.
* `MutableSequence` or `MutableSet` -> `list` (equivalent to `sorted()` in this case)
* *immutable* `Sequence` or `Set` -> `tuple`

```python
>>> ordered(mydict)
OrderedDict([('c', -1), ('a', 1), ('b', 4)])

>>> ordered(frozenset({2, 4, -5}))
(-5, 2, 4)
```


# Scorer

The `Scorer` is a `dict` subclass for scoring hashable items. It generalizes functionality of built-in `Counter` to floating-point numbers with full math operation support.


```python
from izy import Scorer

s1 = Scorer({'a': 1, 'b': 2, 'c': 5})
s1['d'] = 3

>>> s1
Scorer({c: 5, d: 3, b: 2, a: 1})

s2 = Scorer('abc', [-2, 3, 4])

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
>>> abs(s2))
Scorer({c: 4, b: 3, a: 2})

>>> round(s2/4, 1)
Scorer({c: 1.0, b: 0.8, a: -0.5})
```

Logical operators `&`, `|` apply element-wise min/max and they are also applicable to scalars. As `Scorer` is not a `set` or even `multiset` (like `Counter`), we don't refer to these as intersection and union, but the functionalities are still similar. 


```python
>>> abs(s1 & s2)      # ~ min (drops non-common items)
Scorer({c: 4, a: 2, b: 2})

>>> s1 & 2            # drops items with score less than 2
Scorer({c: 5, d: 3, b: 2})

>>> s1 | s2           # ~ max
Scorer({c: 5, b: 3, d: 3, a: 1})

```

> About the above warning, note that `(s1 | (s1 & s2))` gives the subset of `s1` which also exists in `s2`. You can use this to force math operations to return common items only.

And finally the ultimate goal of the `Scorer` is to sort its items according to scores and give us the `best`, `topk` (or `worst`, `bottomk`).


```python
>>> s1.best()           
('c', 5)

>>> s1.topk(3)           # alias to `s1.best` but more readable when you specify the number of items
[('c', 5), ('d', 3), ('b', 2)]

>>> s1.topk(-2)         # negative k means bottom k
[('a', 1), ('b', 2)]

>>> s1.ascending()   # prefer this to `best` or `topk` with special values of n or k (None, 0, inf)
[('a', 1), ('b', 2), ('d', 3), ('c', 5)]

>>> s1.median()         # if scorer length is even, lower median is returned
('b', 2)
```



# Decorators

Python `functools` is really interesting, but it really lacks some generally usefull   decorators. There are some sippets scattered around and in [PythonDecoratorLibrary](https://wiki.python.org/moin/PythonDecoratorLibrary), but I wanted to gather my favourites in a single package.

First, `@returns()` and `@yields()` make your function/generator return/yield `namedtuple`s to more pythonically access your function output. It also looks like an easy documentation to me (about the *meaning* of what function returns and not just the `type`).


```python
from izy import *

@returns(x='the input', plus_one='input + 1')
def myfunction(x):
    return x, x+1

@yields('a', 'a_doubled')
def mygenerator(x):
    for i in range(x):
        yield i, i*2

>>> myfunction(5)
myfunction_output(x=5, plus_one=6)

>>> myfunction(5).plus_one
6

>>> myfunction.__doc__
 Returns:
    x: the input
    plus_one: input + 1
```

`@returns_time()` calculates function runtime and returns it as a `datetime.timedelta` object. You can change time format to `milis` (`int`) or `seconds` (`float`). It returns a  `namedtuple` which you can rename with using `@returns`.


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
timed_output(output=None, time=datetime.timedelta(seconds=4, microseconds=701631))

>>> timed_milis(32)
timed_milis_output(output='done', milis=2297)
```

`@logs()` does what it says at three stages: before calling, after returning and on exceptions. You can control log level for each stage, log `to_file` using default logger (named after the function) or pass your own `logging.Logger`.


```python
import logging

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

@logs(before=logging.DEBUG, after=logging.INFO,
      to_file='logged.log', file_mode='a')
def logged(x, **kw):
    for i in range(1000000):
        x += i
  
>>> logged(1, key1=5, key2=7.2)
[2022-01-09 12:38:41][logged][DEBUG] - Function `logged` called with args: (1, key1=5, key2=7.2)
[2022-01-09 12:38:41][logged][INFO] - Function `logged` returned after 0:00:00.075534 with output: None
```


`@fix_this()` reminds you to fix something in a stronger way than a passive comment. It raises `UserWarning` at runtime and does this everytime :)



```python
@fix_this('It always prints ValueError, errors should be raised!')
def please(x):
    print('ValueError')
```

This one `@ignores()` exceptions you define (and returns `None`). Who knows when and why you need this? :) You can stack it on top of `@logs()` to be aware of ignored exceptions.  


```python
@ignores(ValueError, IndexError)
@logs()
def ignorer(x):
    for i in range(x):
        raise ValueError

>>> ignorer(5)    # no error raises, only logging it
[2022-01-09 12:38:41][ignorer][DEBUG] - Function `ignorer` called with args: (5)
[2022-01-09 12:38:41][ignorer][ERROR] - ValueError() raised in `ignorer` after 0:00:00.003514!
```

Want more useful exception handler? `@fallsback()` falls back on specified exception to predefined return value or another `callable`. For multiple exceptions, stack it like this:


```python
import math

@fallsback(ZeroDivisionError, float('inf'))
@fallsback(ValueError, lambda x: x**2)
def multifb(x):
    if x < 0:
        raise ValueError
    elif x == 0:
        raise ZeroDivisionError
    else:
      return 1 / math.sqrt(x)

>>> multifb(25)
0.2
>>> multifb(-5)   # falls back to callable
25
>>> multifb(0)     # falls back to value
inf
```

# Bidict
> If you already heard about (and used) the great [`bidict`](https://github.com/jab/bidict) package, you can simply skip this one as this is merely a minimal bidict for those in a hurry :).

The **Bidi**rectional **dict**ionary is an invertible one-to-one mapping (a bijection). Obviously both sides should be valid dictionary keys. Uniqueness in either side is preserved by removing previous confilcting pairs, without any warnings. 


```python
from izy import Bidict

bd = Bidict({'a': 1, 'b': 2, 'c': 5})

bd = Bidict([('a', 1), ('b', 2), ('c', 5)])

bd = Bidict(a=1, b=2, c=5)  # nothing special, just like dict()

>>> bd              # all above are quivalent to
Bidict({'a': 1, 'b': 2, 'c': 5})
```

This is how you would access the mapping, in the direct way or reversed:

```python
>>> bd.r     # or bd.reverse
{1: 'a', 2: 'b', 5: 'c'}
>>> bd['c']
5
>>> bd.r[5]
'c'
```

It is recommended to name the two directions of your `Bidict` to make your code more readable.


```python
bd = Bidict('char', 'id')           # or Bidict('char-id')
bd.update({'a': 1, 'b': 2, 'c': 5})

>>> bd
Bidict({'a': 1, 'b': 2, 'c': 5})

bd = Bidict(char=['a', 'b', 'c'], id=[1, 2, 5])
>>> bd
Bidict({'a': 1, 'b': 2, 'c': 5})

>>> bd.id['c']
5
>>> bd.char[5]
'c'

>>> bd.char2id['c']   # more expressive access
5
>>> bd.id2char[5]
'c'
```

On evey update, the `Bidict` makes sure that all values in both directions remain unique. This is done by removing every existing pair which has conflict with the new one (overwritig).


```python
bd.char[2] = 'c'  # two conflicting pairs ('b', 2), ('c', 5) are removed

>>> bd
Bidict({'a': 1, 'c': 2})
```

Not to mention that a `Bidict` and its reversed views (`bd.r` or other accessors) are still a `dict`.

```python
>>> isinstance(bd, dict)
True

>>> for char, id in bd.r.items():
        print(char, id)
1 a
2 c
```

# Regex

Here are some functions to help you create complex regular expressions. These functions are especially useful for some *hard-to-remember* and *hard-to-read* pattern syntaxes, like lookahead, lookbehind patterns.

```python
p = make_regex(
   following('then '),      # lookbehind
   charset('a-z '), '+',
   followed_by(r' end')     # lookahead
)

>>> p.pattern
'(?<=then )[a-z ]+(?= end)'

>>> p.search('if condition then do something end; etc')
<re.Match object; span=(18, 30), match='do something'>

p = make_regex(
   any_of('ali', 'hossein', 'javad'),
   '\s+',
   grouped(any_of('goodarzi', 'sharafi'), name='family')
)

>>> p.pattern
'(?:hossein|javad|ali)\s+(?P<family>(?:goodarzi|sharafi))'

>>> match = p.search('his name is hossein sharafi.')
>>> match
<re.Match object; span=(12, 27), match='hossein sharafi'>

>>> match.group('family')
'sharafi'
```

# Head

This simple function `head()` gives you a brief insight about the structure and contents of a possible large and nested python data object. The key use case is when you load a large `.json` file for the first time in a jupyter notebook.

```python
x = [
   (1, 2, 3, 4),
   {1: range(3), 2: range(2, 40, 2), 5: 6, 7: 8},
   range(1000),
   (7, 8, 9, 10),
   *range(10)
]

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
```

# Table

If you have a small tabular data and you don't want to install `numpy`, `pandas` just to handle it, here is the thing for you. The `Table` is a simple pure-python container for tabular data:

```python
# create table using dict of lists (columns)
data = {
   'a': [3, 5, 21638540, 'very-loong-value'],
   'b': [16, 8, 0, 1],
   'c': [0, 5, 6, None],
   }
table = Table(data)

>>> print(table.draw())
a               b    c      
============================
3               16   0      
5               8    5      
21638540        0    6      
very-loong-va.. 1    None

# ... or a list of dicts (rows)
data = [
   {'a': 3, 'b': 16, 'c': 0},
   {'a': 5, 'b': 8, 'c': 5},
   {'a': 21638540, 'b': 0, 'c': 6},
   {'b': 1, 'a': 'very-loong-value'},
   ]
table = Table(data)

>>> print(table.draw())
a               b    c      
============================
3               16   0      
5               8    5      
21638540        0    6      
very-loong-va.. 1    None
```

You can easily access columns, rows, or a slice of the table:

```python
>>> table['b']      # access table columns (by str key)
[16, 8, 0, 1]

>>> table[2]        # access table rows (by int key)
{'a': 21638540, 'b': 0, 'c': 6}

>>> table[1:3]      # or get a slice of table
a          b   c   
===================
5          8   5   
21638540   0   6
```
Concatenate tables:
```python
>>> table[:2] + table[2:]
a               b    c      
============================
3               16   0      
5               8    5      
21638540        0    6      
very-loong-va.. 1    None
```
And manipulate table data:
```python
# add/change a column
>>> table['d'] = [0] * len(table)
>>> table
a               b    c      d   
================================
3               16   0      0   
5               8    5      0   
21638540        0    6      0   
very-loong-va.. 1    None   0

# manipulate table rows
>>> table[1] = {'a': 5, 'b': 55, 'c': 555}
>>> table.append({'b': 66, 'c': 666})
>>> table
a               b    c      d      
===================================
3               16   0      0      
5               55   555    None   
21638540        0    6      0      
very-loong-va.. 1    None   0      
None            66   666    None
```

`csv` read/write is alse there:
```python
>>> table.to_csv('output.tsv')
>>> Table.from_csv('output.tsv')
a               b    c      d      
===================================
3               16   0      0      
5               55   555    None   
21638540        0    6      0      
very-loong-va.. 1    None   0      
None            66   666    None
```

# Path

Yet another `path` operations toolkit along with `pathlib`, `path.py`. This one is based on the standard `pathlib` and shares most of advantages of `path.py`. What makes it different is the convenient *method-chaining* api, and its file read/write methods.

```python
d = Path('path/to').mkdir()
p = (d / 'file').with_suffix('.txt').touch()

>>> p.copy(d / 'copy.txt').name
'copy.txt'

>>> len(d.glob('*.txt'))
2
>>> d.parent.rmdir(recursive=True).exists()
False
```

`FilePath` is a `Path` which handles some file read/write operations which are not relevant to a Path.

```python
f = FilePath('path/to', 'file.txt')

>>> f.mkdir().write_text('hello world!').read_text()
'hello world!'

>>> f.print({'x': 4, 'y':5}).aprint({'x': 6, 'y':7}).get_size()
36

>>> print(f.read_text())
{'x': 4, 'y': 5}
{'x': 6, 'y': 7}

>>> f.pickle({'x': 4, 'y': 5}).pickle({'x': 6, 'y': 7}, append=True).unpickle()
[{'x': 4, 'y': 5}, {'x': 6, 'y': 7}]
```
Read/write operations for `json` and `csv` (using `izy.Table`) are also available.
