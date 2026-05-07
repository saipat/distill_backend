from app.transcript import (
    get_transcript,
    get_full_text,
    get_chunked_transcript,
    format_timestamp,
)

# A classic 15-minute TED talk — good test video
URL = "https://www.youtube.com/watch?v=UF8uR6Z6KLc"

print("=" * 50)
print("TEST 1 — Raw transcript (first 3 segments)")
print("=" * 50)
segments = get_transcript(URL)
for seg in segments[:3]:
    print(seg)

print("\n" + "=" * 50)
print("TEST 2 — Full text (first 300 characters)")
print("=" * 50)
text = get_full_text(URL)
print(text[:300])

print("\n" + "=" * 50)
print("TEST 3 — Chunked transcript")
print("=" * 50)
chunks = get_chunked_transcript(URL)
print(f"Total chunks: {len(chunks)}")
print(f"First chunk starts at: {format_timestamp(chunks[0]['start'])}")
print(f"First chunk preview: {chunks[0]['text'][:200]}")
