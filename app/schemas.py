from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CallBase(BaseModel):
    call_id: str
    agent_id: str
    customer_id: str
    language: str
    start_time: datetime
    duration_seconds: int
    transcript: str


class CallDetail(CallBase):
    embedding: Optional[List[float]] = None
    customer_sentiment: Optional[float] = None
    agent_talk_ratio: Optional[float] = None


class CallSummary(CallBase):
    customer_sentiment: float
    agent_talk_ratio: float


class CallsListResponse(BaseModel):
    total: int
    items: List[CallSummary]


class Recommendation(BaseModel):
    call_id: str
    similarity: float
    nudge: str = Field(..., max_length=40)


class AnalyticsAgent(BaseModel):
    agent_id: str
    avg_sentiment: float
    avg_talk_ratio: float
    total_calls: int


class ErrorResponse(BaseModel):
    detail: str
