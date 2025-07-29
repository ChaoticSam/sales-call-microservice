from fastapi import FastAPI
from app.routes import calls, analytics

app = FastAPI(title="Sales Call Analytics API")

app.include_router(calls.router, prefix="/api/v1/calls", tags=["calls"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
