import re
from typing import Iterable, List, Mapping, MutableMapping, MutableSequence, Sequence


class Boundict(dict):
    """
    A `Bound` `dict`ionary is bound to a peer which acts as its reverse.
    """
    def __init__(self, peer=None):
        self.peer = peer
        if peer is not None:
            peer.bind(self)
        return super().__init__()

    @staticmethod
    def create_pair():
        a = Boundict()
        b = Boundict(peer=a)
        return a, b

    def bind(self, peer):
        self.peer = peer
        for k, v in self.items():
            super(Boundict, self.peer).__setitem__(v, k)
    
    def __setitem__(self, k, v) -> None:
        if k in self and self[k] != v:
            self.__delitem__(k)
        if v in self.peer and self.peer[v] != k:
            self.peer.__delitem__(v)

        super(Boundict, self).__setitem__(k, v)
        super(Boundict, self.peer).__setitem__(v, k)

    def __delitem__(self, k) -> None:
        super(Boundict, self.peer).__delitem__(self[k])
        super(Boundict, self).__delitem__(k)

    def update(self, other, **kv):        

        new_items = other.items() if isinstance(other, Mapping) else other

        for k, v in new_items:
            self[k] = v
        for k, v in kv.items():
            self[k] = v


class Bidict(Boundict):
    """
    `Bidi`rectional `dict`ionary is an invertible one-to-one mapping (a bijection).
    Obviously both sides should be valid dictionary keys. Uniqueness in either side
    is preserved by removing previous confilctig pairs, without any warnings.

    >>> bd = Bidict()                   # default key names ('direct', 'reverse')
    >>> bd = Bidict('word', 'id')       # custom key names ('word', 'id') 
    >>> bd = Bidict('word-id') 

    >>> bd = Bidict({'salam':0, 'aziam':1, 'khoobi':2})     # default key names
    >>> bd = Bidict(salam=0, aziam=1, khoobi=2)
    >>> bd = Bidict([('salam', 0), ('azizam', 1), ('khoobi', 2)])

    # custom key names
    >>> bd = Bidict(word=['salam', 'azizam', 'khoobi'], id=[0, 1, 2])

    >>> bd['salam'] = 1     # two conflicting pairs ('salam', 0), ('azizam', 1) are removed

    >>> bd.id['salam']      # == bd['salam']
    1
    
    # or more expressive   
    >>> bd.word2id['salam'] 
    1

    >>> bd.word[1]          # == bd.r[1] == bd.id2word[1]
    'salam'

    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.r = Boundict(peer=self)

        key_name, value_name = 'reverse', 'direct'

        if len(args) == 1:
            arg = args[0]
            # Bidict('word-id')
            if isinstance(arg, str) and arg.count('-') == 1:
                key_name, _,value_name = arg.partition('-')
            # Bidict({'salam':0, 'aziam':1, 'khoobi':2})
            elif isinstance(arg, Mapping):
                self.update(args[0])
            # Bidict([('salam', 0), ('azizam', 1), ('khoobi', 2)])
            elif isinstance(arg, Sequence):
                self.update(dict(args[0]))
            else:
                raise ValueError('Invalid arguments. Expected one of:'\
                '\nstr containing exactly one "-" e.g. "word-id"'
                '\nMapping'
                '\nSequence'
            )
        # Bidict('word', 'id')
        elif len(args) == 2:
            if all(isinstance(arg, str) for arg in args):
                key_name, value_name = args
            else:
                raise ValueError('Invalid arguments. In case of having two positional arguments, '\
                    'both sould be strings which can be valid variable names e.g. "word", "id".')

        elif len(args) > 2:
            raise ValueError('Invalid arguments. Expected at most two positional arguments.')

        # Bidict(words)
        if len(kwargs) == 2 and all(isinstance(v, MutableSequence) for v in kwargs.values()):
            # MutableSequence is not valid as key/value for bidict
            key_name, value_name = kwargs.keys()
            keys, values = kwargs.values()
            self.update(zip(keys, values))
        else:
            self.update(kwargs)

        setattr(self, 'd', self)
        setattr(self, 'r', self.r)
        setattr(self, value_name, self)         # self.word[*] is supposed to return a word
        setattr(self, key_name, self.r)         # self.id[*] is supposed to return an id

        if key_name != 'direct' and value_name != 'reverse':
            setattr(self, f'{key_name}2{value_name}', self)
            setattr(self, f'{value_name}2{key_name}', self.r)

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        dict_repr = super().__repr__()
        return f'{self.__class__.__name__}({dict_repr})'


# class Redict(Bidict):
#     """`Re`versible `dict`ionary is `Bidict` with easier reversed access.
#     Do not use this if direct and reverse values can be equal (e.g. both are numbers). 
#     """
#     def __getitem__(self, k) -> None:
#         if k in self:
#             return super().__getitem__(k)
#         return self.r.__getitem__(k)

#     def __delitem__(self, k) -> None:
#         if k in self:
#             super().__delitem__(k)
#         else:
#             self.r.__delitem__(k)


if __name__ == '__main__':
    print('\n------------ Bidict ------------')
    
    # print(f"{Bidict() = }")
    # print(f"{Bidict('word', 'id') = }")
    # print(f"{Bidict('word-id') = }")
    # print(f"{Bidict({'salam':0, 'aziam':1, 'khoobi':2}) = }")
    # print(f"{Bidict(salam=0, aziam=1, khoobi=2) = }")
    # print(f"{Bidict([('salam', 0), ('azizam', 1), ('khoobi', 2)]) = }")
    # print(f"{Bidict(word=['salam', 'azizam', 'khoobi'], id=[0, 1, 2]) = }\n")
    
    # bd = Bidict(word=['salam', 'azizam', 'khoobi'], id=[0, 1, 2])
    # bd.id['salaam'] = 0
    # print(">>> bd.id['salaam'] = 0")
    # # bd.word[1] = 'azizam'
    # # bd.word[-1] = '<unk>'
    # print(f'{bd = }')
    # print(f'{bd.d = }')
    # print(f'{bd.r = }')
    
    # bd.id[1] = 'khoobi?'
    # print(f'{bd = }')
    # print(f'{bd.id2word = }')
    # print(f'{bd.word = }')

    # print(exec_doc(Bidict.__doc__))

    # print('\n------------ Redict ------------')
    # rd = Redict()
    # rd['salaam'] = 0
    # rd[1] = 'azizam'
    # rd[-1] = '<unk>'
    # print(f'{rd = }')
    # print(f'{rd[1] = }')
    # print(f'{rd["azizam"] = }')
    
    # rd[1] = 'khoobi?'
    # print(f'{rd = }')
    
    # del rd['khoobi?']
    # print(f'{rd = }')