#!/usr/bin/env python3
"""
Basic usage example for Kachy Valkey client.
"""

import os
import json
import kachy

def main():
    # Initialize the client with your access key
    kachy.init(os.environ.get("KACHY_ACCESS_KEY"))
    
    print("🚀 Kachy Valkey client initialized!")
    
    # Basic operations
    print("\n📝 Setting key-value pairs...")
    kachy.set("greeting", "Hello, World!")
    kachy.set("user:123:name", "John Doe")
    kachy.set("session:abc", "active", 3600)  # 1 hour expiration
    
    print("✅ Keys set successfully!")
    
    # Retrieving values
    print("\n📖 Retrieving values...")
    greeting = kachy.get("greeting")
    user_name = kachy.get("user:123:name")
    session = kachy.get("session:abc")
    
    print(f"Greeting: {greeting}")
    print(f"User name: {user_name}")
    print(f"Session: {session}")
    
    # Check if keys exist
    print("\n🔍 Checking key existence...")
    exists_greeting = kachy.exists("greeting")
    exists_nonexistent = kachy.exists("nonexistent")
    
    print(f"Greeting exists: {exists_greeting}")
    print(f"Nonexistent key exists: {exists_nonexistent}")
    
    # Get TTL for session
    print("\n⏰ Getting TTL...")
    ttl = kachy.ttl("session:abc")
    print(f"Session TTL: {ttl} seconds")
    
    # Custom Valkey commands
    print("\n⚡ Using custom Valkey commands...")
    
    # Hash operations
    kachy.valkey("HMSET", "user:123:profile", "age", "30", "city", "New York")
    profile = kachy.valkey("HMGET", "user:123:profile", "age", "city")
    print(f"User profile: {profile}")
    
    # List operations
    kachy.valkey("LPUSH", "notifications:123", "Welcome message")
    kachy.valkey("LPUSH", "notifications:123", "System update")
    notifications = kachy.valkey("LRANGE", "notifications:123", 0, -1)
    print(f"Notifications: {notifications}")
    
    # Pipeline operations
    print("\n🚀 Using pipeline for batch operations...")
    with kachy.pipeline() as pipe:
        pipe.set("batch:1", "value1")
        pipe.set("batch:2", "value2")
        pipe.set("batch:3", "value3")
        results = pipe.execute()
    
    print(f"Pipeline results: {results}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    kachy.delete("greeting")
    kachy.delete("user:123:name")
    kachy.delete("user:123:profile")
    kachy.delete("notifications:123")
    kachy.delete("batch:1")
    kachy.delete("batch:2")
    kachy.delete("batch:3")
    
    print("✅ Cleanup completed!")
    
    # Close connection
    kachy.close()
    print("\n👋 Client closed!")

if __name__ == "__main__":
    main()
