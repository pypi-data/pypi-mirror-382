"""
Enhanced Ringmaster Client with full orchestrator v2 support
"""
import asyncio
from typing import Optional, Callable, Awaitable, Dict, Any, List
from datetime import datetime
import time

from .config import RingmasterConfig
from .models import TravelQuery, TravelPlanResult, SessionStatus, StreamUpdate, HealthStatus, SessionMemory, ConversationHistory
from .auth import AuthManager
from .rate_limiter import RateLimiter
from .retry import RetryHandler
from .cache import ResultCache
from .logger import get_logger, StructuredLogger
from .metrics import MetricsCollector
from .session_manager import SessionManager
from .rest_client import RestClient
from .websocket_client import WebSocketManager
from .exceptions import RingmasterError


StreamCallback = Callable[[StreamUpdate], Awaitable[None]]



class RingmasterClient:
    """
    Production-ready Python SDK for Ringmaster Orchestrator v2
    
    NEW Features in v2:
    - Session memory management and retrieval
    - Conversation history tracking
    - Follow-up query support
    - Incremental updates (budget, itinerary modifications)
    - Extended session management
    
    Example:
        ```python
        from ringmaster_sdk import RingmasterClient, RingmasterConfig
        
        # Initialize client
        config = RingmasterConfig(api_key="your-api-key")
        client = RingmasterClient(config)
        
        # New conversation
        result = await client.submit_query(
            "Plan a 3-day trip to Paris"
        )
        
        # Follow-up query (reuses context)
        result = await client.submit_query(
            "Change my budget to $2000",
            session_id=result.session_id
        )
        
        # Check session memory
        memory = await client.get_session_memory(result.session_id)
        print(f"Destination: {memory.destination}")
        
        # Close client
        await client.close()
        ```
    """
    
    def __init__(self, config: RingmasterConfig):
        """Initialize Ringmaster client"""
        self.config = config
        
        # Initialize logger
        self.logger = get_logger(
            "ringmaster_sdk",
            level=config.log_level,
            format_type=config.log_format
        )
        
        self.logger.info(
            "Initializing Ringmaster SDK v2",
            base_url=config.base_url,
            qps=config.queries_per_second
        )
        
        # Initialize components
        self.auth = AuthManager(api_key=config.api_key)
        self.rate_limiter = RateLimiter(
            queries_per_second=config.queries_per_second,
            burst_size=config.burst_size
        )
        self.retry_handler = RetryHandler(
            max_retries=config.max_retries,
            base_delay=config.retry_base_delay,
            max_delay=config.retry_max_delay,
            multiplier=config.retry_multiplier,
            logger=self.logger
        )
        self.cache = ResultCache(
            max_size=config.cache_max_size,
            ttl=config.cache_ttl
        ) if config.cache_enabled else None
        
        self.metrics = MetricsCollector(
            enabled=config.metrics_enabled
        ) if config.metrics_enabled else None
        
        self.session_manager = SessionManager(
            cache=self.cache if self.cache else ResultCache(max_size=10, ttl=3600),
            logger=self.logger
        )
        
        # Initialize API clients with v2 base path
        api_base_url = f"{config.base_url}/api/v2/orchestrator"
        
        self.rest = RestClient(
            base_url=api_base_url,
            auth_manager=self.auth,
            retry_handler=self.retry_handler,
            rate_limiter=self.rate_limiter,
            logger=self.logger,
            timeout=config.request_timeout
        )
        
        # WebSocket uses different base (ws:// instead of http://)
        ws_base_url = config.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_base_url = f"{ws_base_url}/api/v2/orchestrator/ws"
        
        self.websocket = WebSocketManager(
            base_url=ws_base_url,
            auth_manager=self.auth,
            logger=self.logger,
            timeout=config.websocket_timeout
        )
        
        self._closed = False
        
        self.logger.info("Ringmaster SDK v2 initialized successfully")
    
    async def submit_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        force_new_session: bool = False,
        stream_callback: Optional[StreamCallback] = None,
        wait_for_completion: bool = True
    ) -> TravelPlanResult:
        """
        Submit a travel query with session memory support
        
        Args:
            query: Natural language travel query
            session_id: Optional session ID (for follow-ups)
            user_id: Optional user ID
            force_new_session: Force new session ignoring existing memory
            stream_callback: Optional callback for streaming updates
            wait_for_completion: Whether to wait for completion
        
        Returns:
            Travel plan result
        
        Example:
            ```python
            # New conversation
            result = await client.submit_query(
                "Plan a trip to Tokyo for 5 days"
            )
            
            # Follow-up (reuses context)
            result2 = await client.submit_query(
                "Change budget to $3000",
                session_id=result.session_id
            )
            ```
        """
        self._check_not_closed()
        
        start_time = time.time()
        
        # Build request payload
        payload = {
            "query": query,
            "session_id": session_id,
            "user_id": user_id,
            "force_new_session": force_new_session
        }
        
        self.logger.info(
            "Submitting travel query",
            query_length=len(query),
            session_id=session_id,
            is_follow_up=session_id is not None
        )
        
        if self.metrics:
            self.metrics.record_session_created()
        
        try:
            # Subscribe to streaming updates if callback provided
            if stream_callback and session_id:
                await self._setup_streaming(session_id, stream_callback)
            
            # Submit query via REST API (POST /plan)
            result = await self.rest.post("/plan", json=payload)
            
            result_session_id = result.get("session_id")
            
            # Setup streaming for new session if callback provided
            if stream_callback and not session_id and result_session_id:
                await self._setup_streaming(result_session_id, stream_callback)
            
            # Register session
            await self.session_manager.register_session(result_session_id)
            
            # Wait for completion if requested
            if wait_for_completion and result.get("status") != "completed":
                result = await self._wait_for_completion(
                    result_session_id,
                    timeout=self.config.request_timeout * 3
                )
            
            # Cache result if completed
            if self.cache and result.get("status") == "completed":
                self.cache.set_result(result_session_id, result)
            
            # Update session manager
            if result.get("status") == "completed":
                await self.session_manager.complete_session(result_session_id, result)
                if self.metrics:
                    duration = time.time() - start_time
                    self.metrics.record_session_completed(duration)
            elif result.get("status") == "failed":
                await self.session_manager.fail_session(
                    result_session_id,
                    ", ".join(result.get("errors", []))
                )
                if self.metrics:
                    self.metrics.record_session_failed()
            
            # Record metrics
            if self.metrics:
                latency_ms = (time.time() - start_time) * 1000
                self.metrics.record_request(success=True, latency_ms=latency_ms)
            
            self.logger.info(
                "Query submitted successfully",
                session_id=result_session_id,
                status=result.get("status"),
                is_follow_up=result.get("is_follow_up", False)
            )
            
            return TravelPlanResult(**result)
            
        except Exception as e:
            self.logger.error(
                "Failed to submit query",
                error=e,
                session_id=session_id
            )
            
            if self.metrics:
                latency_ms = (time.time() - start_time) * 1000
                self.metrics.record_request(
                    success=False,
                    latency_ms=latency_ms,
                    error_type=type(e).__name__
                )
            
            raise
    
    # NEW: Memory management methods
    
    async def get_session_memory(self, session_id: str) -> SessionMemory:
        """
        Get session memory and context
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session memory information
        
        Example:
            ```python
            memory = await client.get_session_memory("session_abc123")
            if memory.exists:
                print(f"Destination: {memory.destination}")
                print(f"Turns: {memory.conversation_turns}")
            ```
        """
        self._check_not_closed()
        
        try:
            result = await self.rest.get(f"/session/{session_id}/memory")
            return SessionMemory(result)
        except Exception as e:
            self.logger.error(f"Failed to get session memory: {e}")
            raise
    
    async def get_conversation_history(self, session_id: str) -> ConversationHistory:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Conversation history
        
        Example:
            ```python
            history = await client.get_conversation_history("session_abc123")
            for msg in history.history:
                print(f"{msg['role']}: {msg['content']}")
            ```
        """
        self._check_not_closed()
        
        try:
            result = await self.rest.get(f"/session/{session_id}/history")
            return ConversationHistory(result)
        except Exception as e:
            self.logger.error(f"Failed to get conversation history: {e}")
            raise
    
    async def extend_session(self, session_id: str, hours: int = 24) -> Dict[str, Any]:
        """
        Extend session memory TTL
        
        Args:
            session_id: Session identifier
            hours: Hours to extend (1-168)
        
        Returns:
            Extension confirmation
        
        Example:
            ```python
            await client.extend_session("session_abc123", hours=48)
            ```
        """
        self._check_not_closed()
        
        try:
            result = await self.rest.put(
                f"/session/{session_id}/extend",
                json={"hours": hours}
            )
            return result
        except Exception as e:
            self.logger.error(f"Failed to extend session: {e}")
            raise
    
    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Delete a session and its memory
        
        Args:
            session_id: Session identifier
        
        Returns:
            Deletion confirmation
        
        Example:
            ```python
            await client.delete_session("session_abc123")
            ```
        """
        self._check_not_closed()
        
        try:
            result = await self.rest.delete(f"/session/{session_id}")
            
            # Remove from local cache and session manager
            await self.session_manager.remove_session(session_id)
            if self.cache:
                self.cache.invalidate_session(session_id)
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to delete session: {e}")
            raise
    
    # Updated methods
    
    async def _setup_streaming(
        self,
        session_id: str,
        callback: StreamCallback
    ) -> None:
        """Setup WebSocket streaming for a session"""
        if self.metrics:
            self.metrics.record_websocket_connection()
        
        # Wrap callback to update session manager
        async def wrapped_callback(update: StreamUpdate):
            await self.session_manager.update_session(session_id, update)
            await callback(update)
        
        # Connect to WebSocket endpoint: /ws/{session_id}
        await self.websocket.subscribe(f"/{session_id}", wrapped_callback)
    
    async def _wait_for_completion(
        self,
        session_id: str,
        timeout: float = 90.0,
        poll_interval: float = 2.0
    ) -> Dict[str, Any]:
        """Wait for session to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if result is in cache
            if self.cache:
                cached_result = self.cache.get_result(session_id)
                if cached_result and cached_result.get("status") in ["completed", "failed"]:
                    return cached_result
            
            # Poll status
            try:
                status = await self.get_status(session_id)
                
                if status.status == "completed":
                    result = await self.get_result(session_id)
                    return result
                elif status.status == "failed":
                    result = await self.get_result(session_id)
                    return result
                
            except Exception as e:
                self.logger.warning(
                    "Error polling session status",
                    error=e,
                    session_id=session_id
                )
            
            await asyncio.sleep(poll_interval)
        
        raise TimeoutError(
            f"Session {session_id} did not complete within {timeout}s"
        )
    
    async def get_status(self, session_id: str) -> SessionStatus:
        """
        Get the current status of a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session status
        """
        self._check_not_closed()
        
        start_time = time.time()
        
        try:
            # GET /session/{session_id}/status
            status_data = await self.rest.get(f"/session/{session_id}/status")
            
            # Cache status
            if self.cache:
                self.cache.set_status(session_id, status_data)
            
            # Record metrics
            if self.metrics:
                latency_ms = (time.time() - start_time) * 1000
                self.metrics.record_request(success=True, latency_ms=latency_ms)
            
            return SessionStatus(**status_data)
            
        except Exception as e:
            if self.metrics:
                latency_ms = (time.time() - start_time) * 1000
                self.metrics.record_request(
                    success=False,
                    latency_ms=latency_ms,
                    error_type=type(e).__name__
                )
            raise
    
    async def get_result(self, session_id: str) -> TravelPlanResult:
        """
        Get the result of a completed session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Travel plan result
        """
        self._check_not_closed()
        
        start_time = time.time()
        
        try:
            # GET /session/{session_id}/result
            result = await self.rest.get(f"/session/{session_id}/result")
            
            # Cache result
            if self.cache:
                self.cache.set_result(session_id, result)
            
            # Record metrics
            if self.metrics:
                latency_ms = (time.time() - start_time) * 1000
                self.metrics.record_request(success=True, latency_ms=latency_ms)
            
            return TravelPlanResult(**result)
            
        except Exception as e:
            if self.metrics:
                latency_ms = (time.time() - start_time) * 1000
                self.metrics.record_request(
                    success=False,
                    latency_ms=latency_ms,
                    error_type=type(e).__name__
                )
            raise
    
    async def cancel_session(self, session_id: str) -> Dict[str, str]:
        """
        Cancel an active session (alias for delete_session)
        
        Args:
            session_id: Session identifier
        
        Returns:
            Cancellation confirmation
        """
        return await self.delete_session(session_id)
    
    async def listen_stream(
        self,
        session_id: str,
        callback: StreamCallback
    ) -> None:
        """
        Listen to streaming updates for a session
        
        Args:
            session_id: Session identifier
            callback: Async callback for updates
        """
        self._check_not_closed()
        
        await self._setup_streaming(session_id, callback)
    
    async def health_check(self) -> HealthStatus:
        """
        Perform health check on the API
        
        Returns:
            Health status
        """
        self._check_not_closed()
        # GET /health
        result = await self.rest.get("/health")
        return HealthStatus(**result)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get SDK metrics
        
        Returns:
            Dictionary with metrics data
        """
        if not self.metrics:
            return {"enabled": False}
        
        metrics = self.metrics.get_metrics()
        
        # Add cache stats
        if self.cache:
            metrics["cache"].update(self.cache.get_stats())
        
        # Add rate limiter stats
        metrics["rate_limiter"] = self.rate_limiter.get_status()
        
        # Add session stats
        metrics["session_manager"] = self.session_manager.get_statistics()
        
        return metrics
    
    def _check_not_closed(self):
        """Check if client has been closed"""
        if self._closed:
            raise RingmasterError("Client has been closed")
    
    async def close(self):
        """Close the client and cleanup resources"""
        if self._closed:
            return
        
        self.logger.info("Closing Ringmaster SDK")
        
        # Close WebSocket connections
        await self.websocket.close_all()
        
        # Close REST client
        await self.rest.close()
        
        self._closed = True
        
        self.logger.info("Ringmaster SDK closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()