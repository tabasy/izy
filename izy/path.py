"""Path utils with focus on ease-of-use and method-chaining.
"""

import os
import json
import pickle
import shutil
import pprint
import pathlib
import tempfile
from typing import Any, Dict, List, Union


try:
    from .table import Table
except:
    class Table:
        ...


__all__ = ['Path', 'FilePath', 'TempFilePath']


class Path(str):
    """String-like path with path-related methods, focused on method-chaining.
    Methods return the path-itself when there is no other explicit return value.
    Internally, a `pathlib.Path` is used to invoke most of the operations.

    >>> d = Path('path/to').mkdir()
    >>> p = (d / 'file').with_suffix('.txt').touch()
    >>> p.copy(d / 'copy.txt').name
    'copy.txt'

    >>> len(d.glob('*.txt'))
    2
    >>> d.parent.rmdir(recursive=True).exists()
    False
    """

    def __new__(cls, *args, **kwargs):
        # explicitly only pass value to the str constructor
        path = pathlib.Path(*args)
        return super(Path, cls).__new__(cls, path)

    def __init__(self, *args, **kwargs):
        # ... and don't even call the str initializer
        self._path = pathlib.Path(*args)

    @classmethod
    def cwd(cls):
        """Return a new path pointing to the current working directory
        (as returned by os.getcwd()).
        """
        return cls(pathlib.Path.cwd())

    @classmethod
    def home(cls):
        """Return a new path pointing to the user's home directory (as
        returned by os.path.expanduser('~')).
        """
        return cls(pathlib.Path.home())

    @property
    def name(self):
        """A string representing the final path component, excluding the drive and root, if any"""
        return self.__class__(self._path.name)

    @property
    def suffix(self):
        """The file extension of the final component, if any"""
        return self._path.suffix

    @property
    def stem(self):
        """The final path component, without its suffix"""
        return self._path.stem

    @property
    def parent(self):
        """The logical parent of the path. Note that this is a purely lexical operation"""
        return self.__class__(self._path.parent)

    @property
    def drive(self):
        """A string representing the drive letter or name, if any"""
        return self._path.drive

    @property
    def root(self):
        """A string representing the (local or global) root, if any"""
        return self.__class__(self._path.root)

    @property
    def anchor(self):
        """The concatenation of the drive and root"""
        return self.__class__(self._path.anchor)

    extension = suffix

    # Path manipulation

    def absolute(self):
        """Return an absolute version of this path.  This function works
        even if the path doesn't point to anything.

        No normalization is done, i.e. all '.' and '..' will be kept along.
        Use resolve() to get the canonical path to a file.
        """
        return self.__class__(self._path.absolute())

    def resolve(self, strict=False):
        """
        Make the path absolute, resolving all symlinks on the way and also
        normalizing it (for example turning slashes into backslashes under
        Windows).
        """
        return self.__class__(self._path.resolve(strict))

    def readlink(self):
        """
        Returns the path to which the symbolic link points.
        """
        return self.__class__(self._path.readlink())

    def relative_to(self, other):
        """
        Compute a version of this path relative to the path represented by other.
        """
        return self.__class__(self._path.relative_to(other))

    def join(self, *paths):
        """
        Calling this method is equivalent to combining the path with each of the other arguments in turn.
        """
        return self.__class__(self._path.joinpath(*paths))

    def with_suffix(self, suffix):
        """Returns a new path with the suffix changed. If the original path doesn’t have a suffix,
        the new suffix is appended instead. If the suffix is an empty string, the original suffix is removed"""
        return self.__class__(self._path.with_suffix(suffix))

    def with_name(self, name):
        """Returns a new path with the name changed. If the original path doesn’t have a name, ValueError is raised"""
        return self.__class__(self._path.with_name(name))

    def with_stem(self, name):
        """Returns a new path with the stem changed. If the original path doesn’t have a name, ValueError is raised"""
        return self.__class__(self._path.with_stem(name))

    def with_dir(self, parent_dir):
        """Returns a new path with the parent dir changed."""
        return self.__class__(parent_dir / self.name)

    with_ext = with_suffix

    # Magic methods

    def __truediv__(self, other):
        return self.__class__(self._path / other)

    def __rtruediv__(self, other):
        return self.__class__(other / self._path)

    def __floordiv__(self, other):
        return self.with_dir(other)

    # File/Directory operations

    def touch(self, mode=0o666, exist_ok=True):
        """
        Create this file with the given access mode, if it doesn't exist.
        """
        self._path.touch(mode, exist_ok)
        return self

    def unlink(self, missing_ok=False):     # file or link
        """
        Remove this file or link.
        If the path is a directory, use rmdir() instead.
        """
        self._path.unlink(missing_ok)
        return self

    def rename(self, target, replace=False):
        """
        Rename this path to the target path.

        The target path may be absolute or relative. Relative paths are
        interpreted relative to the current working directory, *not* the
        directory of the Path object.

        Returns the new Path instance pointing to the target path.
        """
        if replace:
            return self.__class__(self._path.replace(target))

        return self.__class__(self._path.rename(target))

    def remove(self, recursive=False, missing_ok=True):
        """Removes both files, directories and even non-empty directory along with its 
        contents (Not default).

        Args:
            recursive (bool, optional): Remove non-empty dir with its contents?. Defaults to False.
            missing_ok (bool, optional): Ignore missing file or dir?. Defaults to True.

        Raises:
            FileNotFoundError: if path does not exist and `missing_ok` is False.

        Returns:
            The path itself.
        """
        if self.is_file():
            return self.unlink()
        elif self.is_dir():
            return self.rmdir(recursive=recursive)
        elif not missing_ok:
            raise FileNotFoundError(
                f'The file or dir `{self}` does not exist!')

    def copy(self, dst, **kwargs):
        """Copy file or directory to the destination.
        If the path is a file `shutil.copy2()` is used, else `shutil.copytree` copies the entire directory.
        """

        if self.is_file():
            return self.__class__(shutil.copy2(self, dst, **kwargs))
        else:
            shutil.copytree(self, dst, **kwargs)

        return self.__class__(dst)

    def rmdir(self, recursive=False):
        """
        Remove this directory.  If the directory is not empty, passing
        `recursive=True` means remove this with its contents.
        """
        if recursive:
            shutil.rmtree(self)
        else:
            self._path.rmdir()
        return self

    def mkdir(self, mode=0o777, parents=True, exist_ok=True):
        """
        Create a new directory at this given path.
        """
        self._path.mkdir(mode, parents, exist_ok)
        return self

    makedirs = mkdir

    # Symbolic link operations

    def symlink_to(self, target, target_is_directory=False):
        """
        Make this path a symlink pointing to the target path.
        Note the order of arguments (link, target) is the reverse of os.symlink.
        """
        self._path.symlink_to(target, target_is_directory)
        return self

    def hardlink_to(self, target):
        """
        Make the target path a hard link pointing to this path.

        Note this function does not make this path a hard link to *target*,
        despite the implication of the function and argument names. The order
        of arguments (target, link) is the reverse of Path.symlink_to, but
        matches that of os.link.
        """
        self._path.link_to(target)
        return self

    symlink = symlink_to
    link = hardlink_to

    # Path queries (neither changes path string nor files, dirs)
    # returns non-Path objects

    def match(self, pattern):
        """Match this path against the provided glob-style pattern"""
        return self._path.match(pattern)

    def same(self, other_path):
        """Return whether other_path is the same or not as this file
        (as returned by os.path.samefile()).
        """
        return self._path.samefile(other_path)

    def chmod(self, mode):
        """
        Change the permissions of the path, like os.chmod().
        """
        self._path.chmod(mode)
        return self

    def lchmod(self, mode):
        """
        Like chmod(), except if the path points to a symlink, the symlink's
        permissions are changed, rather than its target's.
        """
        self._path.lchmod(mode)
        return self

    def exists(self):
        """
        Whether this path exists.
        """
        return self._path.exists()

    def stat(self):
        """
        Return the result of the stat() system call on this path, like
        os.stat() does.
        """
        return self._path.stat()

    def is_dir(self):
        """
        Whether this path is a directory.
        """
        return self._path.is_dir()

    def is_file(self):
        """
        Whether this path is a regular file (also True for symlinks pointing
        to regular files).
        """
        return self._path.is_file()

    def is_mount(self):
        """
        Check if this path is a POSIX mount point
        """
        # Need to exist and be a dir
        return self._path.is_mount()

    def is_symlink(self):
        """
        Whether this path is a symbolic link.
        """
        return self._path.is_symlink()

    def is_block_device(self):
        """
        Whether this path is a block device.
        """
        return self._path.is_block_device()

    def is_char_device(self):
        """
        Whether this path is a character device.
        """
        return self._path.is_char_device()

    def is_fifo(self):
        """
        Whether this path is a FIFO.
        """
        return self._path.is_fifo()

    def is_socket(self):
        """
        Whether this path is a socket.
        """
        return self._path.is_socket()

    def get_size(self, recursive=True):
        """Returns file size in bytes and if the path is a directory,
        (recursively) calculates sum of all file """
        if self.is_file():
            return self.stat().st_size

        file_paths = self.rglob('*') if recursive else self.listdir()

        return sum(f.stat().st_size for f in file_paths if f.is_file())

    matches = match
    isdir = is_dir
    isfile = is_file
    islink = is_symlink
    isfile = is_file
    isfile = is_file

    def owner(self):
        """
        Return the login name of the file owner.
        """
        return self._path.owner()

    def group(self):
        """
        Return the group name of the file gid.
        """
        return self._path.group()

    def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        """
        Open the file pointed by this path and return a file object, as
        the built-in open() function does.
        """
        return self._path.open(mode, buffering=buffering, encoding=encoding,
                               errors=errors, newline=newline)

    # Directory exploring

    def iterdir(self):
        """Iterates over the child paths in this directory.  Does not 
        yield any result for the special paths '.' and '..'.
        """
        return (self.__class__(p) for p in self._path.iterdir())

    def listdir(self):
        """Lists the child paths in this directory.  Does not yield any
        result for the special paths '.' and '..'.
        """
        return [self.__class__(p) for p in self._path.iterdir()]

    def glob(self, pattern):
        """Iterate over this subtree and yield all existing files (of any
        kind, including directories) matching the given relative pattern.
        """
        return [self.__class__(p) for p in self._path.glob(pattern)]

    def rglob(self, pattern):
        """Recursively yield all existing files (of any kind, including
        directories) matching the given relative pattern, anywhere in
        this subtree.
        """
        return [self.__class__(p) for p in self._path.rglob(pattern)]


class FilePath(Path):
    """Handles file read/write operations which are not relevant to a Path.

    >>> f = FilePath('path/to', 'file.txt')
    >>> f.mkdir().write_text('hello world!').read_text()
    'hello world!'
    >>> f.print({'x': 4, 'y':5}).aprint({'x': 6, 'y':7}).get_size()
    36
    >>> print(f.read_text())
    {'x': 4, 'y': 5}
    {'x': 6, 'y': 7}
    <BLANKLINE>

    >>> f.pickle({'x': 4, 'y': 5}).pickle({'x': 6, 'y': 7}, append=True).unpickle()
    [{'x': 4, 'y': 5}, {'x': 6, 'y': 7}]

    # and so on for `json` and `csv`
    """

    def mkdir(self, mode=0o777, parents=True, exist_ok=True):
        """Make parent directory for the file path.
        """
        Path(self.parent).mkdir(mode=mode, parents=parents, exist_ok=exist_ok)
        return self

    makedirs = mkdir

    def read_bytes(self):
        """
        Open the file in bytes mode, read it, and close the file.
        """
        return self._path.read_bytes()

    def read_text(self, encoding=None, errors=None):
        """
        Open the file in text mode, read it, and close the file.
        """
        return self._path.read_text(encoding, errors)

    def write_bytes(self, data):
        """
        Open the file in bytes mode, write to it, and close the file.
        """
        # type-check for the buffer interface before truncating the file
        self._path.write_bytes(data)
        return self

    def write_text(self, data, encoding=None, errors=None):
        """
        Open the file in text mode, write to it, and close the file.
        """
        self._path.write_text(data, encoding, errors)
        return self

    def readlines(self, n=None) -> List[str]:
        return list(self.ireadlines(n))

    def ireadlines(self, n=None):
        with self.open(mode='r') as f:
            for i, line in enumerate(f):
                if n is not None and i == n:
                    break
                yield line

    def print(self, *objs, pretty=True, **kwargs):
        with open(self, 'w') as f:
            if pretty:
                for obj in objs:
                    pprint.pprint(obj, stream=f, **kwargs)
            else:
                print(*objs, sep='\n', file=f, flush=True)
        return self

    def append_print(self, *objs, pretty=True, **kwargs):
        with open(self, 'a') as f:
            if pretty:
                for obj in objs:
                    pprint.pprint(obj, stream=f, **kwargs)
            else:
                print(*objs, sep='\n', file=f, flush=True)
        return self

    aprint = append_print

    def dump_pickle(self, obj, append=False, **kwargs):
        mode = 'a+b' if append else 'wb'
        with open(self, mode) as f:
            pickle.dump(obj, f, **kwargs)
        return self

    def dump_pickles(self, *objects, append=False, **kwargs):
        mode = 'a+b' if append else 'wb'
        with open(self, mode) as f:
            for obj in objects:
                pickle.dump(obj, f, **kwargs)
        return self

    def iload_pickle(self, **kwargs) -> Any:
        with open(self, 'rb') as f:
            while True:
                try:
                    yield pickle.load(f, **kwargs)
                except (EOFError, IOError):
                    break

    def load_pickle(self, **kwargs) -> Any:
        return list(self.iload_pickle(**kwargs))

    pickle = dump_pickle
    unpickle = load_pickle

    def dump_json(self, obj, **kwargs):
        with open(self, 'w') as f:
            json.dump(obj, f, **kwargs)
        return self

    def load_json(self, **kwargs) -> Any:
        with open(self, 'r') as f:
            return json.load(f, **kwargs)

    def read_csv(self, sep=',', header=True, missing_value=None) -> Table:
        """Read path as csv file and return data as `izy.table.Table`.

        Args:
            sep (str, optional): Separator (delimiter) character. Defaults to ','.
            header (bool, optional): Whether or not to use first row as header. Defaults to True.
            missing_value (Any, optional): The value to replace empty row fileds. Defaults to None.

        Returns:
            izy.table.Table: The csv data
        """
        return Table.from_csv(self, sep=sep, header=header, missing_value=missing_value,)

    def write_csv(self, table: Union[Table, List, Dict], sep=',', header=True):
        """Write tabular data into path as csv file and return the path.

        Args:
            table (Union[Table, List, Dict]): Tabular data. Can be an `izy.table.Table` or 
                any data acceptable for `Table` constructor.
            sep (str, optional): Separator (delimiter) character. Defaults to ','.
            header (bool, optional): Whether or not to use first row as header. Defaults to True.
        """
        if not isinstance(table, Table):
            table = Table(table)
        table.to_csv(self, sep=sep, header=header)
        return self

    def append_csv(self, table, sep=','):
        """Append tabular data into path as csv file and return the path.

        Args:
            table (Union[Table, List, Dict]): Tabular data. Can be an `izy.table.Table` or 
                any data acceptable for `Table` constructor.
            sep (str, optional): Separator (delimiter) character. Defaults to ','.
            header (bool, optional): Whether or not to use first row as header. Defaults to True.
        """
        if not isinstance(table, Table):
            table = Table(table)
        table.append_to_csv(self, sep=sep)
        return self


class TempFilePath(FilePath):
    """Path to a temporary file. If the file is created, it will
    be removed after this path is removed by garbage collector.
    """

    def __new__(cls, dir=None, prefix=None, suffix=None):
        # explicitly only pass value to the str constructor
        fd, path = tempfile.mkstemp(dir=dir, prefix=prefix, suffix=suffix)
        os.close(fd)
        path = pathlib.Path(path)
        return super(Path, cls).__new__(cls, path)

    def __init__(self, *args, **kwargs):
        # ... and don't even call the str initializer
        self._path = pathlib.Path(self)

    def __del__(self):
        if self.exists():
            self.unlink()


if __name__ == '__main__':

    import doctest
    doctest.testmod()
