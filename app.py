import hashlib
import streamlit as st

from ingestion import extract_pdf_chunks
from retrieval import search_chunks
from tutor import answer_question
from quiz import generate_quiz
from config import has_api_key, redact, explain_error
from learner_model import init_db, save_attempt, get_mastery, update_mastery


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Mi(a) Ai",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()


# =========================================================
# PREMIUM DARK UI
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
      --bg: #0b0c12;
      --panel: #14151f;
      --panel2: #1b1c29;
      --line: #292a3a;
      --text: #f4f4fb;
      --muted: #a2a4b8;
      --violet: #8b5cf6;
      --violet2: #6d28d9;
    }

    html, body, [class*="css"] {
      font-family: 'Inter', sans-serif;
    }
    .stApp {
      background:
        radial-gradient(ellipse at 82% 0%, rgba(109,40,217,.13), transparent 35%),
        #0b0c12;
      color: var(--text);
    }
    [data-testid="stHeader"] { background: rgba(11,12,18,.92); }
    .block-container {
      max-width: 1600px;
      padding-top: 1.4rem;
      padding-bottom: 2.5rem;
    }
    [data-testid="stSidebar"] {
      background: #10111a;
      border-right: 1px solid #252636;
    }
    [data-testid="stSidebar"] > div { padding-top: 1.4rem; }
    h1, h2, h3, h4, p, label { color: var(--text); }
    .brand {
      font-size: 1.35rem; font-weight: 800; letter-spacing: -.7px;
      color: #fff; padding: 6px 0 2px 0;
    }
    .brand span { color: #a78bfa; }
    .subbrand { color: #9294aa; font-size: .78rem; margin-bottom: 18px; }
    .hero {
      background: linear-gradient(115deg, #211638 0%, #2a1c48 45%, #191a2a 100%);
      border: 1px solid #3a2b58; border-radius: 22px;
      padding: 27px 30px; margin-bottom: 20px;
      box-shadow: 0 15px 40px rgba(0,0,0,.18);
    }
    .eyebrow {
      color: #c4b5fd; font-size: .72rem; font-weight: 800;
      letter-spacing: 1.8px; text-transform: uppercase; margin-bottom: 9px;
    }
    .hero-title {
      font-size: 2rem; font-weight: 800; letter-spacing: -1px;
      line-height: 1.15; margin: 0 0 9px 0; color: #fff;
    }
    .hero-copy { color: #d5cde8; font-size: .93rem; line-height: 1.6; margin: 0; }
    .panel {
      background: linear-gradient(145deg, #171823, #12131c);
      border: 1px solid #292a3a; border-radius: 18px;
      padding: 19px 20px; margin-bottom: 14px;
    }
    .panel-title { font-weight: 700; font-size: 1rem; margin-bottom: 5px; color: #f5f3ff; }
    .muted { color: var(--muted); font-size: .83rem; line-height: 1.55; }
    .metric {
      background: linear-gradient(145deg, #1a1727, #151620);
      border: 1px solid #302641; border-radius: 16px;
      padding: 17px 18px; min-height: 106px;
    }
    .metric-label { color: #aaa8bf; font-size: .77rem; font-weight: 600; }
    .metric-value { color: #fff; font-size: 1.65rem; font-weight: 800; margin: 7px 0 2px; }
    .metric-hint { color: #8f91a8; font-size: .72rem; }
    .status-pill {
      display: inline-block; border: 1px solid #443365; color: #c4b5fd;
      background: #241b37; border-radius: 100px; padding: 5px 10px;
      font-size: .72rem; font-weight: 600;
    }
    .stButton > button, .stDownloadButton > button {
      border-radius: 10px; min-height: 40px; font-weight: 600;
      border: 1px solid #343548; background: #20212e; color: #f5f3ff;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
      border-color: #8b5cf6; color: #fff; background: #2a2140;
    }
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
      background: linear-gradient(100deg, #7c3aed, #6d28d9);
      border: 1px solid #8b5cf6; color: white;
    }
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover { background: #6d28d9; }
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {
      background: #171823; color: #f5f3ff; border-color: #333447; border-radius: 10px;
    }
    [data-testid="stFileUploader"] {
      background: #151620; border: 1px dashed #49405f;
      border-radius: 14px; padding: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
      gap: 8px; border-bottom: 1px solid #292a3a;
    }
    .stTabs [data-baseweb="tab"] {
      background: #151620; border: 1px solid #292a3a;
      border-radius: 10px 10px 0 0; padding: 11px 15px;
      color: #b7b8ca; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
      background: #28203b !important; color: #d8ccff !important;
      border-color: #6d4ca0 !important;
    }
    [data-testid="stExpander"] {
      background: #151620; border: 1px solid #2a2b3c; border-radius: 12px;
    }
    [data-testid="stChatMessage"] {
      background: #151620; border: 1px solid #292a3a; border-radius: 14px;
      padding: 12px 14px;
    }
    [data-testid="stProgressBar"] > div {
      background: #30283e; border-radius: 20px;
    }
    [data-testid="stProgressBar"] > div > div {
      background: linear-gradient(90deg, #7c3aed, #c084fc);
      border-radius: 20px;
    }
    [data-testid="stMetric"] {
      background: #171823; padding: 13px 15px; border-radius: 12px;
      border: 1px solid #2a2b3c;
    }
    hr { border-color: #292a3a; }
    .footer { text-align: center; color: #77798f; font-size: .74rem; padding-top: 25px; }
    @media (max-width: 768px) {
      .hero { padding: 21px; }
      .hero-title { font-size: 1.55rem; }
      .block-container { padding-top: .8rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================
DEFAULTS = {
    "file_signature": None,
    "chunks": [],
    "chat_history": [],
    "quiz": None,
    "quiz_meta": {},
    "quiz_results": None,
    "quiz_counter": 0,
    "document_name": None,
    "pending_question": None,
    "active_section": "Overview",
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HELPERS
# =========================================================
def metric_card(label, value, hint):
    st.markdown(
        f"""
        <div class="metric">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-hint">{hint}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_filename(name):
    cleaned = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)
    return cleaned or "mia_ai_export"


def export_chat(history):
    rows = ["Mi(a) AI — Conversation Export", "=" * 36, ""]
    for item in history:
        rows.append(item["role"].upper())
        rows.append(item["content"])
        rows.append("")
    return "\n".join(rows)


def source_text(chunks):
    rows = []
    for chunk in chunks:
        rows.append(
            f"Source: {chunk.get('source', 'Uploaded PDF')}\n"
            f"Page: {chunk.get('page', 'Unknown')}\n\n"
            f"{chunk.get('text', '')}\n\n{'-' * 60}"
        )
    return "\n\n".join(rows)


def render_sources(matches):
    for index, chunk in enumerate(matches, 1):
        src = chunk.get("source", "Uploaded PDF")
        page = chunk.get("page", "?")
        with st.expander(f"📄 {src}  ·  Page {page}  ·  Passage {index}"):
            st.write(chunk.get("text", ""))


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown('<div class="brand">📚 Mi(a) <span>AI</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="subbrand">Your personal learning system</div>', unsafe_allow_html=True)
    st.divider()

    section = st.radio(
        "WORKSPACE",
        ["Overview", "AI Tutor", "Topic Quiz", "Source Explorer", "My Progress"],
        label_visibility="visible",
        key="nav_section",
    )

    st.divider()
    st.markdown("#### Document library")
    uploaded = st.file_uploader(
        "Add a course PDF",
        type=["pdf"],
        help="Upload a selectable-text PDF. Scanned files may need OCR.",
        key="course_pdf_uploader",
    )

    if has_api_key():
        st.success("AI connection configured")
    else:
        st.error("API key not detected")
        st.caption("Check your .env file and restart Streamlit.")

    if st.session_state["document_name"]:
        st.markdown("#### Current document")
        st.markdown(f"**{st.session_state['document_name']}**")
        st.caption(f"{len(st.session_state['chunks'])} searchable passages")
        if st.button("Reset current workspace", use_container_width=True):
            for key in [
                "file_signature", "chunks", "chat_history", "quiz",
                "quiz_meta", "quiz_results", "quiz_counter", "document_name",
                "pending_question",
            ]:
                st.session_state[key] = DEFAULTS.get(key)
            st.rerun()

    st.markdown("---")
    st.caption("Mi(a) AI · Study with your own materials")


# =========================================================
# PROCESS PDF
# =========================================================
if uploaded is not None:
    file_bytes = uploaded.getvalue()
    signature = f"{uploaded.name}:{hashlib.sha256(file_bytes).hexdigest()}"

    if st.session_state["file_signature"] != signature:
        try:
            with st.spinner("Reading PDF and indexing source passages..."):
                extracted = extract_pdf_chunks(file_bytes, uploaded.name)

            st.session_state["chunks"] = extracted
            st.session_state["file_signature"] = signature
            st.session_state["document_name"] = uploaded.name
            st.session_state["chat_history"] = []
            st.session_state["quiz"] = None
            st.session_state["quiz_meta"] = {}
            st.session_state["quiz_results"] = None
            st.session_state["quiz_counter"] = 0
        except Exception as exc:
            st.error("Could not process this PDF: " + explain_error(exc))
            st.stop()

chunks = st.session_state["chunks"]


# =========================================================
# TOP HEADER
# =========================================================
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">PERSONAL KNOWLEDGE WORKSPACE</div>
      <div class="hero-title">Your second brain for learning.</div>
      <p class="hero-copy">
        Turn course PDFs into clear answers, focused practice, and measurable progress.
        Everything stays connected to your learning material.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not chunks:
    st.markdown(
        """
        <div class="panel">
          <div class="panel-title">Welcome to Mi(a) AI</div>
          <p class="muted">
            Upload a course PDF using the left sidebar to get started.
            You can then ask source-grounded questions, generate quizzes,
            search passages, and track your topic mastery.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(
    f'<span class="status-pill">● Document ready</span> &nbsp; '
    f'<span class="muted">{st.session_state["document_name"]} · {len(chunks)} passages indexed</span>',
    unsafe_allow_html=True,
)

mastery_data = get_mastery() or []
total_attempts = sum(int(item.get("attempts", 0)) for item in mastery_data)
avg_mastery = (
    sum(float(item.get("mastery", 0)) for item in mastery_data) / len(mastery_data)
    if mastery_data else 0
)
question_count = sum(1 for item in st.session_state["chat_history"] if item["role"] == "user")

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("📚 Source passages", len(chunks), "Retrieved from your PDF")
with m2:
    metric_card("💬 Tutor questions", question_count, "This session")
with m3:
    metric_card("📝 Quiz attempts", total_attempts, "Saved to learner profile")
with m4:
    metric_card("◉ Average mastery", f"{avg_mastery:.0%}", "Across tracked topics")

st.write("")


# =========================================================
# OVERVIEW
# =========================================================
if section == "Overview":
    left, right = st.columns([1.35, 1])

    with left:
        st.markdown('<div class="panel-title">Pick up where you left off</div>', unsafe_allow_html=True)
        st.markdown('<p class="muted">Choose a learning activity to continue.</p>', unsafe_allow_html=True)

        a, b = st.columns(2)
        with a:
            with st.container(border=True):
                st.markdown("### 💬 AI Tutor")
                st.markdown('<p class="muted">Ask questions and get answers grounded in your uploaded course notes.</p>', unsafe_allow_html=True)
                st.button("Open AI Tutor →", key="overview_tutor", type="primary", use_container_width=True)
                st.caption("Choose AI Tutor from the sidebar to open it.")
        with b:
            with st.container(border=True):
                st.markdown("### 📝 Topic Quiz")
                st.markdown('<p class="muted">Generate practice questions at your preferred difficulty.</p>', unsafe_allow_html=True)
                st.button("Start a quiz →", key="overview_quiz", use_container_width=True)
                st.caption("Choose Topic Quiz from the sidebar to open it.")

        a, b = st.columns(2)
        with a:
            with st.container(border=True):
                st.markdown("### 🔎 Source Explorer")
                st.markdown('<p class="muted">Search extracted passages and check page references.</p>', unsafe_allow_html=True)
                st.button("Explore sources →", key="overview_sources", use_container_width=True)
                st.caption("Choose Source Explorer from the sidebar to open it.")
        with b:
            with st.container(border=True):
                st.markdown("### 📈 Learning progress")
                st.markdown('<p class="muted">Review topic mastery and find what to revise next.</p>', unsafe_allow_html=True)
                st.button("View progress →", key="overview_progress", use_container_width=True)
                st.caption("Choose My Progress from the sidebar to open it.")

    with right:
        st.markdown('<div class="panel-title">Your study snapshot</div>', unsafe_allow_html=True)
        if mastery_data:
            weakest = min(mastery_data, key=lambda x: float(x.get("mastery", 0)))
            st.markdown(f"**Suggested revision: {str(weakest.get('topic', 'Topic')).title()}**")
            st.progress(max(0.0, min(1.0, float(weakest.get("mastery", 0)))))
            st.caption(f"Estimated mastery: {float(weakest.get('mastery', 0)):.0%}")
        else:
            st.markdown("**Your learning profile is ready to build.**")
            st.markdown('<p class="muted">Complete your first quiz to see mastery estimates and revision suggestions here.</p>', unsafe_allow_html=True)

        st.divider()
        st.markdown("**Quick prompts**")
        quick_prompts = [
            "Summarize the main concepts in this PDF",
            "List the important formulas and explain each",
            "Create an exam revision checklist",
        ]
        for idx, prompt in enumerate(quick_prompts):
            if st.button(prompt, key=f"quick_prompt_{idx}", use_container_width=True):
                st.session_state["pending_question"] = prompt
                st.info("Prompt saved for this session. Choose AI Tutor in the sidebar to ask it.")


# =========================================================
# AI TUTOR
# =========================================================
elif section == "AI Tutor":
    st.markdown("## AI Tutor")
    st.markdown('<p class="muted">Ask questions about your uploaded document. Source passages are shown with each answer.</p>', unsafe_allow_html=True)

    tools_col1, tools_col2 = st.columns([1, 1])
    with tools_col1:
        if st.session_state["chat_history"]:
            st.download_button(
                "⬇ Export conversation",
                data=export_chat(st.session_state["chat_history"]),
                file_name="mia_ai_conversation.txt",
                mime="text/plain",
                use_container_width=True,
            )
    with tools_col2:
        if st.button("Clear conversation", use_container_width=True):
            st.session_state["chat_history"] = []
            st.session_state["pending_question"] = None
            st.rerun()

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    typed_question = st.chat_input("Ask something about your course material...")
    question = typed_question or st.session_state.pop("pending_question", None)

    if question:
        st.session_state["chat_history"].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        matches = search_chunks(question, chunks, top_k=4)
        with st.chat_message("assistant"):
            response = None
            if not matches:
                response = (
                    "I couldn't find a relevant passage in the uploaded material. "
                    "Try using terminology that appears in your notes."
                )
                st.info(response)
            else:
                try:
                    with st.spinner("Finding relevant passages and preparing an answer..."):
                        response = answer_question(question, matches)
                    st.markdown(response)
                    with st.expander("📚 Supporting source passages"):
                        render_sources(matches)
                except Exception as exc:
                    st.error(explain_error(exc))
                    st.code(redact(str(exc)))

            if response:
                st.session_state["chat_history"].append(
                    {"role": "assistant", "content": response}
                )


# =========================================================
# TOPIC QUIZ
# =========================================================
elif section == "Topic Quiz":
    st.markdown("## Topic Quiz")
    st.markdown('<p class="muted">Build a focused practice session from your course material.</p>', unsafe_allow_html=True)

    with st.container(border=True):
        with st.form("quiz_setup"):
            topic = st.text_input("Topic", placeholder="e.g. Hall effect, kinetics, crystal structures")
            c1, c2 = st.columns(2)
            with c1:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
            with c2:
                num_questions = st.selectbox("Number of questions", [3, 5], index=0)
            make_quiz = st.form_submit_button("✨ Generate quiz", type="primary", use_container_width=True)

    if make_quiz:
        if not topic.strip():
            st.warning("Enter a topic first.")
        else:
            topic_chunks = search_chunks(topic, chunks, top_k=8)
            if not topic_chunks:
                st.warning("No relevant text found. Try a term used in the PDF.")
            else:
                try:
                    with st.spinner("Creating questions from the retrieved course material..."):
                        new_quiz = generate_quiz(topic, difficulty, num_questions, topic_chunks)
                    if not new_quiz:
                        st.warning("No questions were generated. Try again.")
                    else:
                        st.session_state["quiz"] = new_quiz
                        st.session_state["quiz_meta"] = {
                            "topic": topic.strip(),
                            "difficulty": difficulty,
                        }
                        st.session_state["quiz_results"] = None
                        st.session_state["quiz_counter"] += 1
                        st.rerun()
                except Exception as exc:
                    st.error("Quiz generation failed: " + explain_error(exc))
                    st.code(redact(str(exc)))

    quiz = st.session_state.get("quiz")
    meta = st.session_state.get("quiz_meta", {})

    if quiz:
        quiz_topic = meta.get("topic", "Course topic")
        quiz_difficulty = meta.get("difficulty", "Medium")
        quiz_id = st.session_state["quiz_counter"]

        st.divider()
        st.markdown(f"### {quiz_topic}")
        st.markdown(f'<span class="status-pill">{len(quiz)} questions</span> &nbsp; <span class="status-pill">{quiz_difficulty}</span>', unsafe_allow_html=True)

        if st.session_state.get("quiz_results") is None:
            with st.form(f"quiz_form_{quiz_id}"):
                chosen = {}
                for i, q in enumerate(quiz):
                    st.markdown(f"**Q{i + 1}. {q['question']}**")
                    chosen[i] = st.radio(
                        "Choose one answer",
                        q["options"],
                        key=f"quiz_{quiz_id}_{i}",
                        index=None,
                        label_visibility="collapsed",
                    )
                    st.write("")
                submitted = st.form_submit_button("Check answers", type="primary", use_container_width=True)

            if submitted:
                results, correct_count = [], 0
                for i, q in enumerate(quiz):
                    answer = chosen.get(i)
                    correct = (
                        answer is not None
                        and answer.strip().casefold() == q["answer"].strip().casefold()
                    )
                    correct_count += int(correct)
                    save_attempt(
                        topic=quiz_topic,
                        question_id=q.get("id", str(i)),
                        is_correct=correct,
                        difficulty=quiz_difficulty,
                        source=q.get("source", "Uploaded course material"),
                    )
                    results.append({"q": q, "correct": correct, "given": answer})

                update_mastery(quiz_topic, correct_count / max(len(quiz), 1))
                st.session_state["quiz_results"] = {"items": results, "score": correct_count}
                st.rerun()

        result = st.session_state.get("quiz_results")
        if result is not None:
            score = result["score"]
            total = len(result["items"])
            accuracy = score / max(total, 1)
            st.markdown("### Your results")
            r1, r2 = st.columns(2)
            with r1:
                st.metric("Score", f"{score}/{total}")
            with r2:
                st.metric("Accuracy", f"{accuracy:.0%}")
            st.progress(accuracy)

            if accuracy == 1:
                st.success("Perfect score — excellent work!")
            elif accuracy >= 0.6:
                st.info("Good progress. Review the missed questions to improve.")
            else:
                st.warning("Review the explanations below, then try another quiz.")

            lines = [
                "Mi(a) AI — Quiz Review",
                f"Topic: {quiz_topic}",
                f"Difficulty: {quiz_difficulty}",
                f"Score: {score}/{total} ({accuracy:.0%})",
                "",
            ]
            for i, item in enumerate(result["items"], 1):
                q = item["q"]
                st.markdown(f"**Q{i}: {'✅ Correct' if item['correct'] else '❌ Review this'}**")
                st.write(q["question"])
                st.caption(f"Your answer: {item['given'] or 'Not answered'}")
                st.write(f"Correct answer: {q['answer']}")
                st.write(q.get("explanation", "Review the relevant source passage."))
                if q.get("source"):
                    st.caption(f"Source: {q['source']}")
                lines.extend([
                    f"Q{i}: {q['question']}",
                    f"Your answer: {item['given'] or 'Not answered'}",
                    f"Correct answer: {q['answer']}",
                    f"Explanation: {q.get('explanation', '')}",
                    "",
                ])

            st.download_button(
                "⬇ Download quiz review",
                data="\n".join(lines),
                file_name=f"{safe_filename(quiz_topic)}_quiz_review.txt",
                mime="text/plain",
                use_container_width=True,
            )
            if st.button("Create another quiz", type="primary", use_container_width=True):
                st.session_state["quiz"] = None
                st.session_state["quiz_meta"] = {}
                st.session_state["quiz_results"] = None
                st.rerun()


# =========================================================
# SOURCE EXPLORER
# =========================================================
elif section == "Source Explorer":
    st.markdown("## Source Explorer")
    st.markdown('<p class="muted">Search passages extracted from your PDF and inspect their page references.</p>', unsafe_allow_html=True)

    query = st.text_input("Search your document", placeholder="Search a concept, equation, or keyword...")
    if query.strip():
        matches = search_chunks(query, chunks, top_k=min(20, max(len(chunks), 1)))
    else:
        matches = chunks[:20]

    st.caption(f"Showing {len(matches)} passage(s)")
    if not matches:
        st.info("No matching passages found. Try another keyword.")
    else:
        render_sources(matches)

    st.divider()
    st.markdown("### Export extracted notes")
    st.download_button(
        "⬇ Download all source passages",
        data=source_text(chunks),
        file_name=f"{safe_filename((st.session_state['document_name'] or 'course').rsplit('.', 1)[0])}_notes.txt",
        mime="text/plain",
        use_container_width=True,
    )


# =========================================================
# MY PROGRESS
# =========================================================
elif section == "My Progress":
    st.markdown("## My Progress")
    st.markdown('<p class="muted">Your topic mastery estimates and revision priorities.</p>', unsafe_allow_html=True)

    mastery = get_mastery() or []
    if not mastery:
        st.markdown(
            """
            <div class="panel">
              <div class="panel-title">Your learning analytics will appear here</div>
              <p class="muted">Complete a topic quiz to begin tracking your mastery estimates.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        avg = sum(float(x.get("mastery", 0)) for x in mastery) / len(mastery)
        weakest = min(mastery, key=lambda x: float(x.get("mastery", 0)))
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Topics tracked", len(mastery), "Topics in your profile")
        with c2:
            metric_card("Average mastery", f"{avg:.0%}", "Simple average estimate")
        with c3:
            metric_card("Quiz attempts", sum(int(x.get("attempts", 0)) for x in mastery), "Recorded attempts")

        st.write("")
        st.markdown("### Topic mastery")
        for item in sorted(mastery, key=lambda x: float(x.get("mastery", 0))):
            name = str(item.get("topic", "Untitled topic"))
            value = max(0.0, min(1.0, float(item.get("mastery", 0))))
            attempts = int(item.get("attempts", 0))
            with st.container(border=True):
                left, right = st.columns([4, 1])
                with left:
                    st.markdown(f"**{name.title()}**")
                with right:
                    st.markdown(f"**{value:.0%}**")
                st.progress(value)
                st.caption(f"{attempts} recorded attempt(s)")

        st.divider()
        st.markdown("### Recommended revision")
        st.info(
            f"Prioritize **{str(weakest.get('topic', 'this topic')).title()}**. "
            "It has the lowest estimated mastery in your current profile."
        )
        if st.button("Practice weakest topic", type="primary", use_container_width=True):
            st.session_state["revision_topic"] = weakest.get("topic", "")
            st.info(
                f"Choose Topic Quiz in the sidebar and enter **{weakest.get('topic', '')}** "
                "as the topic to practice."
            )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    '<div class="footer">Mi(a) AI · Your course material, organized for learning · Prototype edition</div>',
    unsafe_allow_html=True,
)
