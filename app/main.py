from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.summarizer import summarize_transcript
from app.timestamps import get_key_moments
from app.flashcards import get_flashcards
from app.quiz import get_quiz
from app.transcript import extract_video_id

app = FastAPI(title="Distill API")

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class VideoRequest(BaseModel):
    url: str


@app.get("/")
def root():
    return {"message": "Distill API is running"}


@app.post("/summarize")
def summarize(request: VideoRequest):
    """Returns tldr, key_concepts, and conclusion for a YouTube video."""
    try:
        summary = summarize_transcript(request.url)
        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/moments")
def moments(request: VideoRequest):
    """Returns 6 timestamped key moments with YouTube deep-link seconds."""
    try:
        data = get_key_moments(request.url)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flashcards")
def flashcards(request: VideoRequest):
    """Returns 8 flashcard question/answer pairs."""
    try:
        data = get_flashcards(request.url)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quiz")
def quiz(request: VideoRequest):
    """Returns 5 quiz questions — mix of multiple choice and typed."""
    try:
        data = get_quiz(request.url)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/distill")
def distill(request: VideoRequest):
    """
    Master endpoint — calls all four features in sequence and returns everything.
    The frontend calls this once and gets the full VideoData object back.
    """
    try:
        video_id = extract_video_id(request.url)

        summary = summarize_transcript(request.url)
        moments = get_key_moments(request.url)
        cards = get_flashcards(request.url)
        questions = get_quiz(request.url)

        return {
            "success": True,
            "data": {
                "url": request.url,
                "videoId": video_id,
                "title": "Video Summary",  # frontend can update with YouTube oEmbed later
                "duration": "",
                "summary": summary,
                "moments": moments,
                "flashcards": cards,
                "quiz": questions,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
