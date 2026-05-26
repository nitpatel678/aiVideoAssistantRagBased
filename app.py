import html
import os
import re

import streamlit as st
from dotenv import load_dotenv
from markdown_it import MarkdownIt

from core.rag_engine import ask_question
from main import run_pipeline


load_dotenv()

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&display=swap');

:root {
    --bg: #030604;
    --panel: rgba(10, 18, 13, 0.62);
    --panel-2: rgba(12, 24, 17, 0.72);
    --line: rgba(255, 255, 255, 0.14);
    --muted: rgba(255, 255, 255, 0.70);
    --green: #30f28a;
    --green-2: #b7ff4a;
    --white: #f7fff9;
    --glass: rgba(255, 255, 255, 0.07);
    --glass-strong: rgba(255, 255, 255, 0.11);
}

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 16% 2%, rgba(48, 242, 138, 0.18), transparent 32rem),
        radial-gradient(circle at 80% 12%, rgba(183, 255, 74, 0.10), transparent 24rem),
        linear-gradient(145deg, #020302 0%, #07100b 48%, #020504 100%);
    color: var(--white);
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(255,255,255,.075), rgba(255,255,255,.035)),
        rgba(4, 8, 6, 0.72);
    border-right: 1px solid rgba(255,255,255,.12);
    box-shadow: 24px 0 80px rgba(0, 0, 0, 0.38);
    backdrop-filter: blur(22px) saturate(155%);
    -webkit-backdrop-filter: blur(22px) saturate(155%);
}

[data-testid="stSidebar"] * {
    color: var(--white);
}

[data-testid="stSidebar"] > div {
    padding-top: 1.35rem;
}

[data-testid="stSidebar"] h3 {
    font-size: 1.15rem;
    font-weight: 900;
    margin-bottom: 1.15rem;
}

.block-container {
    max-width: 1360px;
    padding-top: 5rem;
    padding-bottom: 3rem;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 2.4rem;
    padding-top: .4rem;
}

.brand {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}

.brand-mark {
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border: 1px solid rgba(48, 242, 138, 0.42);
    border-radius: 8px;
    background: linear-gradient(145deg, rgba(48, 242, 138, 0.18), rgba(255, 255, 255, 0.04));
    color: var(--green);
    font-weight: 900;
}

.brand-title {
    font-size: 0.94rem;
    font-weight: 800;
    letter-spacing: 0;
    text-transform: uppercase;
}

.status-pill {
    border: 1px solid rgba(48, 242, 138, 0.38);
    border-radius: 999px;
    padding: 0.55rem 0.85rem;
    color: var(--green);
    background: rgba(48, 242, 138, 0.08);
    font-size: 0.82rem;
    font-weight: 800;
    white-space: nowrap;
}

.hero {
    padding: 1.6rem 0 1.6rem;
}

.kicker {
    color: var(--green);
    font-size: 0.82rem;
    font-weight: 900;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

.hero h1 {
    color: var(--white);
    font-size: clamp(2.5rem, 6vw, 6.6rem);
    line-height: 0.94;
    letter-spacing: 0;
    margin: 0 0 1rem;
    font-weight: 900;
}

.gradient-text {
    background: linear-gradient(90deg, #ffffff 0%, #30f28a 45%, #b7ff4a 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hero p {
    color: var(--muted);
    max-width: 760px;
    font-size: 1.05rem;
    line-height: 1.7;
    margin: 0;
    font-weight: 600;
}

.metric-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.8rem;
    margin: 1.7rem 0 1.4rem;
}

.metric {
    border: 1px solid rgba(255,255,255,.13);
    background: linear-gradient(145deg, rgba(255,255,255,.10), rgba(255,255,255,.045));
    border-radius: 8px;
    padding: 1rem;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}

.metric strong {
    display: block;
    color: var(--green);
    font-size: 1.3rem;
    font-weight: 900;
}

.metric span {
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
}

.section-title {
    color: var(--white);
    font-size: 1.28rem;
    font-weight: 900;
    margin: 1.35rem 0 1rem;
    line-height: 1.35;
}

.result-box {
    border: 1px solid rgba(255,255,255,.13);
    background:
        linear-gradient(145deg, rgba(255,255,255,.10), rgba(255,255,255,.042)),
        rgba(6, 12, 8, .52);
    border-radius: 8px;
    padding: 1.35rem 1.45rem;
    color: rgba(255, 255, 255, 0.84);
    line-height: 1.72;
    backdrop-filter: blur(20px) saturate(150%);
    -webkit-backdrop-filter: blur(20px) saturate(150%);
    box-shadow: 0 24px 70px rgba(0,0,0,.26);
}

.result-box h3 {
    margin: 0 0 0.6rem;
    color: var(--green);
    font-size: 0.9rem;
    font-weight: 900;
    text-transform: uppercase;
}

.result-label {
    color: var(--green);
    font-size: 0.78rem;
    font-weight: 900;
    letter-spacing: .06rem;
    margin-bottom: 1rem;
    text-transform: uppercase;
}

.result-box h1,
.result-box h2,
.result-box h3,
.result-box h4 {
    color: var(--white);
    letter-spacing: 0;
}

.result-box h1 {
    font-size: 1.45rem;
}

.result-box h2 {
    font-size: 1.24rem;
    margin-top: 1.1rem;
}

.result-box h3 {
    font-size: 1.02rem;
    margin-top: 1rem;
}

.result-box p {
    margin: .62rem 0;
}

.result-box ul,
.result-box ol {
    padding-left: 1.25rem;
    margin: .65rem 0 1rem;
}

.result-box li {
    margin: .35rem 0;
}

.result-box strong {
    color: #dfffea;
    font-weight: 900;
}

.stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stTextArea textarea {
    background: rgba(255, 255, 255, 0.085) !important;
    border: 1px solid rgba(255,255,255,.16) !important;
    border-radius: 8px !important;
    color: var(--white) !important;
    min-height: 3.15rem;
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02) !important;
    font-weight: 700;
}

.stTextInput input::placeholder {
    color: rgba(255, 255, 255, 0.42) !important;
}

[data-testid="InputInstructions"] {
    display: none !important;
}

[data-testid="stSidebar"] .stTextInput,
[data-testid="stSidebar"] .stSelectbox {
    margin-bottom: 1.05rem;
}

.sidebar-label {
    color: rgba(255,255,255,.72);
    font-size: .78rem;
    font-weight: 900;
    margin-bottom: .5rem;
    text-transform: uppercase;
}

.stButton > button {
    width: 100%;
    min-height: 3.1rem;
    border: 1px solid rgba(255,255,255,.18) !important;
    border-radius: 8px;
    background:
        linear-gradient(90deg, rgba(48,242,138,.95), rgba(183,255,74,.95)) !important;
    color: #031009 !important;
    font-weight: 900;
    box-shadow: 0 18px 42px rgba(48, 242, 138, 0.18), inset 0 1px 0 rgba(255,255,255,.55);
}

.stButton > button * {
    color: #061009 !important;
    font-weight: 900 !important;
}

.stButton > button:hover {
    border: 1px solid rgba(183, 255, 74, 0.75) !important;
    color: #061009 !important;
    transform: translateY(-1px);
    filter: brightness(1.03);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.55rem;
    padding: .35rem;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 8px;
    background: rgba(255,255,255,.045);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.10);
    background: rgba(255, 255, 255, 0.055);
    color: var(--white);
    font-weight: 800;
    padding: .62rem .82rem;
}

.stTabs [aria-selected="true"] {
    color: #04110a !important;
    background: linear-gradient(90deg, #30f28a, #b7ff4a) !important;
    border-color: rgba(255,255,255,.26);
    box-shadow: 0 10px 24px rgba(48,242,138,.16);
}

.stTabs [aria-selected="true"] * {
    color: #04110a !important;
    font-weight: 900 !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.15rem;
}

[data-testid="stChatMessage"] {
    border: 1px solid rgba(255,255,255,.11);
    background: rgba(255,255,255,.055);
    border-radius: 8px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

@media (max-width: 820px) {
    .topbar, .metric-row {
        grid-template-columns: 1fr;
        display: grid;
    }
    .status-pill {
        width: fit-content;
    }
    .block-container {
        padding-top: 4.4rem;
    }
}
</style>
"""


MARKDOWN = MarkdownIt("commonmark", {"html": False}).enable("table")


def clean_inline_markdown(text: str) -> str:
    cleaned = re.sub(r"^[#*\s]+|[#*\s]+$", "", text or "")
    return cleaned.strip() or "AI Video Assistant"


def render_markdown_box(title: str, content: str) -> None:
    rendered = MARKDOWN.render(content or "No content generated yet.")
    st.markdown(
        f"""
        <div class="result-box">
            <div class="result-label">{html.escape(title)}</div>
            <div>{rendered}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if "result" not in st.session_state:
    st.session_state.result = None
if "messages" not in st.session_state:
    st.session_state.messages = []


st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <div class="brand-mark">AI</div>
            <div>
                <div class="brand-title">AI Video Assistant</div>
                <div style="color: rgba(255,255,255,.58); font-size: .82rem; font-weight: 700;">Transcript intelligence workspace</div>
            </div>
        </div>
        <div class="status-pill">LLM + Whisper + RAG</div>
    </div>
    <section class="hero">
        <div class="kicker">Video to insight pipeline</div>
        <h1>Turn recordings into <span class="gradient-text">answers.</span></h1>
        <p>Drop in a YouTube URL or local media path, then generate a title, summary, action items, decisions, open questions, transcript, and a chat-ready knowledge base.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Source")
    st.markdown("<div class='sidebar-label'>YouTube URL or local file path</div>", unsafe_allow_html=True)
    source = st.text_input(
        "YouTube URL or local file path",
        placeholder="https://youtube.com/watch?v=...",
        label_visibility="collapsed",
    )
    st.markdown("<div class='sidebar-label'>Language mode</div>", unsafe_allow_html=True)
    language = st.selectbox("Language mode", ["english", "hinglish"], index=0, label_visibility="collapsed")
    run_clicked = st.button("Analyze Video", type="primary")

    st.markdown("---")
    st.markdown("### System")
    has_mistral = bool(os.getenv("MISTRAL_API_KEY"))
    has_sarvam = bool(os.getenv("SARVAM_API_KEY"))
    st.caption(f"Mistral key: {'Ready' if has_mistral else 'missing'}")
    st.caption(f"Sarvam key: {'Ready' if has_sarvam else 'optional'}")
    st.caption(f"Embedding device: {os.getenv('EMBEDDING_DEVICE', 'cpu')}")


if run_clicked:
    if not source.strip():
        st.error("Add a YouTube URL or local file path first.")
    elif language == "hinglish" and not os.getenv("SARVAM_API_KEY"):
        st.error("Hinglish mode requires SARVAM_API_KEY in your .env file.")
    else:
        try:
            with st.spinner("Processing audio, transcribing, summarizing, and building RAG..."):
                st.session_state.result = run_pipeline(source.strip(), language)
                st.session_state.messages = []
            st.success("Analysis complete.")
        except Exception as exc:
            st.session_state.result = None
            error_message = str(exc)
            st.error(error_message)
            if "YouTube blocked" in error_message or "HTTP 403" in error_message:
                st.info(
                    "This can happen on Streamlit Cloud because YouTube often blocks "
                    "datacenter requests. Try another public video, redeploy after "
                    "yt-dlp updates, or add YouTube cookies as YOUTUBE_COOKIES_TEXT "
                    "in Streamlit secrets."
                )
            else:
                st.info(
                    "Try a shorter video, confirm the source has audible speech, or set "
                    "WHISPER_MODEL=base/tiny in .env for faster local transcription."
                )


result = st.session_state.result

if result:
    transcript_words = len(result["transcript"].split())
    action_lines = len([line for line in result["action_items"].splitlines() if line.strip()])
    question_lines = len([line for line in result["open_questions"].splitlines() if line.strip()])

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric"><strong>{transcript_words}</strong><span>Transcript words</span></div>
            <div class="metric"><strong>{action_lines}</strong><span>Action signals</span></div>
            <div class="metric"><strong>{question_lines}</strong><span>Open questions</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='section-title'>{html.escape(clean_inline_markdown(result['title']))}</div>",
        unsafe_allow_html=True,
    )

    summary_tab, actions_tab, decisions_tab, questions_tab, transcript_tab, chat_tab = st.tabs(
        ["Summary", "Actions", "Decisions", "Questions", "Transcript", "Ask"]
    )

    with summary_tab:
        render_markdown_box("Summary", result["summary"])

    with actions_tab:
        render_markdown_box("Action Items", result["action_items"])

    with decisions_tab:
        render_markdown_box("Key Decisions", result["key_decisions"])

    with questions_tab:
        render_markdown_box("Open Questions", result["open_questions"])

    with transcript_tab:
        st.text_area("Transcript", value=result["transcript"], height=420)

    with chat_tab:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        prompt = st.chat_input("Ask anything from this video")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Searching transcript context..."):
                    answer = ask_question(result["rag_chain"], prompt)
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
else:
    st.markdown(
        """
        <div class="metric-row">
            <div class="metric"><strong>01</strong><span>Add source</span></div>
            <div class="metric"><strong>02</strong><span>Run analysis</span></div>
            <div class="metric"><strong>03</strong><span>Chat with context</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
