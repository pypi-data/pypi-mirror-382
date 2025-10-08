import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Core settings
    TEABLE_BASE_URL: str = os.getenv("TEABLE_BASE_URL", "http://localhost:3000/api")
    TEABLE_TOKEN: str = os.getenv("TEABLE_TOKEN", "")
    LAYDATA_ENV: str = os.getenv("LAYDATA_ENV", "dev")
    LAYDATA_VERSION: str = os.getenv("LAYDATA_VERSION", "0.1.0")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    # Retry settings (simple for internal use)
    RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    RETRY_BASE_DELAY: float = float(os.getenv("RETRY_BASE_DELAY", "1.0"))  # seconds
    RETRY_JITTER: bool = os.getenv("RETRY_JITTER", "true").lower() == "true"
    
    # Timeout settings for different operation types
    HTTP_TIMEOUT_CONNECT: float = float(os.getenv("HTTP_TIMEOUT_CONNECT", "10.0"))  # Connect timeout
    HTTP_TIMEOUT_READ_BASIC: float = float(os.getenv("HTTP_TIMEOUT_READ_BASIC", "30.0"))  # Basic operations
    HTTP_TIMEOUT_READ_ATTACHMENT: float = float(os.getenv("HTTP_TIMEOUT_READ_ATTACHMENT", "600.0"))  # 10 minutes for attachments
    HTTP_TIMEOUT_WRITE: float = float(os.getenv("HTTP_TIMEOUT_WRITE", "120.0"))  # Write timeout
    HTTP_TIMEOUT_POOL: float = float(os.getenv("HTTP_TIMEOUT_POOL", "10.0"))  # Pool timeout
    
    # Connection pool settings for high load
    HTTP_MAX_KEEPALIVE: int = int(os.getenv("HTTP_MAX_KEEPALIVE", "20"))  # More keepalive connections
    HTTP_MAX_CONNECTIONS: int = int(os.getenv("HTTP_MAX_CONNECTIONS", "100"))  # Higher connection limit
    HTTP_KEEPALIVE_EXPIRY: float = float(os.getenv("HTTP_KEEPALIVE_EXPIRY", "60.0"))  # Longer keepalive
    
    # Attachment handling settings (no size limits)
    ATTACHMENT_BASE_TIMEOUT: float = float(os.getenv("ATTACHMENT_BASE_TIMEOUT", "60.0"))  # Base timeout for attachments
    ATTACHMENT_MAX_TIMEOUT: float = float(os.getenv("ATTACHMENT_MAX_TIMEOUT", "1800.0"))  # 30 minutes max for any size
    
    # Client retry settings
    CLIENT_RETRY_MAX_ATTEMPTS: int = int(os.getenv("CLIENT_RETRY_MAX_ATTEMPTS", "1"))  # More attempts for attachments
    CLIENT_RETRY_BASE_DELAY: float = float(os.getenv("CLIENT_RETRY_BASE_DELAY", "2.0"))
    CLIENT_RETRY_MAX_DELAY: float = float(os.getenv("CLIENT_RETRY_MAX_DELAY", "120.0"))  # Longer max delay
    
    # Metrics settings
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"

    # Singleflight/Idempotency settings
    SINGLEFLIGHT_LOCK_TIMEOUT: float = float(os.getenv("SINGLEFLIGHT_LOCK_TIMEOUT", "10.0"))
    SINGLEFLIGHT_WAIT_TIMEOUT: float = float(os.getenv("SINGLEFLIGHT_WAIT_TIMEOUT", "20.0"))
    SINGLEFLIGHT_POLL_INTERVAL: float = float(os.getenv("SINGLEFLIGHT_POLL_INTERVAL", "0.5"))
    SINGLEFLIGHT_RECENT_TTL: float = float(os.getenv("SINGLEFLIGHT_RECENT_TTL", "5.0"))


config = Config()

