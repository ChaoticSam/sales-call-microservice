import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Call, CallInsight
from ai_utils import compute_embeddings, compute_sentiment_score, compute_agent_talk_ratio

async def backfill():
    async with SessionLocal() as session:
        # Fetch calls without insights
        result = await session.execute(
            select(Call).outerjoin(CallInsight).where(CallInsight.call_id == None)
        )
        calls = result.scalars().all()

        for call in calls:
            emb   = compute_embeddings(call.transcript)
            sent  = compute_sentiment_score(call.transcript)
            ratio = compute_agent_talk_ratio(call.transcript)

            insight = CallInsight(
                call_id=call.call_id,
                embedding=emb,
                customer_sentiment=sent,
                agent_talk_ratio=ratio
            )
            session.add(insight)

        await session.commit()
        print(f"Backfilled insights for {len(calls)} calls.")

if __name__ == "__main__":
    asyncio.run(backfill())
