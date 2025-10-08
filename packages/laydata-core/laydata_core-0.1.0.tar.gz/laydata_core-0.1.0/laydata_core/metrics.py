"""
Metrics and performance monitoring for LayData.

Simple metrics collection for internal use - tracks request latency,
error rates, and Teable API performance.
"""

import time
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from threading import RLock
from collections import defaultdict, deque
from laydata_core.config import config
from laydata_core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RequestMetric:
    """Single request metric."""
    timestamp: float
    endpoint: str
    method: str
    duration_ms: float
    status_code: int
    error: Optional[str] = None


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for an endpoint."""
    total_requests: int = 0
    total_duration_ms: float = 0
    error_count: int = 0
    status_codes: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    
    @property
    def avg_duration_ms(self) -> float:
        return self.total_duration_ms / self.total_requests if self.total_requests > 0 else 0
    
    @property
    def error_rate(self) -> float:
        return self.error_count / self.total_requests if self.total_requests > 0 else 0


class MetricsCollector:
    """Simple metrics collector for internal use."""
    
    def __init__(self, max_recent_metrics: int = 1000):
        self._lock = RLock()
        self._recent_metrics: deque = deque(maxlen=max_recent_metrics)
        self._aggregated: Dict[str, AggregatedMetrics] = defaultdict(AggregatedMetrics)
        self._start_time = time.time()
    
    def record_request(self, endpoint: str, method: str, duration_ms: float, 
                      status_code: int, error: str = None):
        """Record a request metric."""
        if not config.ENABLE_METRICS:
            return
            
        metric = RequestMetric(
            timestamp=time.time(),
            endpoint=endpoint,
            method=method,
            duration_ms=duration_ms,
            status_code=status_code,
            error=error
        )
        
        with self._lock:
            self._recent_metrics.append(metric)
            
            # Update aggregated metrics
            key = f"{method} {endpoint}"
            agg = self._aggregated[key]
            agg.total_requests += 1
            agg.total_duration_ms += duration_ms
            agg.status_codes[status_code] += 1
            
            if error or status_code >= 400:
                agg.error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics statistics."""
        with self._lock:
            uptime_seconds = time.time() - self._start_time
            
            # Recent metrics (last 100)
            recent = list(self._recent_metrics)[-100:]
            
            # Calculate recent averages
            recent_duration = sum(m.duration_ms for m in recent) / len(recent) if recent else 0
            recent_errors = sum(1 for m in recent if m.error or m.status_code >= 400)
            recent_error_rate = recent_errors / len(recent) if recent else 0
            
            # Top slow endpoints
            endpoint_times = defaultdict(list)
            for m in recent:
                endpoint_times[f"{m.method} {m.endpoint}"].append(m.duration_ms)
            
            slow_endpoints = sorted(
                [(endpoint, sum(times)/len(times)) for endpoint, times in endpoint_times.items()],
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return {
                "uptime_seconds": uptime_seconds,
                "total_metrics_collected": len(self._recent_metrics),
                "recent_avg_duration_ms": round(recent_duration, 2),
                "recent_error_rate": round(recent_error_rate, 3),
                "aggregated_by_endpoint": {
                    endpoint: {
                        "total_requests": agg.total_requests,
                        "avg_duration_ms": round(agg.avg_duration_ms, 2),
                        "error_rate": round(agg.error_rate, 3),
                        "status_codes": dict(agg.status_codes)
                    }
                    for endpoint, agg in self._aggregated.items()
                },
                "slowest_endpoints": slow_endpoints
            }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a simple health summary for /health endpoint."""
        with self._lock:
            recent = list(self._recent_metrics)[-50:]  # Last 50 requests
            
            if not recent:
                return {"status": "ok", "message": "No recent metrics"}
            
            avg_duration = sum(m.duration_ms for m in recent) / len(recent)
            error_count = sum(1 for m in recent if m.error or m.status_code >= 400)
            error_rate = error_count / len(recent)
            
            # Determine health status
            status = "ok"
            issues = []
            
            if avg_duration > 5000:  # 5 seconds
                status = "degraded"
                issues.append("High average response time")
                
            if error_rate > 0.1:  # 10% error rate
                status = "degraded" 
                issues.append("High error rate")
            
            return {
                "status": status,
                "avg_duration_ms": round(avg_duration, 2),
                "error_rate": round(error_rate, 3),
                "issues": issues
            }


# Global metrics collector
metrics = MetricsCollector() if config.ENABLE_METRICS else None


def track_request(endpoint: str, method: str = "GET"):
    """Decorator to track request metrics."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            if not config.ENABLE_METRICS or metrics is None:
                return await func(*args, **kwargs)
            
            start_time = time.time()
            error = None
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_request(endpoint, method, duration_ms, status_code, error)
        
        def sync_wrapper(*args, **kwargs):
            if not config.ENABLE_METRICS or metrics is None:
                return func(*args, **kwargs)
            
            start_time = time.time()
            error = None
            status_code = 200
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_request(endpoint, method, duration_ms, status_code, error)
        
        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator


def track_teable_call(operation: str):
    """Decorator specifically for tracking Teable API calls."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            if not config.ENABLE_METRICS or metrics is None:
                return await func(*args, **kwargs)
            
            start_time = time.time()
            error = None
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = f"Teable API error: {str(e)}"
                # Try to extract status code from exception if it's an HTTP error
                if hasattr(e, 'status_code'):
                    status_code = e.status_code
                else:
                    status_code = 500
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_request(f"teable/{operation}", "API", duration_ms, status_code, error)
                
                # Log slow Teable calls
                if duration_ms > 2000:  # 2 seconds
                    logger.warning(f"Slow Teable API call: {operation} took {duration_ms:.1f}ms")
        
        return async_wrapper
    return decorator