import os
from openai import OpenAI
from dotenv import load_dotenv
from app.transcript import get_full_text, get_chunked_transcript

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_transcript(url: str) -> dict:
    chunks = get_chunked_transcript(url)

    if len(chunks) <= 3:
        full_text = get_full_text(url)
        return _summarize_text(full_text)

    chunk_summaries = []
    for chunk in chunks:
        mini_summary = _quick_summary(chunk["text"])
        chunk_summaries.append(mini_summary)

    combined = "\n\n".join(chunk_summaries)
    return _summarize_text(combined)


def _summarize_text(text: str) -> dict:
    prompt = """You are an expert learning assistant for an app called Distill.

Analyze the transcript below and return a summary using EXACTLY this format.
Do not add any extra text before or after. Do not change the section headers.

TLDR: Write a single paragraph of 3-5 sentences summarizing the video here.

KEY CONCEPTS:
- First important concept or idea
- Second important concept or idea
- Third important concept or idea
- Fourth important concept or idea
- Fifth important concept or idea

CONCLUSION: Write 2-3 sentences on the core takeaway and why it matters here.

TRANSCRIPT:
""" + text[:6000]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content
    print("DEBUG - Raw response preview:", raw[:200])
    return _parse_summary(raw)


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


def _parse_summary(raw_text: str) -> dict:
    result = {"tldr": "", "key_concepts": [], "conclusion": ""}

    lines = raw_text.strip().split("\n")
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect section headers
        if line.upper().startswith("TLDR:"):
            current_section = "tldr"
            content = line[5:].strip()  # everything after "TLDR:"
            if content:
                result["tldr"] = content

        elif line.upper().startswith("KEY CONCEPTS:"):
            current_section = "key_concepts"

        elif line.upper().startswith("CONCLUSION:"):
            current_section = "conclusion"
            content = line[11:].strip()  # everything after "CONCLUSION:"
            if content:
                result["conclusion"] = content

        # Fill sections
        elif current_section == "tldr" and not result["tldr"]:
            result["tldr"] = line

        elif current_section == "key_concepts" and line.startswith("-"):
            concept = line.lstrip("-").strip()
            if concept:
                result["key_concepts"].append(concept)

        elif current_section == "conclusion" and not result["conclusion"]:
            result["conclusion"] = line

    return result
