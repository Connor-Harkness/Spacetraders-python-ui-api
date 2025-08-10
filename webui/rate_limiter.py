"""
Rate limiting functionality for API requests.
"""

import asyncio
import time
from typing import Callable, Any
from functools import wraps

class RateLimiter:
    """Rate limiter that enforces a maximum number of requests per time window."""
    
    def __init__(self, max_requests: int = 2, time_window: float = 1.0):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        Acquire permission to make a request. Blocks if rate limit would be exceeded.
        """
        async with self._lock:
            current_time = time.time()
            
            # Remove requests outside the time window
            self.requests = [req_time for req_time in self.requests 
                           if current_time - req_time < self.time_window]
            
            # If we're at the limit, wait until we can make another request
            if len(self.requests) >= self.max_requests:
                # Calculate how long to wait
                oldest_request = min(self.requests)
                wait_time = self.time_window - (current_time - oldest_request)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Remove the old request after waiting
                    self.requests = [req_time for req_time in self.requests 
                                   if time.time() - req_time < self.time_window]
            
            # Record this request
            self.requests.append(time.time())

def rate_limited(func: Callable) -> Callable:
    """
    Decorator to apply rate limiting to async functions.
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> Any:
        await self.rate_limiter.acquire()
        return await func(self, *args, **kwargs)
    return wrapper