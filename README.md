# UPSC Q&A Chatbot

A Streamlit chatbot that answers UPSC Civil Services Examination questions
(Prelims, Mains, Essay) with clear, exam-ready explanations, powered by the
Gemini API (Google Gen AI SDK, `google-genai`), with automatic fallback to
the Grok API (`xai-sdk`) if Gemini errors out.

## Features

- ChatGPT-style layout: conversation history on top, a query box pinned to
  the bottom of the screen (Streamlit's native `st.chat_input`).
- System prompt tuned for UPSC answers: direct answer first, then a plain
  explanation, syllabus/current-affairs relevance, and a quick revision
  recap.
- Sidebar with example questions and a "Clear conversation" button.
- Uses one Gemini model and one Grok model only — no model picker, kept
  simple for a chatbot.
- If the Gemini call fails (bad key, rate limit, outage), the same
  question is automatically retried against Grok and the answer is
  labelled "Answered by Grok" so you know which model replied.
- Streamed responses (tokens appear as they're generated).

## Setup

```bash
cd upsc-chatbot
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your keys:

```
GEMINI_API_KEY=...   # required — get one at https://aistudio.google.com/apikey
XAI_API_KEY=...       # optional — powers the Grok fallback, get one at https://console.x.ai
```

If `XAI_API_KEY` is left blank, the app still runs — it just surfaces the
Gemini error directly instead of falling back.

## Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploying (e.g. Streamlit Community Cloud)

Instead of a `.env` file, add the key under
**App settings -> Secrets** as:

```toml
GEMINI_API_KEY = "..."
XAI_API_KEY = "..."
```

(or create `.streamlit/secrets.toml` locally with the same content — it is
git-ignored).

## Models

- Primary: `gemini-flash-latest` (the `GEMINI_MODEL` constant in `app.py`) —
  Google's floating alias that always resolves to their current Flash
  model, so it keeps working as new versions ship.
- Fallback: `grok-4-fast-non-reasoning` (the `GROK_MODEL` constant) — used
  automatically only when the Gemini call raises an error.

Change either constant if you want to pin a different model.
