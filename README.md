# UPSC Q&A Chatbot

A Streamlit chatbot that answers UPSC Civil Services Examination questions
(Prelims, Mains, Essay) with clear, exam-ready explanations, powered by the
Claude API.

## Features

- ChatGPT-style layout: conversation history on top, a query box pinned to
  the bottom of the screen (Streamlit's native `st.chat_input`).
- System prompt tuned for UPSC answers: direct answer first, then a plain
  explanation, syllabus/current-affairs relevance, and a quick revision
  recap.
- Sidebar with example questions, a model picker (Opus 5 / Sonnet 5 /
  Haiku 4.5), and a "Clear conversation" button.
- Streamed responses (tokens appear as they're generated).

## Setup

```bash
cd upsc-chatbot
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your key:

```
ANTHROPIC_API_KEY=sk-ant-...
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
ANTHROPIC_API_KEY = "sk-ant-..."
```

(or create `.streamlit/secrets.toml` locally with the same content — it is
git-ignored).

## Changing the model / cost

The sidebar model picker defaults to `claude-opus-5`. Switch to
`claude-sonnet-5` or `claude-haiku-4-5` for a cheaper/faster chatbot if
Opus-level depth isn't needed for every question.
