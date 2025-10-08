import httpx
from laydata_core.config import config
from urllib.parse import urlparse
from laydata_core.logger import get_logger

logger = get_logger(__name__)


def init_teable_http_client() -> httpx.AsyncClient:
    headers = {}
    if config.TEABLE_TOKEN:
        headers["Authorization"] = f"Bearer {config.TEABLE_TOKEN}"

    # Normalize TEABLE_BASE_URL to host root so both .../api and host-only inputs work.
    parsed = urlparse(config.TEABLE_BASE_URL)
    base_root = f"{parsed.scheme}://{parsed.netloc}"
    
    # Configure connection limits and timeouts for high-load scenarios
    limits = httpx.Limits(
        max_keepalive_connections=config.HTTP_MAX_KEEPALIVE,
        max_connections=config.HTTP_MAX_CONNECTIONS,
        keepalive_expiry=config.HTTP_KEEPALIVE_EXPIRY
    )
    
    # Set timeouts optimized for Teable operations (including attachments)
    timeout = httpx.Timeout(
        connect=config.HTTP_TIMEOUT_CONNECT,
        read=config.HTTP_TIMEOUT_READ_ATTACHMENT,  # Use attachment timeout for Teable
        write=config.HTTP_TIMEOUT_WRITE,
        pool=config.HTTP_TIMEOUT_POOL
    )
    
    logger.debug(f"Initializing Teable HTTP client for {base_root}")
    
    return httpx.AsyncClient(
        base_url=base_root,
        headers=headers,
        timeout=timeout,
        limits=limits,
        follow_redirects=True,
        http2=True  # Enable HTTP/2 for better performance
    )


def init_laydata_client(endpoint: str, token: str | None = None) -> httpx.AsyncClient:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Optimized settings for LayData client
    limits = httpx.Limits(
        max_keepalive_connections=config.HTTP_MAX_KEEPALIVE // 2,  # Half of server settings
        max_connections=config.HTTP_MAX_CONNECTIONS // 2,
        keepalive_expiry=config.HTTP_KEEPALIVE_EXPIRY
    )
    
    # Client timeout should be slightly higher than server to avoid client timeouts
    timeout = httpx.Timeout(
        connect=config.HTTP_TIMEOUT_CONNECT,
        read=config.HTTP_TIMEOUT_READ_ATTACHMENT + 30.0,  # Extra 30s buffer
        write=config.HTTP_TIMEOUT_WRITE,
        pool=config.HTTP_TIMEOUT_POOL
    )
    
    logger.debug(f"Initializing LayData client for {endpoint}")
    
    return httpx.AsyncClient(
        base_url=endpoint,
        headers=headers,
        timeout=timeout,
        limits=limits,
        follow_redirects=True,
        http2=True
    )

