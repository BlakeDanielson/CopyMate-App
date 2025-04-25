
import unittest
from unittest.mock import patch
# Assume the cache module will be in backend/data_fetching/cache.py
from backend.data_fetching.cache import Cache

class TestCache(unittest.TestCase):
    
    @patch('redis.from_url')
    def setUp(self, mock_redis_from_url):
        # Mock Redis client
        self.mock_redis = mock_redis_from_url.return_value
        self.cache = Cache()
        
        # Reset any previous calls
        self.mock_redis.reset_mock()
        
        # Set up storage for our test data
        self._storage = {}
        
        # Mock Redis get method
        def mock_get(key):
            return self._storage.get(key)
        self.mock_redis.get.side_effect = mock_get
        
        # Mock Redis set method
        def mock_set(key, value):
            self._storage[key] = value
            return True
        self.mock_redis.set.side_effect = mock_set
        
        # Mock Redis setex method
        def mock_setex(key, ttl, value):
            self._storage[key] = value
            return True
        self.mock_redis.setex.side_effect = mock_setex
    
    def test_set_and_get(self):
        key = "test_key"
        value = {"data": "test_value"}
        self.cache.set(key, value)
        
        # Verify Redis set was called with serialized value
        import json
        serialized_value = json.dumps(value)
        self.mock_redis.set.assert_called_once_with(key, serialized_value)
        
        # Test get operation
        retrieved_value = self.cache.get(key)
        self.assertEqual(retrieved_value, value)
        self.mock_redis.get.assert_called_once_with(key)

    @patch('time.time')
    def test_expiration(self, mock_time):
        key = "expiring_key"
        value = {"data": "expiring_value"}
        ttl = 60 # Time to live in seconds

        # Test expired item - simulate Redis behavior by returning None on get
        mock_time.return_value = 100 # Current time
        self.cache.set(key, value, ttl)
        
        # Verify setex was called with correct parameters
        import json
        serialized_value = json.dumps(value)
        self.mock_redis.setex.assert_called_once_with(key, ttl, serialized_value)
        
        # Reset mock and simulate Redis returning None (expired key)
        self.mock_redis.reset_mock()
        self._storage.clear()  # Simulate key expiration
        
        mock_time.return_value = 200 # Time after expiration
        retrieved_value = self.cache.get(key)
        self.assertIsNone(retrieved_value)
        self.mock_redis.get.assert_called_once_with(key)

        # Test non-expired item
        self.mock_redis.reset_mock()
        mock_time.return_value = 300 # Current time
        self.cache.set(key, value, ttl)
        
        # Reset mock and store valid data for the get operation
        self.mock_redis.reset_mock()
        
        mock_time.return_value = 350 # Time before expiration
        retrieved_value = self.cache.get(key)
        self.assertEqual(retrieved_value, value)
        self.mock_redis.get.assert_called_once_with(key)

if __name__ == '__main__':
    unittest.main()