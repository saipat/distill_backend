import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.transcript import get_chunked_transcript, format_timestamp

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_key_moments(url: str) -> list[dict]:
    chunks = get_chunked_transcript(url)

    # Build transcript with timestamps for the prompt
    transcript_with_times = ""
    for chunk in chunks:
        ts = format_timestamp(chunk["start"])
        transcript_with_times += f"[{ts}] {chunk['text']}\n\n"

    prompt = """You are an expert learning assistant for an app called Distill.

Analyze the transcript below and identify the 6 most important moments.

Return ONLY a valid JSON array. No extra text, no markdown, no code fences.

Each object must have exactly these fields:
- "timestamp": the MM:SS timestamp string e.g. "4:15"
- "seconds": the timestamp converted to total seconds as an integer e.g. 255
- "title": a short 4-8 word title for this moment
- "description": one sentence explaining why this moment matters

Example format:
[
  {"timestamp": "0:42", "seconds": 42, "title": "Introduction to attention mechanism", "description": "The speaker explains why fixed embeddings fail to capture word context."},
  {"timestamp": "4:15", "seconds": 255, "title": "Query key and value matrices", "description": "A concrete retrieval analogy explains the three core projections in self-attention."}
]

TRANSCRIPT:
""" + transcript_with_times[:6000]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    moments = json.loads(raw)
    return moments
