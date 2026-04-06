"""
F=ma Exam Prep — Main Streamlit App
Run: streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Exam Prep Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── API Key Gate ──────────────────────────────────────────────────────────────
def api_key_gate():
    if st.session_state.get("authenticated"):
        os.environ["ANTHROPIC_API_KEY"] = st.session_state.api_key
        return

    env_key = os.getenv("ANTHROPIC_API_KEY", "")
    if env_key.startswith("sk-ant-"):
        st.session_state.api_key = env_key
        st.session_state.authenticated = True
        return

    st.title("⚡ Exam Prep Agent")
    st.markdown("Enter your [Anthropic API key](https://console.anthropic.com) to get started.")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    if st.button("Start", type="primary"):
        if api_key.startswith("sk-ant-"):
            os.environ["ANTHROPIC_API_KEY"] = api_key
            st.session_state.api_key = api_key
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid API key — should start with sk-ant-")
    st.stop()

api_key_gate()

import streamlit as st
from modules.exam_loader import load_exam, list_exams, get_exam_context, get_topic_names, get_subtopics, get_formulas
from modules.tutor import explain_concept, get_hint, check_answer
from modules.problem_gen import generate_problem
from modules.session import init_session
from dotenv import load_dotenv
load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Exam Prep Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Init session ──────────────────────────────────────────────────────────────
init_session(st.session_state)

# ── Sidebar: Exam + Topic Selection ──────────────────────────────────────────
with st.sidebar:
    st.title("⚡ Exam Prep")

    # Exam selector
    available_exams = list_exams()
    selected_exam_name = st.selectbox("Select Exam", list(available_exams.keys()))
    exam = load_exam(available_exams[selected_exam_name])
    exam_context = get_exam_context(exam)
    st.session_state.session.exam_name = exam["name"]

    st.divider()

    # Topic selector
    topics = get_topic_names(exam)
    selected_topic = st.selectbox("Topic", topics)
    subtopics = get_subtopics(exam, selected_topic)
    selected_subtopic = st.selectbox("Subtopic (optional)", ["— any —"] + subtopics)

    formulas = get_formulas(exam, selected_topic)
    if formulas:
        with st.expander("📐 Key Formulas"):
            for f in formulas:
                st.code(f)

    st.divider()

    # Difficulty
    difficulty = st.select_slider("Difficulty", ["easy", "medium", "hard"], value="medium")

    st.divider()

    # Score display
    s = st.session_state.session
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", s.score)
    col2.metric("Streak", f"{s.streak} 🔥" if s.streak >= 3 else s.streak)
    col3.metric("Accuracy", f"{s.accuracy:.0f}%" if s.total_attempted else "—")

    if s.weak_topics():
        st.warning(f"💡 Needs work: {', '.join(s.weak_topics())}")

# ── Main tabs ─────────────────────────────────────────────────────────────────
tab_tutor, tab_practice, tab_about = st.tabs(["🧠 Tutor", "🎯 Practice", "📋 About Exam"])

# ── TAB 1: Tutor ──────────────────────────────────────────────────────────────
with tab_tutor:
    st.header(f"Ask anything about {selected_topic}")

    # Quick-start buttons
    st.caption("Quick starts:")
    cols = st.columns(3)
    quick_prompts = [
        f"Explain {selected_topic} from scratch",
        f"What are the trickiest {selected_topic} problems on {exam['short_name']}?",
        f"Give me an intuitive way to remember {selected_topic}",
    ]
    for i, (col, prompt) in enumerate(zip(cols, quick_prompts)):
        if col.button(prompt, key=f"quick_{i}"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Chat display
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if user_input := st.chat_input(f"Ask about {selected_topic}..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            stream = explain_concept(
                exam["name"], exam_context, selected_topic, user_input, stream=True
            )
            for chunk in stream:
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

    if st.session_state.chat_history:
        if st.button("Clear chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

# ── TAB 2: Practice ───────────────────────────────────────────────────────────
with tab_practice:
    st.header("Practice Problems")

    col_gen, col_spacer = st.columns([1, 3])
    subtopic_for_gen = "" if selected_subtopic == "— any —" else selected_subtopic

    if col_gen.button("⚡ New Problem", type="primary", use_container_width=True):
        with st.spinner("Generating problem..."):
            try:
                problem = generate_problem(exam["name"], selected_topic, subtopic_for_gen, difficulty)
                st.session_state.current_problem = problem
                st.session_state.answered = False
                st.session_state.selected_answer = None
                st.session_state.feedback = None
            except Exception as e:
                st.error(f"Problem generation failed: {e}")

    problem = st.session_state.get("current_problem")

    if problem:
        # Problem card
        diff_color = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(problem["difficulty"], "⚪")
        st.markdown(f"**{diff_color} {problem['difficulty'].upper()} · {selected_topic}**")

        with st.container(border=True):
            st.markdown(f"### {problem['question']}")

            # Answer choices
            answer = st.radio(
                "Select your answer:",
                options=list(problem["choices"].keys()),
                format_func=lambda k: f"**{k})** {problem['choices'][k]}",
                key="answer_radio",
                disabled=st.session_state.answered,
                index=None,
            )

            col_submit, col_hint = st.columns([1, 1])

            # Hint
            if col_hint.button("💡 Hint", disabled=st.session_state.answered):
                with st.spinner("Getting hint..."):
                    hint_stream = get_hint(problem["question"], problem["choices"], stream=True)
                    hint_text = ""
                    hint_placeholder = st.empty()
                    for chunk in hint_stream:
                        hint_text += chunk
                        hint_placeholder.info(hint_text + "▌")
                    hint_placeholder.info(hint_text)

            # Submit
            if col_submit.button("✅ Submit", type="primary", disabled=st.session_state.answered or not answer):
                st.session_state.answered = True
                is_correct = answer.upper() == problem["correct"].upper()
                st.session_state.session.record_attempt(selected_topic, problem["difficulty"], is_correct)

                with st.spinner("Checking answer..."):
                    feedback_stream = check_answer(
                        problem["question"], answer, problem["correct"], problem["solution"], stream=True
                    )
                    feedback_text = ""
                    feedback_placeholder = st.empty()
                    for chunk in feedback_stream:
                        feedback_text += chunk
                        feedback_placeholder.markdown(feedback_text + "▌")
                    feedback_placeholder.markdown(feedback_text)

                if is_correct:
                    points = {"easy": 1, "medium": 2, "hard": 3}.get(problem["difficulty"], 1)
                    st.success(f"✅ Correct! +{points} points")
                    #st.success(f"✅ Correct! +{{'easy':1,'medium':2,'hard':3}.get(problem['difficulty'],1)} points")
                    st.balloons()
                else:
                    st.error(f"❌ Correct answer was **{problem['correct']}**: {problem['choices'][problem['correct']]}")

                # Show full solution
                with st.expander("📖 Full Solution"):
                    st.markdown(problem["solution"])
                    st.caption(f"💡 Concept tested: *{problem['concept']}*")

                st.rerun()

# ── TAB 3: About Exam ─────────────────────────────────────────────────────────
with tab_about:
    st.header(exam["name"])
    st.markdown(exam["description"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Questions", exam["num_questions"])
    col2.metric("Duration", f"{exam['duration_minutes']} min")
    col3.metric("Type", "MCQ")

    st.subheader("Topics & Weights")
    for topic in exam["topics"]:
        weight_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(topic["weight"], "⚪")
        with st.expander(f"{weight_emoji} {topic['name']} ({topic['weight']} weight)"):
            st.write("**Subtopics:**", ", ".join(topic["subtopics"]))
            if topic.get("key_formulas"):
                st.write("**Key Formulas:**")
                for f in topic["key_formulas"]:
                    st.code(f)

    st.subheader("💡 Exam Tips")
    for tip in exam["tips"]:
        st.markdown(f"- {tip}")

    st.link_button("🔗 Past Papers", exam["past_papers_url"])
