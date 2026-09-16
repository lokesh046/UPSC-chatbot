# UPSC Q&A Chatbot

A Streamlit chatbot that answers UPSC Civil Services Examination questions
(Prelims, Mains, Essay) with clear, exam-ready explanations, powered by the
Gemini API (Google Gen AI SDK, `google-genai`).

## Features

- ChatGPT-style layout: conversation history on top, a query box pinned to
  the bottom of the screen (Streamlit's native `st.chat_input`).
- System prompt tuned for UPSC answers: direct answer first, then a plain
  explanation, syllabus/current-affairs relevance, and a quick revision
  recap.
- Sidebar with example questions and a "Clear conversation" button.
- Uses Gemini 3.1 Flash only — no model picker, kept simple for a chatbot.
- Streamed responses (tokens appear as they're generated).

## Setup

```bash
cd upsc-chatbot
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your key (get one at https://aistudio.google.com/apikey):

```
GEMINI_API_KEY=...
```

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
```

(or create `.streamlit/secrets.toml` locally with the same content — it is
git-ignored).

## Model

Hardcoded to `gemini-3.1-flash` in `app.py` (the `MODEL` constant). Change
that constant if you ever want a different model.
