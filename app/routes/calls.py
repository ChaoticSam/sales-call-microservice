from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from sklearn.metrics.pairwise import cosine_similarity
from utils.ai_utils import generate_coaching_nudges

from app.schemas import (
    CallsListResponse,
    CallDetail,
    Recommendation,
    ErrorResponse,
)
from app.models import Call, CallInsight
from app.db import get_session


router = APIRouter()

@router.get(
    "", response_model=CallsListResponse,
    responses={422: {"model": ErrorResponse}}
)
async def list_calls(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    agent_id: str = Query(None),
    from_date: datetime = Query(None),
    to_date: datetime = Query(None),
    min_sentiment: float = Query(None, ge=-1.0, le=1.0),
    max_sentiment: float = Query(None, ge=-1.0, le=1.0),
    session: AsyncSession = Depends(get_session)
):
    filters = []
    if agent_id:
        filters.append(Call.agent_id == agent_id)
    if from_date:
        filters.append(Call.start_time >= from_date)
    if to_date:
        filters.append(Call.start_time <= to_date)
    if min_sentiment is not None:
        filters.append(CallInsight.customer_sentiment >= min_sentiment)
    if max_sentiment is not None:
        filters.append(CallInsight.customer_sentiment <= max_sentiment)

    stmt = (
        select(Call, CallInsight)
        .join(CallInsight, Call.call_id == CallInsight.call_id)
        .where(and_(*filters)) if filters else
        select(Call, CallInsight)
        .join(CallInsight, Call.call_id == CallInsight.call_id)
    )
    total = (await session.execute(stmt.with_only_columns([Call.call_id]).order_by(None))).rowcount
    result = await session.execute(stmt.order_by(Call.start_time.desc()).limit(limit).offset(offset))
    items = [
        {
            **call.__dict__,
            "customer_sentiment": insight.customer_sentiment,
            "agent_talk_ratio": insight.agent_talk_ratio
        }
        for call, insight in result.all()
    ]
    return {"total": total, "items": items}


@router.get(
    "/{call_id}", response_model=CallDetail,
    responses={404: {"model": ErrorResponse}}
)
async def get_call(call_id: str, session: AsyncSession = Depends(get_session)):
    stmt = select(Call, CallInsight).join(
        CallInsight, Call.call_id == CallInsight.call_id
    ).where(Call.call_id == call_id)
    result = await session.execute(stmt)
    rec = result.first()
    if not rec:
        raise HTTPException(404, f"Call {call_id} not found")
    call, insight = rec
    return {
        **call.__dict__,
        "embedding": insight.embedding,
        "customer_sentiment": insight.customer_sentiment,
        "agent_talk_ratio": insight.agent_talk_ratio
    }


@router.get(
    "/{call_id}/recommendations",
    response_model=List[Recommendation],
    responses={404: {"model": ErrorResponse}}
)
async def get_recommendations(
    call_id: str,
    session: AsyncSession = Depends(get_session)
):
    # fetch embedding for this call
    stmt0 = select(CallInsight.embedding).where(CallInsight.call_id == call_id)
    res0 = await session.execute(stmt0)
    emb = res0.scalar_one_or_none()
    if emb is None:
        raise HTTPException(404, f"Insights for {call_id} not found")

    # fetch all other embeddings
    stmt1 = select(CallInsight.call_id, CallInsight.embedding)
    rows = await session.execute(stmt1)
    others = [(cid, vec) for cid, vec in rows if cid != call_id]

    # compute cosine similarity
    sims = cosine_similarity([emb], [vec for _, vec in others])[0]
    top5 = sorted(zip(others, sims), key=lambda x: -x[1])[:5]

    # Fetch original transcript
    transcript = Call.transcript
    
    # Generate nudges via Groq API
    nudges = generate_coaching_nudges(transcript)

    recommendations = []
    for (cid, _), sim in top5:
        nudge_text = nudges.pop(0) if nudges else ""
        recommendations.append({
            "call_id": cid,
            "similarity": float(sim),
            "nudge": nudge_text
        })

    return recommendations
