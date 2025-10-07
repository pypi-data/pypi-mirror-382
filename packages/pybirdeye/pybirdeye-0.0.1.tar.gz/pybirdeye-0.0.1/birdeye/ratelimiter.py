"""
Rate limiter implementation using token bucket algorithm.

This module provides a decorator-based rate limiter that can be used to limit
the rate at which functions are called.
"""

import time
import threading
from functools import wraps
from typing import Callable, Literal, List, Tuple, Any


# ============================================================================
# Rate Limit Behavior Types (for rate limiter)
# ============================================================================

RATE_LIMIT_BLOCK = "block"
RATE_LIMIT_RAISE = "raise"
RATE_LIMIT_SKIP = "skip"

RateLimitBehavior = Literal[RATE_LIMIT_BLOCK, RATE_LIMIT_RAISE, RATE_LIMIT_SKIP]


class RateLimiter:
    """
    Token bucket rate limiter implementation.
    
    This class implements the token bucket algorithm, which allows for burst
    traffic while maintaining an average rate limit over time.
    
    Args:
        limit: Maximum number of calls allowed in the given period
        period: Time period in seconds for the rate limit
        on_limit_exceeded: Behavior when rate limit is exceeded
            - 'block': Wait until a token is available (default)
            - 'raise': Raise a RateLimitExceeded exception
            - 'skip': Return None without executing the function
    """
    
    def __init__(
        self,
        limit: int,
        period: float,
        on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK
    ):
        if limit <= 0:
            raise ValueError("Limit must be positive")
        if period <= 0:
            raise ValueError("Period must be positive")
            
        self.limit = limit
        self.period = period
        self.on_limit_exceeded = on_limit_exceeded
        
        # Token bucket state
        self.tokens = float(limit)
        self.last_update = time.time()
        self.lock = threading.RLock()
    
    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time since last refill."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Calculate tokens to add based on elapsed time
        tokens_to_add = elapsed * (self.limit / self.period)
        self.tokens = min(self.limit, self.tokens + tokens_to_add)
        self.last_update = now
    
    def acquire(self, tokens: int = 1, on_limit_exceeded: RateLimitBehavior | None = None) -> bool:
        """
        Attempt to acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
            
        Returns:
            True if tokens were acquired, False otherwise
            
        Raises:
            RateLimitExceeded: If on_limit_exceeded is 'raise' and no tokens available
        """
        if on_limit_exceeded is None:
            on_limit_exceeded = self.on_limit_exceeded
        
        with self.lock:
            self._refill_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            if on_limit_exceeded == RATE_LIMIT_BLOCK:
                # Calculate wait time for next token
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed * (self.period / self.limit)
                
                # Release lock while sleeping
                self.lock.release()
                try:
                    time.sleep(wait_time)
                finally:
                    self.lock.acquire()
                
                # Refill and try again
                self._refill_tokens()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
                return False
                
            elif on_limit_exceeded == RATE_LIMIT_RAISE:
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {self.limit} calls per {self.period} seconds"
                )
            else:  # on_limit_exceeded == RATE_LIMIT_SKIP
                return False
    
    def __call__(self, func: Callable) -> Callable:
        """Allow RateLimiter to be used as a decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if self.acquire():
                return func(*args, **kwargs)
            return None
        return wrapper
    
    def reset(self) -> None:
        """Reset the rate limiter to its initial state."""
        with self.lock:
            self.tokens = float(self.limit)
            self.last_update = time.time()
    
    def get_available_tokens(self) -> float:
        """Get the current number of available tokens."""
        with self.lock:
            self._refill_tokens()
            return self.tokens
    
    def time_until_next_token(self) -> float:
        """Calculate time in seconds until next token is available."""
        with self.lock:
            self._refill_tokens()
            if self.tokens >= 1:
                return 0.0
            tokens_needed = 1 - self.tokens
            return tokens_needed * (self.period / self.limit)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


def ratelimit(
    limit: int,
    period: float,
    on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK
) -> Callable:
    """
    Decorator to rate limit function calls.
    
    Each decorated function gets its own independent rate limiter instance.
    
    Args:
        limit: Maximum number of calls allowed in the given period
        period: Time period in seconds for the rate limit
        on_limit_exceeded: Behavior when rate limit is exceeded
            - 'block': Wait until a token is available (default)
            - 'raise': Raise a RateLimitExceeded exception
            - 'skip': Return None without executing the function
    
    Example:
        >>> @ratelimit(limit=5, period=1.0)
        ... def api_call():
        ...     return "Success"
        
        >>> # Allow 10 requests per second
        >>> @ratelimit(limit=10, period=1.0)
        ... def high_frequency_call():
        ...     pass
        
        >>> # Raise exception when limit exceeded
        >>> @ratelimit(limit=1, period=1.0, on_limit_exceeded=RATE_LIMIT_RAISE)
        ... def strict_api_call():
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        limiter = RateLimiter(limit, period, on_limit_exceeded)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if limiter.acquire():
                return func(*args, **kwargs)
            return None
        
        # Attach limiter instance to wrapper for external access
        wrapper._rate_limiter = limiter
        return wrapper
    
    return decorator


class SharedRateLimiter:
    """
    A shared rate limiter that can be used across multiple functions.
    
    This is useful when you want to limit the combined rate of multiple
    functions rather than limiting each function independently.
    
    Example:
        >>> limiter = SharedRateLimiter(limit=10, period=1.0)
        >>> 
        >>> @limiter
        ... def api_call_1():
        ...     pass
        >>> 
        >>> @limiter
        ... def api_call_2():
        ...     pass
        >>> 
        >>> # Both functions share the same 10 calls/second limit
    """
    
    def __init__(
        self,
        limit: int,
        period: float,
        on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK
    ):
        self._limiter = RateLimiter(limit, period, on_limit_exceeded)
    
    def __call__(self, func: Callable) -> Callable:
        """Use as decorator to apply rate limiting to a function."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if self._limiter.acquire():
                return func(*args, **kwargs)
            return None
        return wrapper
    
    def acquire(self, tokens: int = 1, on_limit_exceeded: RateLimitBehavior | None = None) -> bool:
        """Manually acquire tokens from the shared limiter."""
        return self._limiter.acquire(tokens, on_limit_exceeded)
    
    def reset(self) -> None:
        """Reset the rate limiter."""
        self._limiter.reset()
    
    def get_available_tokens(self) -> float:
        """Get current available tokens."""
        return self._limiter.get_available_tokens()


class MultiRateLimiter:
    """
    Multi-tiered rate limiter that enforces multiple rate limits simultaneously.
    
    This is useful for APIs with tiered rate limiting, where you need to enforce
    multiple limits at different time scales (e.g., 10/second AND 100/minute AND 1000/hour).
    All rate limits must be satisfied for a request to proceed.
    
    Args:
        limits: List of (limit, period) tuples. Each tuple defines a rate limit.
        on_limit_exceeded: Behavior when any rate limit is exceeded
            - 'block': Wait until all limits can be satisfied (default)
            - 'raise': Raise a RateLimitExceeded exception
            - 'skip': Return None without executing the function
    
    Example:
        >>> # 10 per second, 100 per minute, 1000 per hour
        >>> limiter = MultiRateLimiter(
        ...     limits=[(10, 1), (100, 60), (1000, 3600)],
        ...     on_limit_exceeded=RATE_LIMIT_BLOCK
        ... )
        >>> 
        >>> @limiter
        ... def api_call():
        ...     return "Success"
    """
    
    def __init__(
        self,
        limits: List[Tuple[int, float]],
        on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK
    ):
        if not limits:
            raise ValueError("At least one rate limit must be specified")
        
        self.on_limit_exceeded = on_limit_exceeded
        self.limiters: List[RateLimiter] = []
        
        # Create a RateLimiter for each (limit, period) pair
        for limit, period in limits:
            # Use 'skip' mode for individual limiters since we'll handle blocking here
            self.limiters.append(
                RateLimiter(limit, period, on_limit_exceeded=RATE_LIMIT_SKIP)
            )
        
        self.lock = threading.RLock()
    
    def acquire(self, tokens: int = 1, on_limit_exceeded: RateLimitBehavior | None = None) -> bool:
        """
        Attempt to acquire tokens from all rate limiters.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
            
        Returns:
            True if tokens were acquired from all limiters, False otherwise
            
        Raises:
            RateLimitExceeded: If on_limit_exceeded is 'raise' and any limit is exceeded
        """
        if on_limit_exceeded is None:
            on_limit_exceeded = self.on_limit_exceeded
        with self.lock:
            # Check if all limiters can satisfy the request
            can_proceed = all(limiter.get_available_tokens() >= tokens 
                            for limiter in self.limiters)
            
            if can_proceed:
                # Acquire from all limiters
                for limiter in self.limiters:
                    limiter.acquire(tokens)
                return True
            
            if on_limit_exceeded == RATE_LIMIT_BLOCK:
                # Calculate maximum wait time needed across all limiters
                max_wait_time = 0.0
                for limiter in self.limiters:
                    if limiter.get_available_tokens() < tokens:
                        tokens_needed = tokens - limiter.get_available_tokens()
                        wait_time = tokens_needed * (limiter.period / limiter.limit)
                        max_wait_time = max(max_wait_time, wait_time)
                
                # Release lock while sleeping
                self.lock.release()
                try:
                    time.sleep(max_wait_time)
                finally:
                    self.lock.acquire()
                
                # Try again after waiting
                if all(limiter.get_available_tokens() >= tokens 
                       for limiter in self.limiters):
                    for limiter in self.limiters:
                        limiter.acquire(tokens)
                    return True
                return False
                
            elif on_limit_exceeded == RATE_LIMIT_RAISE:
                # Find which limit was exceeded
                exceeded_limits = []
                for limiter in self.limiters:
                    if limiter.get_available_tokens() < tokens:
                        exceeded_limits.append(
                            f"{limiter.limit} calls per {limiter.period}s"
                        )
                
                raise RateLimitExceeded(
                    f"Rate limit(s) exceeded: {', '.join(exceeded_limits)}"
                )
            else:  # on_limit_exceeded == RATE_LIMIT_SKIP
                return False
    
    def __call__(self, func: Callable) -> Callable:
        """Use as decorator to apply multi-tier rate limiting to a function."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if self.acquire():
                return func(*args, **kwargs)
            return None
        return wrapper
    
    def reset(self) -> None:
        """Reset all rate limiters to their initial state."""
        with self.lock:
            for limiter in self.limiters:
                limiter.reset()
    
    def get_status(self) -> List[Tuple[int, float, float]]:
        """
        Get status of all rate limiters.
        
        Returns:
            List of (limit, period, available_tokens) tuples for each limiter
        """
        with self.lock:
            return [
                (limiter.limit, limiter.period, limiter.get_available_tokens())
                for limiter in self.limiters
            ]
    
    def time_until_ready(self) -> float:
        """
        Calculate time in seconds until all limiters are ready.
        
        Returns:
            Maximum wait time across all limiters
        """
        with self.lock:
            return max(
                limiter.time_until_next_token()
                for limiter in self.limiters
            )


if __name__ == "__main__":
    # Test 1: Basic rate limiting with blocking (default behavior)
    print("Test 1: Rate limit 1 call per second (blocking)")
    @ratelimit(limit=1, period=1)
    def test():
        print(f"  test() called at {time.time():.2f}")

    start = time.time()
    for i in range(5):
        test()
    print(f"  Total time: {time.time() - start:.2f}s (expected ~4s)\n")
    
    # Test 2: Higher rate limit
    print("Test 2: Rate limit 5 calls per second")
    @ratelimit(limit=5, period=1)
    def fast_test():
        print(f"  fast_test() called at {time.time():.2f}")
    
    start = time.time()
    for i in range(10):
        fast_test()
    print(f"  Total time: {time.time() - start:.2f}s (expected ~1s)\n")
    
    # Test 3: Skip behavior
    print("Test 3: Skip when limit exceeded")
    @ratelimit(limit=2, period=1, on_limit_exceeded=RATE_LIMIT_SKIP)
    def skip_test():
        return "executed"
    
    results = [skip_test() for _ in range(5)]
    print(f"  Executed: {sum(1 for r in results if r is not None)} out of 5 calls")
    print(f"  Results: {results}\n")
    
    # Test 4: Multi-tier rate limiting
    print("Test 4: Multi-tier rate limiting (3/sec AND 5/2sec)")
    # 3 per second AND 5 per 2 seconds
    multi_limiter = MultiRateLimiter(
        limits=[(3, 1), (5, 2)],
        on_limit_exceeded=RATE_LIMIT_BLOCK
    )
    
    @multi_limiter
    def api_call():
        return "success"
    
    start = time.time()
    print("  Calling 8 times...")
    for i in range(8):
        result = api_call()
        elapsed = time.time() - start
        print(f"  Call {i+1}: {result} at {elapsed:.2f}s")
    print(f"  Total time: {time.time() - start:.2f}s\n")
    
    # Test 5: Multi-tier with status monitoring
    print("Test 5: Multi-tier with status (10/sec, 50/min, 100/hour)")
    status_limiter = MultiRateLimiter(
        limits=[(10, 1), (50, 60), (100, 3600)],
        on_limit_exceeded=RATE_LIMIT_SKIP
    )
    
    @status_limiter
    def monitored_call():
        return "executed"
    
    # Make some calls
    for i in range(15):
        result = monitored_call()
        if result:
            print(f"  Call {i+1}: Success")
        else:
            print(f"  Call {i+1}: Skipped (rate limit)")
    
    # Check status
    print("\n  Rate limiter status:")
    status = status_limiter.get_status()
    for limit, period, available in status:
        print(f"    {limit}/{period}s: {available:.1f} tokens available")
    
    time_until_ready = status_limiter.time_until_ready()
    print(f"  Time until ready: {time_until_ready:.2f}s\n")
    
    # Test 6: Shared rate limiter across multiple functions
    print("Test 6: Shared rate limiter (5 total calls/sec across all functions)")
    shared = SharedRateLimiter(limit=5, period=1, on_limit_exceeded=RATE_LIMIT_SKIP)
    
    @shared
    def func_a():
        return "A"
    
    @shared
    def func_b():
        return "B"
    
    results = []
    for i in range(10):
        if i % 2 == 0:
            result = func_a()
        else:
            result = func_b()
        if result:
            results.append(result)
    
    print(f"  Executed {len(results)} out of 10 calls")
    print(f"  Results: {results}")