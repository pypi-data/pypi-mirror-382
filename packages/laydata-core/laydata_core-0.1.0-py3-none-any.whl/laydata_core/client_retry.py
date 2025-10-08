"""
Client-level retry system for LayData operations.

Handles timeouts, network errors, and attachment-specific retry logic
for operations between LayData client and server.
"""

import asyncio
import random
import time
from typing import Callable, Any, Optional, Dict, List
import httpx
from laydata_core.config import config
from laydata_core.logger import get_logger

logger = get_logger(__name__)


class ClientRetryError(Exception):
    """Raised when all client retry attempts are exhausted."""
    pass


def is_retryable_error(error: Exception) -> bool:
    """Determine if a client error should trigger a retry."""
    # Always retry timeout errors
    if isinstance(error, (httpx.TimeoutException, httpx.ReadTimeout, httpx.WriteTimeout, httpx.ConnectTimeout)):
        return True
    
    # Retry connection errors
    if isinstance(error, (httpx.ConnectError, httpx.NetworkError)):
        return True
    
    # Retry on server errors (5xx)
    if isinstance(error, httpx.HTTPStatusError):
        if error.response.status_code >= 500:
            return True
        # Don't retry client errors (4xx)
        return False
    
    # Retry on common network issues
    error_str = str(error).lower()
    retry_keywords = [
        'timeout', 'connection reset', 'connection aborted', 
        'network unreachable', 'temporary failure', 'service unavailable'
    ]
    
    return any(keyword in error_str for keyword in retry_keywords)


def has_attachments(data: Any) -> bool:
    """Check if the operation involves attachments."""
    if isinstance(data, dict):
        # Check for attachment-like patterns in the data
        for key, value in data.items():
            if key.lower() in ['attachment', 'attachments', 'file', 'files', 'document', 'documents']:
                return True
            if isinstance(value, str) and any(ext in value.lower() for ext in ['.jpg', '.png', '.pdf', '.docx', '.txt']):
                return True
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and any(ext in item.lower() for ext in ['.jpg', '.png', '.pdf', '.docx', '.txt']):
                        return True
    return False


def calculate_retry_delay(attempt: int, base_delay: float, max_delay: float, jitter: bool = True) -> float:
    """Calculate delay with exponential backoff and jitter."""
    delay = base_delay * (2 ** attempt)
    delay = min(delay, max_delay)
    
    if jitter:
        # Add ±25% jitter
        jitter_range = delay * 0.25
        delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0, delay)


async def retry_with_client_backoff(
    operation_func: Callable,
    operation_name: str = "operation",
    max_attempts: Optional[int] = None,
    base_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    is_attachment_operation: bool = False,
    *args, **kwargs
) -> Any:
    """
    Retry a client operation with exponential backoff.
    
    Args:
        operation_func: The async function to retry
        operation_name: Name for logging purposes
        max_attempts: Maximum retry attempts (uses config default if None)
        base_delay: Base delay in seconds (uses config default if None)
        max_delay: Maximum delay in seconds (uses config default if None)
        is_attachment_operation: Whether this involves attachments (for better logging)
        *args, **kwargs: Arguments to pass to operation_func
    """
    max_attempts = max_attempts or config.CLIENT_RETRY_MAX_ATTEMPTS
    base_delay = base_delay or config.CLIENT_RETRY_BASE_DELAY
    max_delay = max_delay or config.CLIENT_RETRY_MAX_DELAY
    
    last_exception = None
    operation_type = "attachment operation" if is_attachment_operation else "operation"
    
    for attempt in range(max_attempts):
        try:
            start_time = time.time()
            result = await operation_func(*args, **kwargs)
            
            if attempt > 0:
                duration = time.time() - start_time
                logger.info(f"Client retry succeeded on attempt {attempt + 1} for {operation_name} ({duration*1000:.1f}ms)")
            
            return result
            
        except Exception as e:
            last_exception = e
            
            # Check if we should retry this error
            if not is_retryable_error(e):
                logger.debug(f"Client retry: Not retrying non-retryable error for {operation_name}: {e}")
                raise
            
            # If this is the last attempt, don't wait
            if attempt == max_attempts - 1:
                break
            
            # Calculate delay
            delay = calculate_retry_delay(attempt, base_delay, max_delay)
            
            # Log the retry attempt
            error_type = type(e).__name__
            if is_attachment_operation:
                logger.warning(f"Attachment {operation_name} failed on attempt {attempt + 1}/{max_attempts} ({error_type}). Retrying in {delay:.1f}s...")
            else:
                logger.warning(f"Client {operation_name} failed on attempt {attempt + 1}/{max_attempts} ({error_type}). Retrying in {delay:.1f}s...")
            
            # Wait before retry
            await asyncio.sleep(delay)
    
    # All attempts failed
    error_msg = f"All {max_attempts} client retry attempts failed for {operation_name}. Last error: {last_exception}"
    logger.error(error_msg)
    
    # Wrap in our custom exception
    raise ClientRetryError(error_msg) from last_exception


def client_retry(
    operation_name: str = None,
    max_attempts: int = None,
    base_delay: float = None,
    max_delay: float = None,
    check_attachments: bool = True
):
    """
    Decorator for adding client-level retry logic to async functions.
    
    Args:
        operation_name: Name of the operation for logging
        max_attempts: Maximum retry attempts
        base_delay: Base delay between retries
        max_delay: Maximum delay between retries
        check_attachments: Whether to auto-detect attachment operations
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Auto-detect operation name from function if not provided
            op_name = operation_name or func.__name__
            
            # Auto-detect attachment operations if enabled
            is_attachment_op = False
            if check_attachments:
                # Check args and kwargs for attachment indicators
                all_args = list(args) + list(kwargs.values())
                is_attachment_op = any(has_attachments(arg) for arg in all_args)
            
            return await retry_with_client_backoff(
                func,
                op_name,
                max_attempts,
                base_delay,
                max_delay,
                is_attachment_op,
                *args, **kwargs
            )
        
        return wrapper
    return decorator


class ClientRetryStats:
    """Track retry statistics for monitoring."""
    
    def __init__(self):
        self._stats = {
            'total_operations': 0,
            'retried_operations': 0,
            'failed_operations': 0,
            'retry_reasons': {},
            'attachment_operations': 0,
            'attachment_retries': 0
        }
    
    def record_operation(self, succeeded: bool, retries: int, error_type: str = None, is_attachment: bool = False):
        """Record operation statistics."""
        self._stats['total_operations'] += 1
        
        if is_attachment:
            self._stats['attachment_operations'] += 1
        
        if retries > 0:
            self._stats['retried_operations'] += 1
            if is_attachment:
                self._stats['attachment_retries'] += 1
        
        if not succeeded:
            self._stats['failed_operations'] += 1
            if error_type:
                self._stats['retry_reasons'][error_type] = self._stats['retry_reasons'].get(error_type, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        stats = self._stats.copy()
        if stats['total_operations'] > 0:
            stats['retry_rate'] = stats['retried_operations'] / stats['total_operations']
            stats['failure_rate'] = stats['failed_operations'] / stats['total_operations']
        else:
            stats['retry_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        return stats


# Global retry statistics
client_retry_stats = ClientRetryStats()