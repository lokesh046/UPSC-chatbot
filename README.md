# UPSC Q&A Chatbot

A Streamlit chatbot that answers UPSC Civil Services Examination questions
(Prelims, Mains, Essay) with clear, exam-ready explanations. Uses
**OpenRouter** as the main provider (a cheap general-purpose model), with
automatic fallback to Gemini, then Grok, if OpenRouter fails.

## Features

- ChatGPT-style layout: conversation history on top, a query box pinned to
  the bottom of the screen (Streamlit's native `st.chat_input`).
- System prompt tuned for UPSC answers: direct answer first, then a plain
  explanation, syllabus/current-affairs relevance, and a quick revision
  recap.
- Sidebar with example questions and a "Clear conversation" button.
- One model per provider, no model picker — kept simple for a chatbot.
- Three-tier fallback: if OpenRouter fails, the same question is retried
  against Gemini, then Grok. The reply is labelled "Answered by Gemini" /
  "Answered by Grok" whenever a fallback answered instead of OpenRouter.
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
OPENROUTER_API_KEY=...   # required — get one at https://openrouter.ai/keys
GEMINI_API_KEY=...       # optional fallback — https://aistudio.google.com/apikey
XAI_API_KEY=...          # optional fallback — https://console.x.ai
```

`GEMINI_API_KEY` and `XAI_API_KEY` are both optional. If neither is set,
the app still runs on OpenRouter alone — an OpenRouter failure just
surfaces its error directly instead of falling back.

## Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploying (e.g. Streamlit Community Cloud)

Instead of a `.env` file, add the keys under
**App settings -> Secrets** as:

```toml
OPENROUTER_API_KEY = "..."
GEMINI_API_KEY = "..."
XAI_API_KEY = "..."
```

(or create `.streamlit/secrets.toml` locally with the same content — it is
git-ignored).

## Models

- **Main**: `meta-llama/llama-3.3-70b-instruct` via OpenRouter (the
  `OPENROUTER_MODEL` constant in `app.py`) — cheap (~$0.10 / $0.32 per
  million input/output tokens) and capable enough for exam-style
  explanations.
- **Fallback 1**: `gemini-flash-latest` (the `GEMINI_MODEL` constant) —
  Google's floating alias that always resolves to their current Flash
  model.
- **Fallback 2**: `grok-4-fast-non-reasoning` (the `GROK_MODEL` constant).

Change any constant if you want to pin a different model. Browse
OpenRouter's catalog and live pricing at https://openrouter.ai/models if
you want an even cheaper (or different) main model.
