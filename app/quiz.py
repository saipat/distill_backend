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
        summaries = [_quick_summary(chunk["text"]) for chunk in chunks]
        text = "\n\n".join(summaries)

    prompt = (
        "You are an expert learning assistant for an app called Distill.\n\n"
        "Generate 5 quiz questions based on the transcript below.\n"
        "Mix: 3 multiple choice and 2 typed/open-ended.\n\n"
        "Return a JSON object with a single key 'questions' containing an array.\n\n"
        "For multiple choice items include: id, type ('multiple_choice'), question, options (array of 4 strings), correctAnswer, explanation.\n"
        "For typed items include: id, type ('typed'), question, options (null), correctAnswer, explanation.\n\n"
        "TRANSCRIPT:\n" + text[:6000]
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()
    parsed = json.loads(raw)
    if isinstance(parsed, dict):
        for v in parsed.values():
            if isinstance(v, list):
                return v
    return parsed


def _quick_summary(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "Summarize this transcript excerpt in 3-5 sentences:\n\n"
                + text,
            }
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
