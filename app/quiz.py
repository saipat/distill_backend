import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.transcript import get_full_text, get_chunked_transcript

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_quiz(url: str) -> list[dict]:
    chunks = get_chunked_transcript(url)

    if len(chunks) <= 3:
        text = get_full_text(url)
    else:
        summaries = []
        for chunk in chunks:
            summaries.append(_quick_summary(chunk["text"]))
        text = "\n\n".join(summaries)

    prompt = """You are an expert learning assistant for an app called Distill.

Generate 5 quiz questions based on the transcript below.
Mix of question types: 3 multiple choice and 2 typed/open-ended.

Return ONLY a valid JSON array. No extra text, no markdown, no code fences.

For multiple choice questions, each object must have:
- "id": unique string like "q1", "q2" etc
- "type": "multiple_choice"
- "question": the question text
- "options": array of exactly 4 answer strings
- "correctAnswer": the correct option (must match one of the options exactly)
- "explanation": 1-2 sentences explaining why the answer is correct

For typed/open-ended questions, each object must have:
- "id": unique string
- "type": "typed"
- "question": the question text
- "options": null
- "correctAnswer": a model answer showing what a good response looks like
- "explanation": 1-2 sentences with extra context

Example:
[
  {
    "id": "q1",
    "type": "multiple_choice",
    "question": "What is the main advantage of attention over RNNs?",
    "options": ["Fewer parameters", "Direct token-to-token connections regardless of distance", "Faster inference", "Smaller memory usage"],
    "correctAnswer": "Direct token-to-token connections regardless of distance",
    "explanation": "Attention creates a direct learned connection between any two tokens, solving the vanishing gradient problem in long sequences."
  },
  {
    "id": "q2",
    "type": "typed",
    "question": "Explain in your own words what the softmax function does in the attention mechanism.",
    "options": null,
    "correctAnswer": "Softmax converts raw attention scores into a probability distribution that sums to 1, so each token's contribution is weighted proportionally.",
    "explanation": "Without softmax the scores would be unbounded and could not be used as mixing weights for the value vectors."
  }
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

    questions = json.loads(raw)
    return questions


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
