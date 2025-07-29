import pytest
from httpx import AsyncClient
from app.models import Call, CallInsight
from datetime import datetime

@pytest.mark.asyncio
async def test_list_and_get_call(initialized_app):
    async with AsyncClient(app=initialized_app, base_url="http://test") as client:
        # 1) Seed one call + insight
        call = Call(
            call_id="test1",
            agent_id="AgentA",
            customer_id="Cust1",
            language="en",
            start_time=datetime.utcnow(),
            duration_seconds=30,
            transcript="Agent: Hello\nCustomer: Hi"
        )
        insight = CallInsight(
            call_id="test1",
            embedding=[0.1, 0.2, 0.3],
            customer_sentiment=0.5,
            agent_talk_ratio=0.5
        )
        # Insert directly via session
        from app.db import get_session
        async for session in get_session():
            session.add(call)
            session.add(insight)
            await session.commit()
            break

        # 2) Test list endpoint
        resp = await client.get("/api/v1/calls", params={"limit":1})
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["call_id"] == "test1"

        # 3) Test get detail
        resp2 = await client.get("/api/v1/calls/test1")
        assert resp2.status_code == 200
        data = resp2.json()
        assert data["call_id"] == "test1"
        assert "embedding" in data
        assert data["customer_sentiment"] == 0.5

@pytest.mark.asyncio
async def test_recommendations_and_analytics(initialized_app):
    async with AsyncClient(app=initialized_app, base_url="http://test") as client:
        # You'd seed multiple calls here to test recommendations & analytics...
        # Then assert recommended call_ids and analytics leaderboard.
        pass
