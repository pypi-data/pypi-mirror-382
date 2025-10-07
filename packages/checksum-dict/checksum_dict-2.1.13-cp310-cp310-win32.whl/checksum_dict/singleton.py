import threading
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Final, Generic, Optional, Tuple

from checksum_dict import exceptions
from checksum_dict._typing import AnyAddressOrContract
from checksum_dict.base import ChecksumAddressDict, T


_LocksDict = DefaultDict[AnyAddressOrContract, threading.Lock]


class ChecksumAddressSingletonMeta(type, Generic[T]):
    """A metaclass for creating singleton instances of addresses.

    This metaclass ensures that each address has a single instance across the application.
    It uses a :class:`~checksum_dict.base.ChecksumAddressDict` to store instances and manages locks to ensure
    thread safety during instance creation.

    Note:
        This implementation uses a :mod:`cchecksum`'s Cython implementation for checksumming to optimize
        performance over the standard :func:`eth_utils.to_checksum_address`.

    Examples:
        >>> class MySingleton(metaclass=ChecksumAddressSingletonMeta):
        ...     def __init__(self, address):
        ...         self.address = address
        ...
        >>> instance1 = MySingleton('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb')
        >>> instance2 = MySingleton('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb')
        >>> assert instance1 is instance2

    See Also:
        - :class:`ChecksumAddressDict` for the underlying dictionary implementation.
    """

    def __init__(self, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> None:
        """Initialize the metaclass with a name, bases, and namespace.

        Args:
            name: The name of the class being created.
            bases: A tuple of base classes.
            namespace: A dictionary representing the class namespace.
        """
        type.__init__(self, name, bases, namespace)
        self.__instances: Final[ChecksumAddressDict[T]] = ChecksumAddressDict()
        self.__locks: Final[_LocksDict] = defaultdict(threading.Lock)
        self.__locks_lock: Final[threading.Lock] = threading.Lock()

    def __call__(self, address: AnyAddressOrContract, *args: Any, **kwargs: Any) -> T:  # type: ignore
        # sourcery skip: use-contextlib-suppress
        """Create or retrieve a singleton instance for the given address.

        Args:
            address: The address for which to create or retrieve the singleton instance.
            *args: Additional positional arguments for instance creation.
            **kwargs: Additional keyword arguments for instance creation.

        Returns:
            The singleton instance associated with the given address.

        Raises:
            :class:`~checksum_dict.exceptions.KeyError`: If the address is not found in the cache.

        Examples:
            >>> class MySingleton(metaclass=ChecksumAddressSingletonMeta):
            ...     def __init__(self, address):
            ...         self.address = address
            ...
            >>> instance = MySingleton('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb')
        """
        normalized = str(address)
        try:
            return self.__instances[normalized]
        except exceptions.KeyError:
            pass  # NOTE: passing instead of proceeding lets helps us keep a clean exc chain

        with self.__get_address_lock(normalized):
            # Try to get the instance again, in case it was added while waiting for the lock
            try:
                return self.__instances[normalized]
            except exceptions.KeyError:
                pass  # NOTE: passing instead of proceeding here lets us keep a clean exc chain

            instance: T = type.__call__(self, normalized, *args, **kwargs)
            self.__instances[normalized] = instance
        self.__delete_address_lock(normalized)
        return instance

    def __getitem__(self, address: AnyAddressOrContract) -> T:
        """Get the singleton instance for `address` from the cache.

        Args:
            address: The address for which to retrieve the singleton instance.

        Returns:
            The singleton instance associated with the given address.

        Raises:
            :class:`~checksum_dict.exceptions.KeyError`: If the address is not found in the cache.

        Examples:
            >>> meta = ChecksumAddressSingletonMeta('MySingleton', (), {})
            >>> instance = meta['0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb']
        """
        return self.__instances[str(address)]

    def __setitem__(self, address: AnyAddressOrContract, item: T) -> None:
        """Set the singleton instance for `address` in the cache.

        You can use this if you need to implement non-standard init sequences.

        Args:
            address: The address for which to set the singleton instance.
            item: The instance to associate with the given address.

        Examples:
            >>> meta = ChecksumAddressSingletonMeta('MySingleton', (), {})
            >>> meta['0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb'] = MySingleton('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb')
        """
        normalized = str(address)
        with self.__get_address_lock(normalized):
            self.__instances[normalized] = item
        self.__delete_address_lock(normalized)

    def __delitem__(self, address: AnyAddressOrContract) -> None:
        """Delete the singleton instance for a given address from the cache.

        Args:
            address: The address for which to delete the instance.

        Raises:
            KeyError: If the address is not found in the cache.

        Examples:
            >>> meta = ChecksumAddressSingletonMeta('MySingleton', (), {})
            >>> del meta['0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb']
        """
        del self.__instances[str(address)]  # type: ignore [arg-type]

    def get_instance(self, address: AnyAddressOrContract) -> Optional[T]:
        """Retrieve the singleton instance for a given address, if it exists.

        Args:
            address: The address for which to retrieve the instance.

        Returns:
            The instance associated with the address, or None if not found.

        Examples:
            >>> meta = ChecksumAddressSingletonMeta('MySingleton', (), {})
            >>> instance = meta.get_instance('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb')
        """
        return self.__instances.get(str(address))  # type: ignore [call-overload, no-any-return]

    def delete_instance(self, address: AnyAddressOrContract) -> None:
        # sourcery skip: use-contextlib-suppress
        """Delete the singleton instance for a given address, if it exists.

        Args:
            address: The address for which to delete the instance.

        Examples:
            >>> meta = ChecksumAddressSingletonMeta('MySingleton', (), {})
            >>> meta.delete_instance('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb')
        """
        try:
            del self.__instances[str(address)]  # type: ignore [arg-type]
        except KeyError:
            pass

    def __get_address_lock(self, address: AnyAddressOrContract) -> threading.Lock:
        """Acquire a lock for the given address to ensure thread safety.

        This method ensures that the singleton instance creation is thread-safe by
        acquiring a lock for the specific address.

        Args:
            address: The address for which to acquire the lock.

        Returns:
            A threading.Lock object for the given address.

        Examples:
            >>> meta = ChecksumAddressSingletonMeta('MySingleton', (), {})
            >>> lock = meta._ChecksumAddressSingletonMeta__get_address_lock('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb')
        """
        with self.__locks_lock:
            return self.__locks[address]

    def __delete_address_lock(self, address: AnyAddressOrContract) -> None:
        # sourcery skip: use-contextlib-suppress
        """Delete the lock for an address once the instance is created.

        This method removes the lock for an address after the singleton instance
        has been successfully created, freeing up resources.

        Args:
            address: The address for which to delete the lock.

        Examples:
            >>> meta = ChecksumAddressSingletonMeta('MySingleton', (), {})
            >>> meta._ChecksumAddressSingletonMeta__delete_address_lock('0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb')
        """
        with self.__locks_lock:
            try:
                del self.__locks[address]
            except KeyError:
                pass
