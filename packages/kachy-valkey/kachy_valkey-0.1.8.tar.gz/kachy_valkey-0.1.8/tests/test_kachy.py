#!/usr/bin/env python3
"""
Basic tests for Kachy Valkey client.
"""

import unittest
import os
from unittest.mock import patch, MagicMock

# Import the kachy module
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import kachy


class TestKachyClient(unittest.TestCase):
    """Test cases for Kachy Valkey client."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variable
        self.env_patcher = patch.dict(os.environ, {'KACHY_SECRET': 'test-secret'})
        self.env_patcher.start()
        
        # Mock the client
        self.mock_client = MagicMock()
        self.client_patcher = patch('kachy.KachyClient')
        self.mock_client_class = self.client_patcher.start()
        self.mock_client_class.return_value = self.mock_client
        
        # Initialize kachy
        kachy.init('test-secret')
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
        self.client_patcher.stop()
        kachy.close()
    
    def test_init(self):
        """Test client initialization."""
        self.assertIsNotNone(kachy.get_client())
        self.mock_client_class.assert_called_once()
    
    def test_set(self):
        """Test set operation."""
        self.mock_client.set.return_value = True
        
        result = kachy.set('test-key', 'test-value')
        
        self.assertTrue(result)
        self.mock_client.set.assert_called_once_with('test-key', 'test-value', None)
    
    def test_set_with_expiration(self):
        """Test set operation with expiration."""
        self.mock_client.set.return_value = True
        
        result = kachy.set('test-key', 'test-value', 3600)
        
        self.assertTrue(result)
        self.mock_client.set.assert_called_once_with('test-key', 'test-value', 3600)
    
    def test_get(self):
        """Test get operation."""
        self.mock_client.get.return_value = 'test-value'
        
        result = kachy.get('test-key')
        
        self.assertEqual(result, 'test-value')
        self.mock_client.get.assert_called_once_with('test-key')
    
    def test_delete(self):
        """Test delete operation."""
        self.mock_client.delete.return_value = True
        
        result = kachy.delete('test-key')
        
        self.assertTrue(result)
        self.mock_client.delete.assert_called_once_with('test-key')
    
    def test_exists(self):
        """Test exists operation."""
        self.mock_client.exists.return_value = True
        
        result = kachy.exists('test-key')
        
        self.assertTrue(result)
        self.mock_client.exists.assert_called_once_with('test-key')
    
    def test_expire(self):
        """Test expire operation."""
        self.mock_client.expire.return_value = True
        
        result = kachy.expire('test-key', 3600)
        
        self.assertTrue(result)
        self.mock_client.expire.assert_called_once_with('test-key', 3600)
    
    def test_ttl(self):
        """Test ttl operation."""
        self.mock_client.ttl.return_value = 1800
        
        result = kachy.ttl('test-key')
        
        self.assertEqual(result, 1800)
        self.mock_client.ttl.assert_called_once_with('test-key')
    
    def test_valkey(self):
        """Test custom valkey command."""
        self.mock_client.valkey.return_value = ['value1', 'value2']
        
        result = kachy.valkey('HMGET', 'hash-key', 'field1', 'field2')
        
        self.assertEqual(result, ['value1', 'value2'])
        self.mock_client.valkey.assert_called_once_with('HMGET', 'hash-key', 'field1', 'field2')
    
    def test_pipeline(self):
        """Test pipeline creation."""
        mock_pipeline = MagicMock()
        self.mock_client.pipeline.return_value = mock_pipeline
        
        result = kachy.pipeline()
        
        self.assertEqual(result, mock_pipeline)
        self.mock_client.pipeline.assert_called_once()
    
    def test_close(self):
        """Test close operation."""
        kachy.close()
        
        self.mock_client.close.assert_called_once()
    
    def test_get_client_not_initialized(self):
        """Test get_client when not initialized."""
        kachy.close()
        
        with self.assertRaises(RuntimeError):
            kachy.get_client()


if __name__ == '__main__':
    unittest.main()
