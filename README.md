# Conversational Insights from Support Tweets

This project processes threaded support conversations (from Twitter-like data), stores them in a PostgreSQL database, and provides structured insights via a FastAPI-based REST API. It includes semantic search and AI-powered coaching nudges using the free [Groq API](https://groq.com).

---

## Setup & Installation

### 1. Clone the Repo

```bash
git clone https://github.com/ChaoticSam/sales_call_microservice.git
cd sales_call_microservice
```

### 2. Set Up Environment Variables
Create a .env file in the root with the following content:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
GROQ_API_KEY=groq_api_key
```

### 3. Create & Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run PostgreSQL Locally
If you're not using Docker, ensure PostgreSQL is running and accessible via localhost:5432.

## Database Migration / Initialization
Initialize DB tables using Alembic (if configured), or let SQLAlchemy auto-create them when running the app.

```bash
python scripts/init_db.py
This uses the ORM to create all tables defined in app/models.py.
```

### Ingesting Conversation Data
The script ingest.py reads a CSV dataset and populates the calls_db table with enriched metadata like embeddings, sentiment, and agent talk ratio.

#### Step-by-Step
1. Place your CSV at: dataset/sample.csv

2. Run the script:
```bash
python ingest.py
```

3. On success, it will:
Normalize threads into conversations
```bash
Save raw JSON into data/raw/{call_id}.json
```

## Running the API Server

### API Usage Examples
1. Get a Call by ID
```bash
curl http://localhost:8000/calls/98765
```
2. Search Calls by Text
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "refund not processed"}'
```
3. Get Recommendations (with Coaching Nudges)
```bash
curl http://localhost:8000/calls/98765/recommendations
```
4. Get Analytics Across Calls
```bash
curl http://localhost:8000/analytics

returns:
{
  "total_calls": 42,
  "average_duration": 165.3,
  "average_sentiment": 0.52,
  "average_agent_talk_ratio": 0.61
}
```
## Testing & Quality
1. Run All Tests with Coverage
```shell
pytest --cov=app
Ensuring coverage ≥ 70%.
```

2. Command for Static Checks (Black, Mypy, Isort)
```bash
black .
mypy .
isort .
```
