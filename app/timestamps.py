import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.transcript import get_chunked_transcript, format_timestamp

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_key_moments(url: str) -> list[dict]:
    chunks = get_chunked_transcript(url)

    transcript_with_times = ""
    for chunk in chunks:
        ts = format_timestamp(chunk["start"])
        transcript_with_times += "[" + ts + "] " + chunk["text"] + "\n\n"

    prompt = (
        "You are an expert learning assistant for an app called Distill.\n\n"
        "Analyze the transcript below and identify the 6 most important moments.\n\n"
        "Return a JSON object with a single key 'moments' containing an array.\n"
        "Each item must have: timestamp (string), seconds (integer), title (string), description (string).\n\n"
        "TRANSCRIPT:\n" + transcript_with_times[:6000]
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
