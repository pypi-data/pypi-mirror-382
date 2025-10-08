from typing import TypeVar, Generic, Dict, Set, List, Optional, Iterable

MultiMapKey = TypeVar('MultiMapKey')
MultiMapValue = TypeVar('MultiMapValue')


class SetMultimap(Generic[MultiMapKey, MultiMapValue]):
    """
    A multimap based on a mutable set for duplication of values.
    """
    _store: Dict[MultiMapKey, Set[MultiMapValue]]

    def __init__(self, store: Dict[MultiMapKey, Set[MultiMapValue]] = None):
        if not store:
            store = dict()
        self._store = store

    def __copy__(self):
        new_store = self._store.copy()
        return SetMultimap(new_store)

    def has_key(self, key: MultiMapKey) -> bool:
        """
        Tests whether the current multimap includes this key.
        """
        return key in self._store

    def has_item(self, key: MultiMapKey, value: MultiMapValue) -> bool:
        """
        Tests whether the current multimap includes this value.
        """
        if not self.has_key(key):
            return False
        return value in self.get(key)

    def keys(self) -> Iterable[MultiMapKey]:
        """
        Get all keys of the current multimap.
        """
        return self._store.keys()

    def discard_value_from_all_keys(self, value: MultiMapValue):
        for store_set in self._store.values():
            store_set.discard(value)

    def discard_item(self, key: MultiMapKey, value: MultiMapValue) -> None:
        if key in self._store:
            self._store.get(key).discard(value)

    @property
    def store(self) -> Dict[MultiMapKey, Set[MultiMapValue]]:
        return self._store

    def clear(self):
        self._store.clear()

    def get_all_values(self):
        return self._store.values()

    def put(self, key: MultiMapKey, value: MultiMapValue):
        if key not in self._store:
            self._store[key] = set([])
        self._store[key].add(value)

    def get(self, key: MultiMapKey) -> Set[MultiMapValue]:
        if key not in self._store:
            return set()
        return self._store.get(key)

    def __eq__(self, other):
        if not isinstance(other, SetMultimap):
            return False
        return self._store == other._store

    def __str__(self):
        return str(self._store)

    def __iter__(self):
        return self._store.__iter__()

    def __len__(self):
        return len(self._store)

    def pop(self, key: MultiMapKey, default_value: Optional[MultiMapValue] = None):
        return self._store.pop(key, default_value)

    def put_all(self, key: MultiMapKey, values: Iterable[MultiMapValue]):
        """
        Add all values from another iterable to this multimap by a specific key.
        """
        if key not in self._store:
            self._store[key] = set([])
        value_set = self._store[key]
        value_set.update(values)

    def remove_all(self, key: MultiMapKey):
        """
        Clear the key from this multimap.
        """
        self._store.pop(key, None)


class ListMultimap(Generic[MultiMapKey, MultiMapValue]):
    """
     A multimap based on a mutable list for duplication of values.
    """
    _store: Dict[MultiMapKey, List[MultiMapValue]]

    def __init__(self):
        self._store = dict()

    def has_key(self, key: MultiMapKey) -> bool:
        """
        Tests whether the current multimap includes this key.
        """
        return key in self._store

    def has_item(self, key: MultiMapKey, value: MultiMapValue) -> bool:
        """
        Tests whether the current multimap includes this value.
        """
        if not self.has_key(key):
            return False
        return value in self.get(key)

    def keys(self) -> Iterable[MultiMapKey]:
        """
        Get all keys of the current multimap.
        """
        return self._store.keys()

    @property
    def store(self) -> Dict[MultiMapKey, List[MultiMapValue]]:
        return self._store

    def discard_item(self, key: MultiMapKey, value: MultiMapValue) -> None:
        if key in self._store:
            if value in self._store.get(key):
                self._store.get(key).remove(value)

    def clear(self):
        self._store.clear()

    def get_all_values(self):
        return self._store.values()

    def put(self, key: MultiMapKey, value: MultiMapValue):
        if key not in self._store:
            self._store[key] = []
        self._store[key].append(value)

    def get(self, key: MultiMapKey) -> List[MultiMapValue]:
        if key not in self._store:
            return []
        return self._store.get(key)

    def __eq__(self, other):
        if not isinstance(other, ListMultimap):
            return False
        return self._store == other._store

    def __str__(self):
        return str(self._store)

    def __iter__(self):
        return self._store.__iter__()

    def __len__(self):
        return len(self._store)

    def pop(self, key: MultiMapKey, default_value: Optional[MultiMapValue] = None):
        return self._store.pop(key, default_value)

    def put_all(self, key: MultiMapKey, values: Iterable[MultiMapValue]):
        """
        Add all values from another iterable to this multimap by a specific key.
        """
        if key not in self._store:
            self._store[key] = list([])
        value_set = self._store[key]
        value_set.extend(values)

    def remove_all(self, key: MultiMapKey):
        """
        Clear the key from this multimap.
        """
        self._store.pop(key, None)