"""
Simple retry logic for LayData.

Provides exponential backoff retry for external API calls,
specifically designed for internal use with Teable API.
"""

import asyncio
import random
import time
from typing import Callable, Any, Optional
from laydata_core.config import config
from laydata_core.logger import get_logger

logger = get_logger(__name__)


async def retry_with_backoff(
    func: Callable,
    max_attempts: int = None,
    base_delay: float = None,
    *args, **kwargs
) -> Any:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts (defaults to config)
        base_delay: Base delay in seconds (defaults to config)
        *args, **kwargs: Arguments to pass to func
    """
    max_attempts = max_attempts or config.RETRY_MAX_ATTEMPTS
    base_delay = base_delay or config.RETRY_BASE_DELAY
    
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            result = await func(*args, **kwargs)
            if attempt > 0:
                logger.info(f"Retry succeeded on attempt {attempt + 1}")
            return result
            
        except Exception as e:
            last_exception = e
            
            # Don't retry on certain errors
            if hasattr(e, 'status_code'):
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.status_code < 500:
                    logger.debug(f"Not retrying 4xx error: {e}")
                    raise
            
            # Last attempt, don't wait
            if attempt == max_attempts - 1:
                break
                
            # Calculate delay with exponential backoff and jitter
            delay = base_delay * (2 ** attempt)
            if config.RETRY_JITTER:
                delay *= (0.5 + random.random())  # Add 50-150% jitter
                
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
            await asyncio.sleep(delay)
    
    # All attempts failed
    logger.error(f"All {max_attempts} attempts failed. Last error: {last_exception}")
    raise last_exception


def retry_on_failure(max_attempts: int = None, base_delay: float = None):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                func, max_attempts, base_delay, *args, **kwargs
            )
        return wrapper
    return decorator


def should_retry_error(error: Exception) -> bool:
    """Determine if an error should trigger a retry."""
    # Don't retry on client errors (4xx)
    if hasattr(error, 'status_code'):
        if 400 <= error.status_code < 500:
            return False
            
    # Retry on server errors (5xx) and network errors
    if hasattr(error, 'status_code'):
        if error.status_code >= 500:
            return True
    
    # Retry on common network/timeout errors
    error_str = str(error).lower()
    retry_keywords = [
        'timeout', 'connection', 'network', 'temporary', 
        'unavailable', 'service', 'server'
    ]
    
    return any(keyword in error_str for keyword in retry_keywords)