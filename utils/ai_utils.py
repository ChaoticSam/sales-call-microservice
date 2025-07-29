from sentence_transformers import SentenceTransformer
from transformers import pipeline
import re
import os
from groq import Groq
from typing import List
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_coaching_nudges(transcript: str) -> List[str]:
    system = {
        "role": "system",
        "content": "You are a coaching assistant helping customer service agents improve their calls. Provide three concise nudges, each ≤ 40 words."
    }
    user = {
        "role": "user",
        "content": f"Here is a call transcript:\n\n{transcript}"
    }

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[system, user],
        temperature=0.3
    )

    raw = response.choices[0].message.content
    # Split lines and strip bullet markers
    nudges = [line.lstrip("-• ").strip() for line in raw.splitlines() if line.strip()]
    return nudges[:3]

# Load model
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
SENT_PIPE = pipeline("sentiment-analysis")
FILLERS = {"um", "uh", "ah", "like", "you know", "hmm"}
WORD_RE = re.compile(r"\b\w+\b")


def compute_embeddings(transcript: str) -> list[float]:
    """
    Split transcript into sentences, compute embeddings, and return mean vector.
    """
    sentences = [s.strip() for s in transcript.split('.') if s.strip()]
    if not sentences:
        return []
    # Compute embeddings
    vectors = EMBED_MODEL.encode(sentences, show_progress_bar=False)
    # Average across sentences
    mean_vec = vectors.mean(axis=0)
    return mean_vec.tolist()


def compute_sentiment_score(transcript: str) -> float:
    # Truncate to first 512 characters to limit processing
    snippet = transcript[:512]
    result = SENT_PIPE(snippet)[0]
    score = result.get("score", 0.0)
    label = result.get("label", "NEUTRAL")
    if label.upper().startswith("NEGATIVE"):
        return -score
    return score


def compute_agent_talk_ratio(transcript: str) -> float:
    total_words = 0
    agent_words = 0

    for line in transcript.split('\n'):
        # Determine speaker
        if line.startswith("Agent"):
            speaker = "agent"
        else:
            speaker = "customer"
        # Extract words
        words = WORD_RE.findall(line.lower())
        # Filter out fillers
        words = [w for w in words if w not in FILLERS]
        count = len(words)
        total_words += count
        if speaker == "agent":
            agent_words += count

    if total_words == 0:
        return 0.0
    return agent_words / total_words
