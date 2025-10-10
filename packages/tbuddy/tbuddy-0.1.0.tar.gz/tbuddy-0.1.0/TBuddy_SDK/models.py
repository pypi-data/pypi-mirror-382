"""
Data models for Ringmaster SDK using Pydantic
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict




class SessionMemory:
    """Session memory information"""
    def __init__(self, data: Dict[str, Any]):
        self.session_id = data.get("session_id")
        self.exists = data.get("exists", False)
        self.destination = data.get("destination")
        self.travel_dates = data.get("travel_dates", [])
        self.travelers_count = data.get("travelers_count")
        self.budget_range = data.get("budget_range")
        self.has_itinerary = data.get("has_itinerary", False)
        self.has_budget_data = data.get("has_budget_data", False)
        self.conversation_turns = data.get("conversation_turns", 0)
        self.last_updated = data.get("last_updated")
        self.expires_in_hours = data.get("expires_in_hours")


class ConversationHistory:
    """Conversation history for a session"""
    def __init__(self, data: Dict[str, Any]):
        self.session_id = data.get("session_id")
        self.history = data.get("conversation_history", [])
        self.total_turns = data.get("total_turns", 0)

class TravelQuery(BaseModel):
    """Model for travel query request"""
    query: str = Field(..., min_length=10, description="Natural language travel query")
    session_id: Optional[str] = Field(None, description="Optional session ID")
    user_id: Optional[str] = Field(None, description="Optional user ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Plan a 3-day trip to Paris from London in July",
                "session_id": "session_abc123"
            }
        }
    )


class AgentStatus(BaseModel):
    """Model for individual agent status"""
    name: str
    status: str  # pending, processing, completed, timeout, failed
    message: Optional[str] = None


class SessionStatus(BaseModel):
    """Model for session status response"""
    session_id: str
    status: str  # initialized, processing, completed, failed
    progress_percent: int = Field(0, ge=0, le=100)
    current_agent: Optional[str] = None
    completed_agents: List[str] = Field(default_factory=list)
    pending_agents: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TravelPlanResult(BaseModel):
    """Model for complete travel plan result"""
    session_id: str
    status: str
    destination: Optional[str] = None
    travel_dates: List[str] = Field(default_factory=list)
    needs_itinerary: bool = False
    weather: Optional[Dict[str, Any]] = None
    events: Optional[Dict[str, Any]] = None
    maps: Optional[Dict[str, Any]] = None
    budget: Optional[Dict[str, Any]] = None
    itinerary: Optional[Dict[str, Any]] = None
    messages: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    agent_statuses: Dict[str, str] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_follow_up: bool
    update_type: Optional[str]


class StreamUpdate(BaseModel):
    """Model for WebSocket stream updates"""
    type: str  # progress, agent_update, completed, error, connected, timeout
    session_id: Optional[str] = None
    agent: Optional[str] = None
    message: str
    progress_percent: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthStatus(BaseModel):
    """Model for health check response"""
    status: str  # healthy, degraded, unhealthy
    orchestrator: str
    redis: str
    timestamp: datetime