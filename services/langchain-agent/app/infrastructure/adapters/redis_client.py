"""
Redis client adapter for pub/sub and caching operations.
"""

import json
from typing import Any, Dict, List, Optional, Callable, Awaitable
import aioredis
from aioredis import Redis

from app.core.config import settings


class RedisClient:
    """
    Redis client for pub/sub and caching operations.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the Redis client.
        
        Args:
            redis_url: Optional Redis URL. If not provided, will use settings.
        """
        if redis_url is None:
            # Construct Redis URL from settings
            password_part = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
            redis_url = f"redis://{password_part}{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None
        self.pubsub = None
    
    async def connect(self) -> None:
        """
        Connect to Redis server.
        """
        if self.redis is None:
            self.redis = await aioredis.from_url(
                self.redis_url,
                decode_responses=True  # Automatically decode to strings
            )
    
    async def disconnect(self) -> None:
        """
        Disconnect from Redis server.
        """
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    async def _ensure_connected(self) -> None:
        """Ensure Redis connection is established."""
        if self.redis is None:
            await self.connect()
    
    async def publish(self, channel: str, message: Any) -> int:
        """
        Publish a message to a channel.
        
        Args:
            channel: The channel to publish to.
            message: The message to publish (will be JSON-encoded if not a string).
            
        Returns:
            Number of clients that received the message.
        """
        await self._ensure_connected()
        
        # Convert message to string if it's not already
        if not isinstance(message, str):
            message = json.dumps(message)
        
        return await self.redis.publish(channel, message)
    
    async def subscribe(
        self, 
        channel: str, 
        callback: Callable[[str, str], Awaitable[None]]
    ) -> None:
        """
        Subscribe to a channel and process messages with callback.
        
        Args:
            channel: The channel to subscribe to.
            callback: Async function to call with channel and message.
        """
        await self._ensure_connected()
        
        # Create pubsub if not exists
        if not self.pubsub:
            self.pubsub = self.redis.pubsub()
        
        # Subscribe to channel
        await self.pubsub.subscribe(channel)
        
        # Start listening for messages in a background task
        while True:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                # Process message with callback
                await callback(message["channel"], message["data"])
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Set a key-value pair in Redis.
        
        Args:
            key: The key to set.
            value: The value to set (will be JSON-encoded if not a string).
            expire: Optional expiration time in seconds.
            
        Returns:
            True if successful.
        """
        await self._ensure_connected()
        
        # Convert value to string if it's not already
        if not isinstance(value, str):
            value = json.dumps(value)
        
        if expire:
            return await self.redis.setex(key, expire, value)
        else:
            return await self.redis.set(key, value)
    
    async def get(self, key: str, as_json: bool = False) -> Any:
        """
        Get a value from Redis.
        
        Args:
            key: The key to get.
            as_json: Whether to parse the value as JSON.
            
        Returns:
            The value, or None if not found.
        """
        await self._ensure_connected()
        
        value = await self.redis.get(key)
        
        if value and as_json:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        
        return value
    
    async def delete(self, key: str) -> int:
        """
        Delete a key from Redis.
        
        Args:
            key: The key to delete.
            
        Returns:
            Number of keys deleted.
        """
        await self._ensure_connected()
        
        return await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            key: The key to check.
            
        Returns:
            True if the key exists.
        """
        await self._ensure_connected()
        
        return await self.redis.exists(key) > 0
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """
        Increment a key's value.
        
        Args:
            key: The key to increment.
            amount: The amount to increment by.
            
        Returns:
            The new value.
        """
        await self._ensure_connected()
        
        return await self.redis.incrby(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key: The key to set expiration for.
            seconds: Expiration time in seconds.
            
        Returns:
            True if successful.
        """
        await self._ensure_connected()
        
        return await self.redis.expire(key, seconds)
