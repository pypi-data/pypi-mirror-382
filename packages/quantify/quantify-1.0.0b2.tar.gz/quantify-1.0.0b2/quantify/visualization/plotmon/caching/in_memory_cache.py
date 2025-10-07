"""in_memory_cache module: Thread-safe in-memory cache implementation for Plotmon."""

import threading

from quantify.visualization.plotmon.caching.base_cache import BaseCache


class InMemoryCache(BaseCache):
    """Thread-safe in memory cache implementation."""

    def __init__(self) -> None:
        """Initializes the in-memory cache and its lock."""
        if not hasattr(self, "_cache"):
            self._cache = {}
            self._cache_lock = threading.Lock()

    def set(self, cache_id: str, data: dict) -> None:
        """
        Set a cache entry by its ID.

        Parameters
        ----------
        cache_id : str
            The ID of the cache entry to set.
        data : Any
            The data to be cached.

        """
        with self._cache_lock:
            self._cache[cache_id] = data

    def get(self, cache_id: str) -> dict | None:
        """
        Retrieve a cache entry by its ID.

        Parameters
        ----------
        cache_id : str
            The ID of the cache entry to retrieve.

        Returns
        -------
        Any | None
            The cache entry if found, otherwise None.

        """
        with self._cache_lock:
            return self._cache.get(cache_id, None)

    def get_all(self, prefix: str = "", suffix: str = "") -> dict[str, dict]:
        """
        Retrieve all cache entries that match the given prefix and suffix.

        Parameters
        ----------
        prefix : str
            The prefix that the cache IDs should start with.
        suffix : str
            The suffix that the cache IDs should end with.

        Returns
        -------
        dict[str, Any]
            A dictionary of cache entries that match the criteria.

        """
        with self._cache_lock:
            return {
                key: value
                for key, value in self._cache.items()
                if key.startswith(prefix) and key.endswith(suffix)
            }
