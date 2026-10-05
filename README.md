# 📝 Recap: Meeting Transcript to Action Items

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-LLM%20API-orange)](https://groq.com)
[![Vercel](https://img.shields.io/badge/Vercel-Live-black?logo=vercel)](https://meeting-bot-frontend-delta.vercel.app/)
[![Render](https://img.shields.io/badge/Render-API-46E3B7?logo=render)](https://render.com)

An end-to-end LLM app that turns raw meeting transcripts into structured notes: a summary, decisions, action items with owner and deadline, and open questions. A grounded chat layer answers follow-up questions and drafts the recap email using only what the transcript says.

👉 **[Try the Live App](https://meeting-bot-frontend-delta.vercel.app/)**

> The backend runs on a free Render instance, so the first request after inactivity can take 30 to 60 seconds while it wakes up.

<img width="1221" height="771" alt="image" src="https://github.com/user-attachments/assets/8552f1e9-bf96-4a36-a335-b71cc26ec029" />


---

## 🔍 The Problem

Teams lose track of what was decided in meetings. Action items get buried in long transcripts, owners are unclear, and follow-up emails are written from memory. General-purpose LLMs also tend to fill gaps with plausible but invented details, such as an owner or deadline nobody actually mentioned.

This project extracts only what is stated in the transcript, marks everything else as `Unassigned` or `Not stated`, and keeps follow-up answers grounded in the source text.

---

## 🧠 How It Works

```
Meeting Transcript
        │
        ▼
┌─────────────────────┐
│   Input Validation  │  empty check + 30,000 character cap
└────────┬────────────┘
         │  clean transcript
         ▼
┌─────────────────────┐
│  Extraction Prompt  │  strict JSON schema, no invented owners or dates
└────────┬────────────┘
         │  prompt + transcript
         ▼
┌─────────────────────┐
│     Groq LLM        │  GPT-OSS in JSON mode
└────────┬────────────┘
         │  structured JSON
         ▼
┌─────────────────────┐
│   Frontend Render   │  notes, action item cards, copy as text
└────────┬────────────┘
         │
         ▼
   Summary + Decisions + Action Items + Open Questions
         │
         ▼
┌─────────────────────┐
│  Grounded Chat      │  transcript as context, answers only from source
└─────────────────────┘
```

---

## ✨ Features

- **Structured extraction**: returns a fixed JSON schema (summary, decisions, action items, open questions)
- **Owner and deadline tracking**: every action item carries an owner and a deadline
- **No invented details**: missing owners or dates come back as `Unassigned` or `Not stated`
- **Grounded follow-up chat**: answers come only from the transcript, and the model says so when a question is not covered
- **Recap email drafting**: one click to generate a follow-up email from the meeting
- **Copy notes**: export the notes as plain text
- **Safe rendering**: model output is inserted with `textContent`, never `innerHTML`
- **CORS allow-list**: the API accepts browser requests only from the deployed frontend
- **Responsive UI**: works on mobile, with automatic light and dark mode
- **Deployed stack**: static frontend on Vercel, FastAPI backend on Render

---

## 📁 Project Structure

```
meeting-bot/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── docs/
│   ├── architecture.png
│   └── screenshot.png
├── .gitignore
└── README.md
```

---

## 🚀 Run Locally

Requires Python 3.10+ and a free Groq API key from [console.groq.com](https://console.groq.com).

```
git clone https://github.com/nishi-0212/meeting-bot.git
cd meeting-bot/backend
pip install -r requirements.txt
```

Create `backend/.env`:

```
GROQ_API_KEY=your_key_here
MODEL=openai/gpt-oss-120b
```

Start the backend:

```
python -m uvicorn main:app --reload
```

In a second terminal, serve the frontend:

```
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500`. For local use, set the `API` constant in `frontend/index.html` to `http://127.0.0.1:8000`.

---

## 💡 Example

**Input:**

```
Sneha: Android is stable, but iOS still has the login crash. We release Android on Monday.
Arjun: I'll fix the iOS crash and share the build with QA by Wednesday.
Kavya: I'll prepare the regression checklist before QA tests on Thursday.
Sneha: Dev, please follow up with the client tomorrow.
Kavya: Nobody has decided who writes the release notes.
```

**Output:**

| Action item                           | Owner  | Deadline            |
| ------------------------------------- | ------ | ------------------- |
| Fix the iOS login crash, share build  | Arjun  | Wednesday           |
| Prepare the regression checklist      | Kavya  | Before Thursday     |
| Follow up with the client             | Dev    | Tomorrow            |

**Decision:** Release Android on Monday, iOS after the fix.

**Open question:** Who writes the release notes?

---

## 🔌 API

| Method | Path       | Body                                              | Returns                                                                             |
| ------ | ---------- | ------------------------------------------------- | ----------------------------------------------------------------------------------- |
| GET    | `/`        | none                                              | `{"status": "ok"}`                                                                  |
| POST   | `/extract` | `{"transcript": "..."}`                           | `{summary, decisions[], action_items[{task, owner, deadline}], open_questions[]}`   |
| POST   | `/chat`    | `{"transcript": "...", "messages": [...]}`        | `{"reply": "..."}`                                                                  |

---

## ⚙️ Tech Stack

| Component       | Tool                                  |
| --------------- | ------------------------------------- |
| Frontend        | HTML, CSS, vanilla JavaScript         |
| Backend         | FastAPI, Pydantic, Uvicorn            |
| LLM inference   | Groq API (GPT-OSS, JSON mode)         |
| Frontend hosting | Vercel                               |
| Backend hosting | Render                                |

---

## 📦 Installation

`backend/requirements.txt`:

```
fastapi
uvicorn
groq
python-dotenv
```

| Variable          | Required | Description                                                  |
| ----------------- | -------- | ------------------------------------------------------------ |
| `GROQ_API_KEY`    | Yes      | Groq API key                                                 |
| `MODEL`           | No       | Groq model ID, defaults to `openai/gpt-oss-120b`             |
| `ALLOWED_ORIGINS` | No       | Comma-separated frontend origins, defaults to `*`            |

---

## ⚠️ Limitations

- Free-tier cold starts on the backend
- No authentication or per-user rate limiting
- Transcripts above the character cap are rejected instead of chunked
- Extraction quality depends on how clearly speakers name owners and dates

## 🛣️ Roadmap

- Per-IP rate limiting
- Chunking and merging for long meetings
- Evaluation set of labelled transcripts with precision and recall for action items
- Export to Slack, Notion and calendar events
