import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel

load_dotenv()

MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")
MAX_CHARS = 30_000
ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

client = Groq()  # reads GROQ_API_KEY from the environment
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXTRACT_SYSTEM = """You extract structured notes from meeting transcripts.
Return ONLY a JSON object with this shape:
{"summary": string, "decisions": [string],
 "action_items": [{"task": string, "owner": string, "deadline": string}],
 "open_questions": [string]}
Use "Unassigned" or "Not stated" when the transcript does not say.
Never invent owners or dates."""

CHAT_SYSTEM = """You are a meeting assistant. Answer using only the transcript
below. If the transcript does not cover something, say so. Be concise.

Transcript:
{transcript}"""


class ExtractReq(BaseModel):
    transcript: str


class ChatReq(BaseModel):
    transcript: str
    messages: list[dict]  # [{"role": "user" or "assistant", "content": "..."}]


def check_size(text: str) -> None:
    if not text.strip():
        raise HTTPException(400, "Transcript is empty.")
    if len(text) > MAX_CHARS:
        raise HTTPException(413, f"Transcript is over {MAX_CHARS} characters.")


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/extract")
def extract(req: ExtractReq):
    check_size(req.transcript)
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM},
                {"role": "user", "content": req.transcript},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1500,
        )
        return json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        raise HTTPException(502, "Model returned invalid JSON. Try again.")
    except Exception as e:
        raise HTTPException(502, f"LLM error: {e}")


@app.post("/chat")
def chat(req: ChatReq):
    check_size(req.transcript)
    messages = [{"role": "system", "content": CHAT_SYSTEM.format(transcript=req.transcript)}]
    messages += req.messages
    try:
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.3, max_tokens=1000
        )
        return {"reply": resp.choices[0].message.content}
    except Exception as e:
        raise HTTPException(502, f"LLM error: {e}")