from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class Call(Base):
    __tablename__ = "calls_db"

    call_id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    language = Column(String, default="en")
    start_time = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer)
    transcript = Column(String, nullable=False)
    
class CallInsight(Base):
    __tablename__ = "call_insights"

    call_id           = Column(String, ForeignKey("calls_db.call_id"), primary_key=True)
    embedding         = Column(ARRAY(Float), nullable=False)
    customer_sentiment= Column(Float, nullable=False)
    agent_talk_ratio  = Column(Float, nullable=False)
