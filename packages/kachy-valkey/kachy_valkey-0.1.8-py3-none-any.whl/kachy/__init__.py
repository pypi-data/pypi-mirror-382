"""
Kachy Valkey Client

High-performance Valkey client with automatic authentication and multi-tenancy support.

Version 0.1.6 - Single-file architecture to eliminate circular imports.
"""

import os
import json
import time
import requests
from typing import Any, Optional, Dict, List, Union, TYPE_CHECKING
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import dataclass, field

# Version information
__version__ = "0.1.8"
__author__ = "Kachy Team"

if TYPE_CHECKING:
    pass


@dataclass
class KachyConfig:
    """Configuration for the Kachy Redis client."""
    
    access_key: str
    base_url: str = field(default_factory=lambda: os.environ.get("KACHY_BASE_URL", "https://api.klache.net"))
    timeout: int = field(default_factory=lambda: int(os.environ.get("KACHY_TIMEOUT", "30")))
    max_retries: int = field(default_factory=lambda: int(os.environ.get("KACHY_MAX_RETRIES", "3")))
    retry_delay: float = field(default_factory=lambda: float(os.environ.get("KACHY_RETRY_DELAY", "1.0")))
    pool_size: int = field(default_factory=lambda: int(os.environ.get("KACHY_POOL_SIZE", "10")))
    user_agent: str = field(default="kachy-valkey-python/0.1.6")
    
    # Request headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and set default values after initialization."""
        if not self.access_key:
            raise ValueError("KACHY_ACCESS_KEY is required")
        
        # Set default headers
        if not self.headers:
            self.headers = {
                "User-Agent": self.user_agent,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "access_key": self.access_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "pool_size": self.pool_size,
            "user_agent": self.user_agent,
            "headers": self.headers.copy()
        }
    
    @classmethod
    def from_env(cls) -> "KachyConfig":
        """Create configuration from environment variables."""
        return cls(
            access_key=os.environ["KACHY_ACCESS_KEY"],
            base_url=os.environ.get("KACHY_BASE_URL", "https://api.klache.net"),
            timeout=int(os.environ.get("KACHY_TIMEOUT", "30")),
            max_retries=int(os.environ.get("KACHY_MAX_RETRIES", "3")),
            retry_delay=float(os.environ.get("KACHY_RETRY_DELAY", "1.0")),
            pool_size=int(os.environ.get("KACHY_POOL_SIZE", "10"))
        )


class KachyError(Exception):
    """Base exception for Kachy Redis client."""
    pass


class KachyConnectionError(KachyError):
    """Exception raised for connection errors."""
    pass


class KachyAuthenticationError(KachyError):
    """Exception raised for authentication errors."""
    pass


class KachyResponseError(KachyError):
    """Exception raised for API response errors."""
    pass


class KachyPipeline:
    """Pipeline for batch Redis operations."""
    
    def __init__(self, client: "KachyClient"):
        """Initialize the pipeline.
        
        Args:
            client: The Kachy client instance
        """
        self.client = client
        self.commands = []
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> "KachyPipeline":
        """Add SET command to pipeline.
        
        Args:
            key: The key to set
            value: The value to store
            ex: Expiration time in seconds
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("SET", key, value, ex))
        return self
    
    def get(self, key: str) -> "KachyPipeline":
        """Add GET command to pipeline.
        
        Args:
            key: The key to retrieve
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("GET", key))
        return self
    
    def delete(self, key: str) -> "KachyPipeline":
        """Add DELETE command to pipeline.
        
        Args:
            key: The key to delete
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("DEL", key))
        return self
    
    def exists(self, key: str) -> "KachyPipeline":
        """Add EXISTS command to pipeline.
        
        Args:
            key: The key to check
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("EXISTS", key))
        return self
    
    def expire(self, key: str, seconds: int) -> "KachyPipeline":
        """Add EXPIRE command to pipeline.
        
        Args:
            key: The key to set expiration for
            seconds: Expiration time in seconds
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("EXPIRE", key, seconds))
        return self
    
    def ttl(self, key: str) -> "KachyPipeline":
        """Add TTL command to pipeline.
        
        Args:
            key: The key to check
            
        Returns:
            Self for method chaining
        """
        self.commands.append(("TTL", key))
        return self
    
    def redis(self, command: str, *args) -> "KachyPipeline":
        """Add custom Redis command to pipeline.
        
        Args:
            command: The Redis command to execute
            *args: Arguments for the command
            
        Returns:
            Self for method chaining
        """
        self.commands.append((command.upper(),) + args)
        return self
    
    def execute(self) -> List[Any]:
        """Execute all commands in the pipeline.
        
        Returns:
            List of results for each command
            
        Raises:
            KachyError: If pipeline execution fails
        """
        if not self.commands:
            return []
        
        try:
            # Execute all commands in a single batch request
            data = {
                "commands": [
                    {
                        "command": cmd[0],
                        "args": list(cmd[1:])
                    }
                    for cmd in self.commands
                ]
            }
            
            result = self.client._make_request("POST", "/valkey/pipeline", data)
            results = result.get("results", [])
            
            # Clear commands after execution
            self.commands.clear()
            
            return results
            
        except Exception as e:
            # Clear commands on error
            self.commands.clear()
            raise e
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - execute pipeline if not empty."""
        if self.commands:
            self.execute()


class KachyClient:
    """Main client for interacting with Kachy Redis."""
    
    def __init__(self, config: KachyConfig):
        """Initialize the Kachy client.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create and configure the requests session."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
            backoff_factor=self.config.retry_delay
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=self.config.pool_size)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_auth_token(self) -> str:
        """Get the access key for authentication."""
        return self.config.access_key
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make an HTTP request to the Kachy API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            
        Returns:
            API response data
            
        Raises:
            KachyConnectionError: For connection issues
            KachyAuthenticationError: For authentication issues
            KachyResponseError: For API errors
        """
        url = f"{self.config.base_url}{endpoint}"
        headers = self.config.headers.copy()
        headers["Authorization"] = f"Bearer {self._get_auth_token()}"
        
        # Debug logging
        print(f"🔍 DEBUG: Making {method} request to {url}")
        print(f"🔍 DEBUG: Headers: {headers}")
        print(f"🔍 DEBUG: Data: {data}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            
            print(f"🔍 DEBUG: Response status: {response.status_code}")
            print(f"🔍 DEBUG: Response headers: {dict(response.headers)}")
            print(f"🔍 DEBUG: Response text: {response.text}")
            
            if response.status_code == 401:
                raise KachyAuthenticationError(f"Authentication failed. Status: {response.status_code}, Response: {response.text}")
            elif response.status_code >= 400:
                raise KachyResponseError(f"API error {response.status_code}: {response.text}")
            
            return response.json() if response.content else None
            
        except requests.exceptions.RequestException as e:
            raise KachyConnectionError(f"Request failed: {e}")
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration.
        
        Args:
            key: The key to set
            value: The value to store
            ex: Expiration time in seconds
            
        Returns:
            True if successful
        """
        data = {"key": key, "value": value}
        if ex is not None:
            data["ex"] = ex
        
        result = self._make_request("POST", "/valkey/set", data)
        return result.get("success", False)
    
    def get(self, key: str) -> Optional[str]:
        """Get a value by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        result = self._make_request("GET", f"/valkey/get/{key}")
        return result.get("value")
    
    def delete(self, key: str) -> bool:
        """Delete a key.
        
        Args:
            key: The key to delete
            
        Returns:
            True if key was deleted, False if it didn't exist
        """
        result = self._make_request("DELETE", f"/valkey/del/{key}")
        return result.get("deleted", False)
    
    def exists(self, key: str) -> bool:
        """Check if a key exists.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists, False otherwise
        """
        result = self._make_request("GET", f"/valkey/exists/{key}")
        return result.get("exists", False)
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key.
        
        Args:
            key: The key to set expiration for
            seconds: Expiration time in seconds
            
        Returns:
            True if expiration was set, False if key doesn't exist
        """
        data = {"key": key, "seconds": seconds}
        result = self._make_request("POST", "/valkey/expire", data)
        return result.get("success", False)
    
    def ttl(self, key: str) -> int:
        """Get time to live for a key.
        
        Args:
            key: The key to check
            
        Returns:
            Time to live in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        result = self._make_request("GET", f"/valkey/ttl/{key}")
        return result.get("ttl", -2)
    
    def redis(self, command: str, *args) -> Any:
        """Execute any Redis command.
        
        Args:
            command: The Redis command to execute
            *args: Arguments for the command
            
        Returns:
            The result of the Redis command
        """
        data = {
            "command": command.upper(),
            "args": list(args)
        }
        
        result = self._make_request("POST", "/valkey/exec", data)
        return result.get("result")
    
    def valkey(self, command: str, *args) -> Any:
        """Execute any Valkey command.
        
        Args:
            command: The Valkey command to execute
            *args: Arguments for the command
            
        Returns:
            The result of the Valkey command
        """
        return self.redis(command, *args)
    
    def pipeline(self) -> KachyPipeline:
        """Create a pipeline for batch operations.
        
        Returns:
            A pipeline object for batch operations
        """
        return KachyPipeline(self)
    
    def close(self):
        """Close the connection and cleanup resources."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global client instance
_client = None

def init(access_key, **kwargs):
    """Initialize the Kachy client with your access key.
    
    Args:
        access_key (str): Your KACHY_ACCESS_KEY for authentication
        **kwargs: Additional configuration options
    """
    global _client
    config = KachyConfig(access_key=access_key, **kwargs)
    _client = KachyClient(config)
    return _client

def get_client():
    """Get the current Kachy client instance.
    
    Returns:
        KachyClient: The initialized client instance
        
    Raises:
        RuntimeError: If client is not initialized
    """
    if _client is None:
        raise RuntimeError("Kachy client not initialized. Call kachy.init() first.")
    return _client

# Convenience functions that delegate to the global client
def set(key, value, ex=None):
    """Set a key-value pair with optional expiration.
    
    Args:
        key (str): The key to set
        value (str): The value to store
        ex (int, optional): Expiration time in seconds
    """
    return get_client().set(key, value, ex)

def get(key):
    """Get a value by key.
    
    Args:
        key (str): The key to retrieve
        
    Returns:
        str: The stored value, or None if not found
    """
    return get_client().get(key)

def delete(key):
    """Delete a key.
    
    Args:
        key (str): The key to delete
        
    Returns:
        bool: True if key was deleted, False if it didn't exist
    """
    return get_client().delete(key)

def exists(key):
    """Check if a key exists.
    
    Args:
        key (str): The key to check
        
    Returns:
        bool: True if key exists, False otherwise
    """
    return get_client().exists(key)

def expire(key, seconds):
    """Set expiration for a key.
    
    Args:
        key (str): The key to set expiration for
        seconds (int): Expiration time in seconds
        
    Returns:
        bool: True if expiration was set, False if key doesn't exist
    """
    return get_client().expire(key, seconds)

def ttl(key):
    """Get time to live for a key.
    
    Args:
        key (str): The key to check
        
    Returns:
        int: Time to live in seconds, -1 if no expiration, -2 if key doesn't exist
    """
    return get_client().ttl(key)

def valkey(command, *args):
    """Execute any Valkey command.
    
    Args:
        command (str): The Valkey command to execute
        *args: Arguments for the command
        
    Returns:
        The result of the Valkey command
    """
    return get_client().valkey(command, *args)

def pipeline():
    """Create a pipeline for batch operations.
    
    Returns:
        KachyPipeline: A pipeline object for batch operations
    """
    return get_client().pipeline()

def close():
    """Close the connection."""
    if _client:
        _client.close()

def debug_info():
    """Print debug information about the kachy module."""
    import sys
    print(f"Kachy version: {__version__}")
    print(f"Python version: {sys.version}")
    print(f"Module file: {__file__}")
    print(f"Module path: {sys.modules[__name__].__path__}")
    print(f"Available classes: KachyClient, KachyConfig, KachyPipeline")
    print("✅ Single-file architecture - no circular imports possible")

def test_connection(access_key: str, base_url: str = None):
    """Test the connection to the Kachy API."""
    if base_url is None:
        base_url = os.environ.get("KACHY_BASE_URL", "https://api.klache.net")
    
    print(f"🔍 Testing connection to: {base_url}")
    print(f"🔍 Using access key: {access_key[:8]}...")
    
    try:
        client = init(access_key, base_url=base_url)
        print("✅ Client initialized successfully")
        
        # Try a simple operation
        result = client.get("test-connection")
        print(f"✅ Test operation successful: {result}")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()

# Export main classes - these will be available after import
__all__ = [
    'init',
    'get_client',
    'set',
    'get',
    'delete',
    'exists',
    'expire',
    'ttl',
    'valkey',
    'pipeline',
    'close',
    'KachyClient',
    'KachyConfig',
    'KachyPipeline',
    'KachyError',
    'KachyConnectionError',
    'KachyAuthenticationError',
    'KachyResponseError',
    'debug_info',
    'test_connection',
    '__version__'
]