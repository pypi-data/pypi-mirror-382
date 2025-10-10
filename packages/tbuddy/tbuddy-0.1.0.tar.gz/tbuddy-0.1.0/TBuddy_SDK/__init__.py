"""
Ringmaster SDK - Production-Ready Python Client for Multi-Agent Orchestrator

A comprehensive SDK for interacting with the Ringmaster travel planning platform,
featuring REST API, WebSocket streaming, rate limiting, caching, and observability.

Example:
    ```python
    from ringmaster_sdk import RingmasterClient, RingmasterConfig
    
    # Initialize client
    config = RingmasterConfig(
        api_key="your-api-key",
        base_url="https://api.ringmaster.com"
    )
    
    async with RingmasterClient(config) as client:
        # Submit query with streaming
        async def on_update(update):
            print(f"Progress: {update.progress_percent}%")
        
        result = await client.submit_query(
            "Plan a 3-day trip to Paris",
            stream_callback=on_update
        )
        
        print(f"Destination: {result.destination}")
    ```
"""

__version__ = "1.0.0"
__author__ = "Ringmaster Team"
__license__ = "MIT"

from .client import RingmasterClient
from .config import RingmasterConfig
from .models import (
    TravelQuery,
    TravelPlanResult,
    SessionStatus,
    StreamUpdate,
    HealthStatus
)
from .exceptions import (
    RingmasterError,
    AuthenticationError,
    RateLimitError,
    SessionNotFoundError,
    SessionNotCompletedError,
    ValidationError,
    NetworkError,
    TimeoutError,
    WebSocketError,
    RetryExhaustedError
)

__all__ = [
    # Main client
    "RingmasterClient",
    "RingmasterConfig",
    
    # Models
    "TravelQuery",
    "TravelPlanResult",
    "SessionStatus",
    "StreamUpdate",
    "HealthStatus",
    
    # Exceptions
    "RingmasterError",
    "AuthenticationError",
    "RateLimitError",
    "SessionNotFoundError",
    "SessionNotCompletedError",
    "ValidationError",
    "NetworkError",
    "TimeoutError",
    "WebSocketError",
    "RetryExhaustedError",
]