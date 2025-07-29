import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from app.db import SessionLocal
from app.models import Call
from ai_utils import (
    compute_embeddings,
    compute_sentiment_score,
    compute_agent_talk_ratio,
)
from app.models import Call as CallModel

CSV_FILE = "dataset/sample.csv"
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def parse_datetime(ts: str) -> datetime:
    try:
        dt = datetime.strptime(ts, "%a %b %d %H:%M:%S %z %Y")
        dt = dt.replace(tzinfo=None)
    except ValueError:
        dt = datetime.strptime(ts, "%a %b %d %H:%M:%S %Y")
    return dt

def normalize_conversations(df: pd.DataFrame):
    tweet_map = {row["tweet_id"]: row for _, row in df.iterrows()}
    conversations = []
    visited = set()

    for _, row in df.iterrows():
        tid = row["tweet_id"]
        if tid in visited:
            continue

        # start only at an agent’s reply
        if not row["inbound"] and pd.notnull(row["in_response_to_tweet_id"]):
            thread = []
            current = row
            while True:
                thread.append(current)
                visited.add(current["tweet_id"])

                parent = current["in_response_to_tweet_id"]
                if pd.isna(parent) or parent not in tweet_map:
                    break
                current = tweet_map[parent]

            conversations.append(list(reversed(thread)))

    return conversations

def build_call(convo: list[dict]):
    start = parse_datetime(convo[0]["created_at"])
    end   = parse_datetime(convo[-1]["created_at"])
    duration = int((end - start).total_seconds())

    # Identifing agent or customer
    agent = next((m for m in convo if not m["inbound"]), None)
    cust  = next((m for m in convo if     m["inbound"]), None)
    if agent is None or cust is None:
        return None

    # Full transcript
    lines = []
    for m in convo:
        speaker = "Agent" if not m["inbound"] else "Customer"
        lines.append(f"{speaker} ({m['author_id']}): {m['text']}")
    transcript = "\n".join(lines)

    return {
        "call_id":           str(agent["tweet_id"]),
        "agent_id":          agent["author_id"],
        "customer_id":       cust["author_id"],
        "language":          "en",
        "start_time":        start,
        "duration_seconds":  duration,
        "transcript":        transcript,
    }

async def insert_call_with_insights(call_dict: dict, convo: list[dict]):
    call_id = call_dict["call_id"]
    print(f"[DEBUG] Preparing to insert call {call_id}")
    
    raw_path = RAW_DIR / f"{call_id}.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump([{
            "tweet_id": m["tweet_id"],
            "author_id": m["author_id"],
            "inbound": m["inbound"],
            "created_at": m["created_at"],
            "text": m["text"]
        } for m in convo], f, ensure_ascii=False, indent=2)

    embedding = compute_embeddings(call_dict["transcript"])
    sentiment = compute_sentiment_score(call_dict["transcript"])
    talk_ratio = compute_agent_talk_ratio(call_dict["transcript"])

    call_row = CallModel(
        call_id             = call_id,
        agent_id            = call_dict["agent_id"],
        customer_id         = call_dict["customer_id"],
        language            = call_dict["language"],
        start_time          = call_dict["start_time"],
        duration_seconds    = call_dict["duration_seconds"],
        transcript          = call_dict["transcript"],
        embedding           = embedding,
        customer_sentiment  = sentiment,
        agent_talk_ratio    = talk_ratio,
    )

    async with SessionLocal() as session:
        try:
            session.add(call_row)
            print(f"[DEBUG] Added call {call_id} to session")
            await session.flush()
            print(f"[DEBUG] Flushed call {call_id}")
            await session.commit()
            print(f"[INFO] Inserted call {call_id}")
        except SQLAlchemyError as e:
            await session.rollback()
            print(f"[ERROR] Inserting call {call_id}: {e}")
            raise

async def main():
    df = pd.read_csv(CSV_FILE, header=0)
    conversations = normalize_conversations(df)
    print(f"[DEBUG] {len(conversations)} threads found")

    async with SessionLocal() as session:
        async with session.begin():
            inserted = 0
            for convo in conversations:
                call_dict = build_call(convo)
                if not call_dict:
                    continue
                # Check for existing call_id
                exists = await session.get(Call, call_dict["call_id"])
                if exists:
                    print(f"[INFO] Skipping duplicate call_id {call_dict['call_id']}")
                    continue
                call_row = Call(**call_dict)
                session.add(call_row)
                inserted += 1
        print(f"[DEBUG] Committed {inserted} calls")

if __name__ == "__main__":
    asyncio.run(main())