import redis
import os
import json

class Cache:
    """
    A Redis-based cache with expiration.
    """
    def __init__(self, redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")):
        self._redis_client = redis.from_url(redis_url)

    def set(self, key: str, value, ttl: int = None):
        """
        Sets a value in the cache with an optional time-to-live (ttl) in seconds.
        Value is serialized to JSON.
        """
        try:
            serialized_value = json.dumps(value)
            if ttl is not None:
                self._redis_client.setex(key, ttl, serialized_value)
            else:
                self._redis_client.set(key, serialized_value)
        except Exception as e:
            print(f"Error setting cache key {key}: {e}")

    def get(self, key: str):
        """
        Retrieves a value from the cache.
        Returns None if the key is not found or has expired.
        Value is deserialized from JSON.
        """
        try:
            serialized_value = self._redis_client.get(key)
            if serialized_value:
                return json.loads(serialized_value)
            return None
        except Exception as e:
            print(f"Error getting cache key {key}: {e}")
            return None

    def delete(self, key: str):
        """
        Deletes a key from the cache.
        """
        try:
            self._redis_client.delete(key)
        except Exception as e:
            print(f"Error deleting cache key {key}: {e}")

    def clear(self):
        """
        Clears the entire cache.
        """
        try:
            self._redis_client.flushdb()
        except Exception as e:
            print(f"Error clearing cache: {e}")