from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname == "youtu.be":
        return parsed.path[1:]
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query)["v"][0]
    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_transcript(url: str) -> list[dict]:
    """
    Updated for youtube-transcript-api v0.6+
    The new version uses a different calling convention.
    """
    video_id = extract_video_id(url)

    # New API style — create an instance first
    ytt_api = YouTubeTranscriptApi()
    fetched = ytt_api.fetch(video_id)

    # Convert to the same format as before so nothing else breaks
    transcript = [
        {"text": snippet.text, "start": snippet.start, "duration": snippet.duration}
        for snippet in fetched
    ]
    return transcript


def get_full_text(url: str) -> str:
    segments = get_transcript(url)
    return " ".join(segment["text"] for segment in segments)


def get_chunked_transcript(url: str, chunk_size: int = 800) -> list[dict]:
    segments = get_transcript(url)
    chunks = []
    current_words = []
    current_start = segments[0]["start"]
    word_count = 0

    for segment in segments:
        words = segment["text"].split()
        current_words.extend(words)
        word_count += len(words)

        if word_count >= chunk_size:
            chunks.append({"text": " ".join(current_words), "start": current_start})
            current_words = []
            current_start = segment["start"]
            word_count = 0

    if current_words:
        chunks.append({"text": " ".join(current_words), "start": current_start})

    return chunks


def format_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"
