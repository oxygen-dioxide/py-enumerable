import itertools
import inspect
import io
from dataclasses import dataclass
from typing import (
    TypeVar,
    Any,
    Iterable,
    Iterator,
    Optional,
    Generic,
    Callable,
)
from copy import deepcopy

T = TypeVar("T")
TKey = TypeVar("TKey")


@dataclass
class Node(Generic[T]):
    """
    Node for linked list
    """

    value: T
    next: "Optional[Node[T]]" = None


class Key(object):
    def __init__(self, key, **kwargs):
        """
        Constructor for Key class. Autogenerates key properties in object
        given dict or kwargs
        :param key: dict of name-values
        :param kwargs: optional keyword arguments
        :return: void
        """
        key = key if key is not None else kwargs
        self.__dict__.update(key)

    def __repr__(self):
        return self.__dict__.__repr__()


class OrderingDirection(Generic[T, TKey]):
    def __init__(self, key: Callable[[T], TKey], reverse: bool) -> None:
        """
        A container to hold the lambda key and sorting direction
        :param key: lambda function
        :param reverse: boolean. True for reverse sort
        """
        self.key = key
        self.descending = reverse


class RepeatableIterable(Generic[T]):
    def __init__(self, data: Iterable[T] | None = None):
        """
        Constructor. Pretty straight forward except for the is_generator check. This is so we
        can detect when a function that generates data is passed as a datasource. In this case we
        need to exhaust the values in the function generator
        """
        if data is None:
            data = []
        if not hasattr(data, "__iter__"):
            raise TypeError(
                "RepeatableIterable must be instantiated with an iterable object"
            )
        self._data: Iterable[T] = data
        self._len: int | None = None
        self._root: Node[T] | None = None
        self._current: Node[T] | None = None

    def __len__(self) -> int:
        if self._len is None:
            self._len = sum(1 for item in iter(self))
        return self._len

    def __reversed__(self) -> Iterator[T]:
        if not isinstance(self._data, list):
            # We need to collect the data from a generator since reversing a generator
            # is not possible
            self._data = list(self._data)
        if self._root is None:
            i = 0
            for index, item in enumerate(reversed(self._data)):
                node = Node(value=item)
                if self._current is None:
                    self._root = node
                    self._current = self._root
                else:
                    self._current.next = node
                    self._current = self._current.next
                yield node.value
                i += 1
            self._len = i
        else:
            while self._current is not None:
                yield self._current.value
                self._current = self._current.next
        self._current = self._root

    def __iter__(self) -> Iterator[T]:
        if self._root is None:
            i = 0
            for index, item in enumerate(self._data):
                node = Node(value=item)
                if self._current is None:
                    self._root = node
                    self._current = self._root
                else:
                    self._current.next = node
                    self._current = self._current.next
                yield node.value
                i += 1
            self._len = i
        else:
            while self._current is not None:
                yield self._current.value
                self._current = self._current.next
        self._current = self._root

    def __next__(self) -> T:
        if self._current is None:
            raise StopIteration
        if self._current.next is None:
            self._current = self._root
            raise StopIteration
        self._current = self._current.next
        return self._current.value

    @property
    def current(self) -> Optional[Node[T]]:
        return self._current

    @current.setter
    def current(self, node: Node[T]) -> None:
        self._current = node

    @property
    def head(self) -> Optional[Node[T]]:
        return self._root

    @head.setter
    def head(self, node: Node[T]) -> None:
        self._root = node

    def next(self):
        return self.__next__()
