"""
Session state management for Ringmaster SDK (Enhanced for v2)
"""
import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable, List
from datetime import datetime
from .models import TravelPlanResult, SessionStatus, StreamUpdate
from .cache import ResultCache
from .logger import StructuredLogger


SessionUpdateCallback = Callable[[str, StreamUpdate], Awaitable[None]]


class SessionInfo:
    """Enhanced session information with v2 features"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.utcnow()
        self.last_update = datetime.utcnow()
        self.status = "initialized"
        self.progress = 0
        self.updates_received = 0
        
        # NEW: v2 fields
        self.is_follow_up = False
        self.conversation_turns = 0
        self.update_type: Optional[str] = None  # budget_update, itinerary_update, etc.
        self.destination: Optional[str] = None
        self.travel_dates: List[str] = []
        self.has_itinerary = False
        self.has_budget = False
        
        # Agent tracking
        self.completed_agents: List[str] = []
        self.pending_agents: List[str] = []
        self.failed_agents: List[str] = []
        
        # Error tracking
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_update": self.last_update.isoformat(),
            "status": self.status,
            "progress": self.progress,
            "updates_received": self.updates_received,
            "is_follow_up": self.is_follow_up,
            "conversation_turns": self.conversation_turns,
            "update_type": self.update_type,
            "destination": self.destination,
            "travel_dates": self.travel_dates,
            "has_itinerary": self.has_itinerary,
            "has_budget": self.has_budget,
            "completed_agents": self.completed_agents,
            "pending_agents": self.pending_agents,
            "failed_agents": self.failed_agents,
            "error": self.error
        }


class SessionManager:
    """
    Manages multiple session states and subscriptions (Enhanced for v2)
    
    NEW Features:
    - Tracks follow-up status and conversation turns
    - Monitors update types (budget, itinerary, etc.)
    - Per-agent progress tracking
    - Enhanced statistics with v2 metrics
    """
    
    def __init__(
        self,
        cache: ResultCache,
        logger: StructuredLogger
    ):
        """
        Initialize session manager
        
        Args:
            cache: Result cache instance
            logger: Structured logger
        """
        self.cache = cache
        self.logger = logger
        
        # Track active sessions with enhanced info
        self._sessions: Dict[str, SessionInfo] = {}
        self._session_callbacks: Dict[str, list[SessionUpdateCallback]] = {}
        self._lock = asyncio.Lock()
    
    async def register_session(
        self,
        session_id: str,
        initial_status: Optional[SessionStatus] = None,
        is_follow_up: bool = False
    ) -> None:
        """
        Register a new session
        
        Args:
            session_id: Session identifier
            initial_status: Optional initial status
            is_follow_up: Whether this is a follow-up query
        """
        async with self._lock:
            if session_id not in self._sessions:
                session_info = SessionInfo(session_id)
                session_info.is_follow_up = is_follow_up
                
                if initial_status:
                    session_info.status = initial_status.status
                    session_info.progress = initial_status.progress_percent
                    
                    # Extract agent info
                    if hasattr(initial_status, 'completed_agents'):
                        session_info.completed_agents = initial_status.completed_agents
                    if hasattr(initial_status, 'pending_agents'):
                        session_info.pending_agents = initial_status.pending_agents
                
                self._sessions[session_id] = session_info
                
                self.logger.info(
                    "Session registered",
                    session_id=session_id,
                    is_follow_up=is_follow_up
                )
    
    async def update_session(
        self,
        session_id: str,
        update: StreamUpdate
    ) -> None:
        """
        Update session with new stream update
        
        Args:
            session_id: Session identifier
            update: Stream update
        """
        async with self._lock:
            if session_id not in self._sessions:
                # Auto-register if not exists
                self._sessions[session_id] = SessionInfo(session_id)
            
            session_info = self._sessions[session_id]
            session_info.last_update = datetime.utcnow()
            session_info.updates_received += 1
            
            # Update progress
            if update.progress_percent is not None:
                session_info.progress = update.progress_percent
            
            # Track agent completion
            if update.agent and update.type == "progress":
                agent_name = update.agent
                if agent_name not in session_info.completed_agents:
                    if "completed" in update.message.lower():
                        session_info.completed_agents.append(agent_name)
                        # Remove from pending if present
                        if agent_name in session_info.pending_agents:
                            session_info.pending_agents.remove(agent_name)
            
            # Update status based on update type
            if update.type == "completed":
                session_info.status = "completed"
                session_info.progress = 100
            elif update.type == "error":
                session_info.status = "failed"
                session_info.error = update.message
            elif update.type == "timeout":
                session_info.status = "timeout"
            
            # Extract v2 metadata from update data
            if update.data:
                if "is_follow_up" in update.data:
                    session_info.is_follow_up = update.data["is_follow_up"]
                if "update_type" in update.data:
                    session_info.update_type = update.data["update_type"]
                if "destination" in update.data:
                    session_info.destination = update.data["destination"]
                if "itinerary_complete" in update.data:
                    session_info.has_itinerary = True
                if "budget_complete" in update.data:
                    session_info.has_budget = True
            
            self.logger.debug(
                "Session updated",
                session_id=session_id,
                update_type=update.type,
                progress=session_info.progress,
                agent=update.agent
            )
        
        # Notify callbacks
        await self._notify_callbacks(session_id, update)
    
    async def update_from_result(
        self,
        session_id: str,
        result: TravelPlanResult
    ) -> None:
        """
        Update session from a travel plan result
        
        Args:
            session_id: Session identifier
            result: Travel plan result
        """
        async with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionInfo(session_id)
            
            session_info = self._sessions[session_id]
            session_info.status = result.status
            
            # Extract v2 fields
            if hasattr(result, 'is_follow_up'):
                session_info.is_follow_up = result.is_follow_up
            if hasattr(result, 'update_type'):
                session_info.update_type = result.update_type
            if hasattr(result, 'conversation_turn'):
                session_info.conversation_turns = result.conversation_turn
            if hasattr(result, 'destination'):
                session_info.destination = result.destination
            if hasattr(result, 'travel_dates'):
                session_info.travel_dates = result.travel_dates or []
            
            # Check what data is available
            if hasattr(result, 'itinerary') and result.itinerary:
                session_info.has_itinerary = True
            if hasattr(result, 'budget') and result.budget:
                session_info.has_budget = True
    
    async def register_callback(
        self,
        session_id: str,
        callback: SessionUpdateCallback
    ) -> None:
        """
        Register a callback for session updates
        
        Args:
            session_id: Session identifier
            callback: Callback function
        """
        async with self._lock:
            if session_id not in self._session_callbacks:
                self._session_callbacks[session_id] = []
            
            self._session_callbacks[session_id].append(callback)
            
            self.logger.debug(
                "Callback registered",
                session_id=session_id,
                callback_count=len(self._session_callbacks[session_id])
            )
    
    async def _notify_callbacks(
        self,
        session_id: str,
        update: StreamUpdate
    ) -> None:
        """Notify all callbacks for a session"""
        callbacks = self._session_callbacks.get(session_id, [])
        
        for callback in callbacks:
            try:
                await callback(session_id, update)
            except Exception as e:
                self.logger.error(
                    "Error in session callback",
                    error=e,
                    session_id=session_id
                )
    
    async def complete_session(
        self,
        session_id: str,
        result: TravelPlanResult
    ) -> None:
        """
        Mark session as completed and cache result
        
        Args:
            session_id: Session identifier
            result: Final travel plan result
        """
        async with self._lock:
            if session_id in self._sessions:
                session_info = self._sessions[session_id]
                session_info.status = "completed"
                session_info.progress = 100
                
                # Update v2 fields from result
                if hasattr(result, 'is_follow_up'):
                    session_info.is_follow_up = result.is_follow_up
                if hasattr(result, 'conversation_turn'):
                    session_info.conversation_turns = result.conversation_turn
        
        # Cache the result
        self.cache.set_result(session_id, result)
        
        self.logger.info(
            "Session completed",
            session_id=session_id,
            is_follow_up=self._sessions.get(session_id, SessionInfo(session_id)).is_follow_up
        )
    
    async def fail_session(
        self,
        session_id: str,
        error: str
    ) -> None:
        """
        Mark session as failed
        
        Args:
            session_id: Session identifier
            error: Error message
        """
        async with self._lock:
            if session_id in self._sessions:
                session_info = self._sessions[session_id]
                session_info.status = "failed"
                session_info.error = error
        
        self.logger.error(
            "Session failed",
            session_id=session_id,
            error=error
        )
    
    async def remove_session(self, session_id: str) -> None:
        """
        Remove session from tracking
        
        Args:
            session_id: Session identifier
        """
        async with self._lock:
            self._sessions.pop(session_id, None)
            self._session_callbacks.pop(session_id, None)
        
        self.logger.info(
            "Session removed",
            session_id=session_id
        )
    
    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session information or None
        """
        return self._sessions.get(session_id)
    
    def get_active_sessions(self) -> list[str]:
        """Get list of active session IDs"""
        return list(self._sessions.keys())
    
    def get_follow_up_sessions(self) -> list[str]:
        """Get list of follow-up session IDs"""
        return [
            sid for sid, info in self._sessions.items()
            if info.is_follow_up
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get session manager statistics with v2 metrics
        
        Returns:
            Dictionary with statistics
        """
        total_sessions = len(self._sessions)
        completed = sum(1 for s in self._sessions.values() if s.status == "completed")
        failed = sum(1 for s in self._sessions.values() if s.status == "failed")
        in_progress = sum(
            1 for s in self._sessions.values()
            if s.status not in ["completed", "failed", "timeout"]
        )
        
        # NEW: v2 statistics
        follow_ups = sum(1 for s in self._sessions.values() if s.is_follow_up)
        with_itinerary = sum(1 for s in self._sessions.values() if s.has_itinerary)
        with_budget = sum(1 for s in self._sessions.values() if s.has_budget)
        
        # Update type breakdown
        update_types = {}
        for session in self._sessions.values():
            if session.update_type:
                update_types[session.update_type] = update_types.get(session.update_type, 0) + 1
        
        # Average conversation turns
        total_turns = sum(s.conversation_turns for s in self._sessions.values())
        avg_turns = total_turns / total_sessions if total_sessions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "active_callbacks": sum(len(cbs) for cbs in self._session_callbacks.values()),
            # NEW: v2 metrics
            "follow_up_sessions": follow_ups,
            "sessions_with_itinerary": with_itinerary,
            "sessions_with_budget": with_budget,
            "update_types": update_types,
            "average_conversation_turns": round(avg_turns, 2)
        }
    
    def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed session information as dictionary
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session details dictionary or None
        """
        session_info = self._sessions.get(session_id)
        return session_info.to_dict() if session_info else None