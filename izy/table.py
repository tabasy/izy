import csv
from copy import deepcopy
from typing import Any, Dict, List, Union


class Table:
    """Simple pythonic container for tabular data.
    
    # create table
    >>> data = {
    ...    'a': [3, 5, 21638540, 'very-loong-value'],
    ...    'b': [16, 8, 0, 1],
    ...    'c': [0, 5, 6, None],
    ...    }
    >>> table = Table(data)
    >>> print(table.draw())
    a               b    c      
    ============================
    3               16   0      
    5               8    5      
    21638540        0    6      
    very-loong-va.. 1    None
    
    >>> data = [
    ...    {'a': 3, 'b': 16, 'c': 0},
    ...    {'a': 5, 'b': 8, 'c': 5},
    ...    {'a': 21638540, 'b': 0, 'c': 6},
    ...    {'b': 1, 'a': 'very-loong-value'},
    ...    ]
    >>> table = Table(data)
    >>> print(table.draw())
    a               b    c      
    ============================
    3               16   0      
    5               8    5      
    21638540        0    6      
    very-loong-va.. 1    None
    
    # access columns, rows
    >>> table['b']      # access table columns (by str key)
    [16, 8, 0, 1]
    
    >>> table[2]        # access table rows (by int key)
    {'a': 21638540, 'b': 0, 'c': 6}
    
    >>> table[1:3]      # or get a slice of table
    a          b   c   
    ===================
    5          8   5   
    21638540   0   6
    
    # concatenate two tables
    >>> table[:2] + table[2:]
    a               b    c      
    ============================
    3               16   0      
    5               8    5      
    21638540        0    6      
    very-loong-va.. 1    None
    
    # manipulate table columns
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
    
    # csv read/write
    >>> table.to_csv('output.tsv')
    >>> Table.from_csv('output.tsv')
    a               b    c      d      
    ===================================
    3               16   0      0      
    5               55   555    None   
    21638540        0    6      0      
    very-loong-va.. 1    None   0      
    None            66   666    None
    """

    MAX_COL_WIDTH = 16

    def __init__(self, data: Union[List[Dict[str, Any]], Dict[str, List]]) -> None:
        if isinstance(data, dict):
            self.check_cols(data)
            self.cols = data
        elif isinstance(data, list):
            self.cols = {}
            self.cols_from_rows(data)
        else:
            raise ValueError(
                'the `data` must be either a list of dicts (rows) or a dict of lists (cols).')

    @classmethod
    def check_cols(cls, cols):
        lengths = [len(col) for col in cols.values()]
        if len(set(lengths)) != 1:
            raise ValueError(
                f'All table columns must have the same lengths. Column lengths: {lengths}')

    def cols_from_rows(self, rows):
        """Converts list of dicts (rows) to dict of lists (cols), 
        fills missing values with `None`.

        Args:
            rows (List[Dict[str, Any]]): Table rows

        Returns:
            (Dic[str, List]): The dict of lists (cols).
        """
        rows = list(rows)
        col_names = []
        for row in rows:
            col_names.extend(row.keys())

        self.cols = {c: [] for c in dict.fromkeys(col_names)}

        for row in rows:
            self.append(row)

    def row_at(self, index):
        return {name: col[index] for name, col in self.cols.items()}

    def append(self, row):
        for c in self.cols:
            self.cols[c].append(row.get(c))

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.cols[key]
        if isinstance(key, int):
            return self.row_at(key)
        if isinstance(key, slice):
            sliced_data = {c: col[key] for c, col in self.cols.items()}
            return self.__class__(data=sliced_data)
        if isinstance(key, list):
            sliced_data = {c: self.cols[c] for c in key}
            return self.__class__(data=sliced_data)
        raise ValueError(
            'Invalid key. It should be `str` or `List[str]` to access column(s), `int` or `slice` to return row(s).')

    def __setitem__(self, key, value):
        
        if isinstance(key, str):
            if len(value) != len(self):
                raise ValueError(
                    f'New columns values must have the same length with existing cols. {len(value)} != {len(self)}')
            self.cols[key] = value
            
        elif isinstance(key, int):
            if not isinstance(value, dict):
                raise ValueError(f'New row should be a dict with string keys.')
            for c in self.cols:
                self.cols[c][key] = value.get(c)
        else:
            raise ValueError(
                'Invalid key. It should be `str` to set columns or `int` to edit rows.')

    def __len__(self):
        a_col = next(iter(self.cols.values()))
        return len(a_col)

    def __iter__(self):
        for idx in range(len(self)):
            yield self.row_at(idx)

    def draw(self, n_rows=5):

        c2len = {}

        for c, col in self.cols.items():
            lengths = map(len, map(str, col[:n_rows]))
            max_len = max([len(c), *lengths]) + 3
            c2len[c] = min(max_len, self.MAX_COL_WIDTH)

        # header
        result = ''.join([c.ljust(c2len[c]) for c in self.cols]) + '\n'
        result += '=' * sum(c2len.values()) + '\n'

        # rows
        for i, row in enumerate(self):
            if i >= n_rows:
                break
            for c in self.cols:
                str_value = str(row[c])
                if len(str_value) > c2len[c] - 1:
                    str_value = str_value[:c2len[c] - 3] + '..'
                result += str_value.ljust(c2len[c])
            result += '\n'

        return result.strip()

    def __str__(self) -> str:
        return self.draw()

    def __repr__(self) -> str:
        return self.draw()
    
    def copy(self):
        return deepcopy(self)
    
    def __add__(self, other):
        first = self.copy()
        first.extend(other)
        return first
        
    def extend(self, other):
        if type(other) is not type(self):
            try:
                fata = self.__class__(other)
            except:
                raise ValueError('Provide a `Table` or valid data for `Table` constructor.')
        
        if self.cols.keys() != other.cols.keys():
            raise ValueError('The `data` must have the same columns as the source table.')
        
        for c, col in self.cols.items():
            col.extend(other[c])
    
    concat = extend

    def to_csv(self, path, sep=',', header=True, **kwargs):

        with open(path, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file,
                                    fieldnames=list(self.cols.keys()),
                                    delimiter=sep, **kwargs)
            if header:
                writer.writeheader()
            for row in self:
                writer.writerow(row)
                
    def append_to_csv(self, path, sep=',', **kwargs):

        with open(path, mode='a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file,
                                    fieldnames=list(self.cols.keys()),
                                    delimiter=sep, **kwargs)
            for row in self:
                writer.writerow(row)
                
    @staticmethod
    def from_csv(path, sep=',', header=True,
                 missing_value=None, transform=None, **kwargs):

        cols = {}

        if transform is None:
            def transform(s): return s

        with open(path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=sep, **kwargs)
            for i, row in enumerate(csv_reader):
                if i == 0:
                    if header:
                        cols.update({c: [] for c in row})
                        continue
                    else:
                        cols.update({i: [] for i in range(len(row))})
                for c, v in zip(cols, row):
                    cols[c].append(transform(v) if v != '' else missing_value)

        return Table(data=cols)


if __name__ == '__main__':
    
    import doctest
    doctest.testmod(verbose=True)

