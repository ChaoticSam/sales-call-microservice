import pytest
from utils.ai_utils import compute_sentiment_score, compute_agent_talk_ratio

def test_sentiment_score():
    sample = "I am very happy with the service."
    score = compute_sentiment_score(sample)
    assert -1 <= score <= 1

def test_agent_talk_ratio():
    transcript = """Agent: Hello! How can I help?
Customer: I'm facing an issue.
Agent: Let me check that for you."""
    ratio = compute_agent_talk_ratio(transcript)
    assert 0 <= ratio <= 1
