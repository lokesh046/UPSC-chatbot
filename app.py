import os

import streamlit as st
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from xai_sdk import Client as XaiClient
from xai_sdk.chat import assistant as xai_assistant
from xai_sdk.chat import system as xai_system
from xai_sdk.chat import user as xai_user

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

GEMINI_MODEL = "gemini-flash-latest"
GROK_MODEL = "grok-4-fast-non-reasoning"

SYSTEM_PROMPT = """You are an expert UPSC (Union Public Service Commission) \
Civil Services Examination mentor. Aspirants ask you Prelims, Mains, and \
Essay-type questions from any subject (Polity, History, Geography, Economy, \
Environment, Science & Tech, Ethics, Current Affairs, CSAT, etc.).

For every question, explain it clearly and in an exam-ready way. Structure \
your answer with short markdown headings when useful:
- **Direct Answer** - the core answer up front (for MCQs, state the correct \
  option and why the others are wrong).
- **Explanation** - break the concept down simply, as if teaching a student \
  new to the topic.
- **UPSC Relevance** - how this connects to the Prelims/Mains syllabus, and \
  static + current affairs linkages where relevant.
- **Quick Recap** - 2-4 bullet points an aspirant could use for revision.

Keep language simple and precise. Avoid unnecessary padding. If a question \
is ambiguous or you are not fully certain of a fact (dates, statistics, \
amendment numbers), say so explicitly rather than guessing."""

st.set_page_config(
    page_title="UPSC Q&A Chatbot",
    page_icon="\U0001F3DB️",
    layout="centered",
)

st.markdown(
    """
    <style>
    .upsc-banner {
        background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
        padding: 3px;
        border-radius: 10px;
        margin-bottom: 0.75rem;
    }
    .upsc-banner-inner {
        background: #0B3D91;
        border-radius: 8px;
        padding: 1.1rem 1.4rem;
        text-align: center;
    }
    .upsc-banner-inner h1 {
        color: #FFFFFF;
        font-size: 1.6rem;
        margin: 0;
    }
    .upsc-banner-inner p {
        color: #E6ECFA;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }
    </style>
    <div class="upsc-banner">
      <div class="upsc-banner-inner">
        <h1>\U0001F3DB️ UPSC Q&amp;A Chatbot</h1>
        <p>Ask any Prelims, Mains or Essay question &mdash; get a clear, exam-ready explanation.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

EXAMPLE_QUESTIONS = [
    "Explain the difference between Fundamental Rights and Directive Principles of State Policy.",
    "What is the significance of the Preamble in the Indian Constitution?",
    "Discuss the causes and consequences of the 1991 Balance of Payments crisis.",
    "What are Western Disturbances and how do they affect Indian agriculture?",
]

with st.sidebar:
    st.header("Settings")
    st.subheader("Try an example")
    example_clicked = None
    for q in EXAMPLE_QUESTIONS:
        if st.button(q, use_container_width=True):
            example_clicked = q

    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


def get_gemini_api_key():
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        return None


def get_xai_api_key():
    key = os.environ.get("XAI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("XAI_API_KEY")
    except Exception:
        return None


@st.cache_resource
def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)


@st.cache_resource
def get_xai_client(api_key: str):
    return XaiClient(api_key=api_key)


gemini_api_key = get_gemini_api_key()
if not gemini_api_key:
    st.error(
        "No Gemini API key found. Set the `GEMINI_API_KEY` environment "
        "variable (e.g. in a `.env` file) or add it to "
        "`.streamlit/secrets.toml`, then restart the app."
    )
    st.stop()

gemini_client = get_gemini_client(gemini_api_key)

xai_api_key = get_xai_api_key()
xai_client = get_xai_client(xai_api_key) if xai_api_key else None

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "\U0001F9D1‍\U0001F393" if msg["role"] == "user" else "\U0001F3DB️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your UPSC question here...")
prompt = example_clicked or user_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="\U0001F9D1‍\U0001F393"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="\U0001F3DB️"):
        gemini_contents = [
            types.Content(
                role="user" if m["role"] == "user" else "model",
                parts=[types.Part(text=m["content"])],
            )
            for m in st.session_state.messages
        ]

        used_fallback = {"value": False}

        def stream_gemini():
            for chunk in gemini_client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=gemini_contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=4096,
                ),
            ):
                if chunk.text:
                    yield chunk.text

        def stream_grok():
            xai_messages = [xai_system(SYSTEM_PROMPT)]
            for m in st.session_state.messages:
                xai_messages.append(
                    xai_user(m["content"])
                    if m["role"] == "user"
                    else xai_assistant(m["content"])
                )
            chat = xai_client.chat.create(model=GROK_MODEL, messages=xai_messages)
            for _, chunk in chat.stream():
                if chunk.content:
                    yield chunk.content

        def stream_answer():
            try:
                yield from stream_gemini()
            except Exception:
                if not xai_client:
                    raise
                used_fallback["value"] = True
                yield from stream_grok()

        full_response = None
        try:
            full_response = st.write_stream(stream_answer)
        except genai_errors.ClientError as e:
            if e.code in (400, 401, 403) and "API key" in (e.message or ""):
                st.error("Invalid Gemini API key. Check `GEMINI_API_KEY` and try again.")
            elif e.code == 429:
                st.error("Rate limited by the Gemini API. Please wait a moment and try again.")
            else:
                st.error(f"Gemini API error: {e.message or e}")
        except genai_errors.ServerError as e:
            st.error(f"Gemini API server error, please retry: {e.message or e}")
        except genai_errors.APIError as e:
            st.error(f"Gemini API error: {e.message or e}")
        except Exception as e:
            st.error(f"Grok API error: {e}")

        if used_fallback["value"] and full_response:
            st.caption("⚡ Answered by Grok (Gemini was unavailable)")

    if full_response:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
