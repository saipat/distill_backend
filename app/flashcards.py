import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.transcript import get_full_text, get_chunked_transcript

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_flashcards(url: str) -> list[dict]:
    chunks = get_chunked_transcript(url)

    # For long videos use chunk summaries, for short use full text
    if len(chunks) <= 3:
        text = get_full_text(url)
    else:
        summaries = []
        for chunk in chunks:
            summaries.append(_quick_summary(chunk["text"]))
        text = "\n\n".join(summaries)

    prompt = """You are an expert learning assistant for an app called Distill.

Generate 8 flashcards based on the transcript below.

Return ONLY a valid JSON array. No extra text, no markdown, no code fences.

Each object must have exactly these fields:
- "id": a unique string like "fc1", "fc2" etc
- "question": a clear, specific question testing understanding of a concept
- "answer": a concise but complete answer (2-4 sentences)

Focus on the most important concepts. Make questions test understanding, not just recall.

Example format:
[
  {"id": "fc1", "question": "What problem does the attention mechanism solve?", "answer": "It lets a model relate any two tokens directly regardless of distance, solving the long-range dependency problem that RNNs struggled with."},
  {"id": "fc2", "question": "What are the three matrices in self-attention?", "answer": "Query (Q), Key (K), and Value (V). Each token is projected into all three. Attention scores come from Q times K and the output is a weighted sum of V."}
]

TRANSCRIPT:
""" + text[:6000]

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

    flashcards = json.loads(raw)
    return flashcards


def _quick_summary(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"Summarize this transcript excerpt in 3-5 sentences:\n\n{text}",
            }
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
