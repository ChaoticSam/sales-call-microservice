from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.schemas import AnalyticsAgent
from app.models import CallInsight, Call
from app.db import get_session

router = APIRouter()

@router.get("/agents", response_model=list[AnalyticsAgent])
async def agents_leaderboard(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(
            Call.agent_id,
            func.avg(CallInsight.customer_sentiment).label("avg_sentiment"),
            func.avg(CallInsight.agent_talk_ratio).label("avg_talk_ratio"),
            func.count(Call.call_id).label("total_calls"),
        )
        .join(CallInsight, Call.call_id == CallInsight.call_id)
        .group_by(Call.agent_id)
        .order_by(func.count(Call.call_id).desc())
    )
    rows = await session.execute(stmt)
    return [
        {
            "agent_id": agent_id,
            "avg_sentiment": avg_sentiment,
            "avg_talk_ratio": avg_talk_ratio,
            "total_calls": total_calls,
        }
        for agent_id, avg_sentiment, avg_talk_ratio, total_calls in rows
    ]
