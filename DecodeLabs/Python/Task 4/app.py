"""
The General Knowledge Quiz - Ultimate Streamlit Web Application
Features modern UI/UX, animations, audio cues, lifelines, custom modes, and rich review analytics.
"""
import streamlit as st
import random
from questions import QUESTIONS, get_categories, filter_questions
from ui_components import inject_custom_css, play_audio_effect

# Page Configuration
st.set_page_config(
    page_title="General Knowledge Quiz - Ultimate Trivia",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Apply CSS Styling
inject_custom_css()

# Session State Initialization
def init_session_state():
    if "game_state" not in st.session_state:
        st.session_state.game_state = "setup" # "setup", "playing", "completed"
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = []
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = None
    if "answered" not in st.session_state:
        st.session_state.answered = False
    if "is_correct" not in st.session_state:
        st.session_state.is_correct = False
    if "lifeline_5050_used" not in st.session_state:
        st.session_state.lifeline_5050_used = False
    if "lifeline_hint_used" not in st.session_state:
        st.session_state.lifeline_hint_used = False
    if "show_hint" not in st.session_state:
        st.session_state.show_hint = False
    if "disabled_options" not in st.session_state:
        st.session_state.disabled_options = []
    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = []
    if "audio_trigger" not in st.session_state:
        st.session_state.audio_trigger = None

init_session_state()

# Sound Effect Trigger Execution
if st.session_state.audio_trigger:
    play_audio_effect(st.session_state.audio_trigger)
    st.session_state.audio_trigger = None

# Sidebar Controls & History
with st.sidebar:
    st.markdown("### 🏆 Session History")
    if st.session_state.quiz_history:
        for idx, record in enumerate(reversed(st.session_state.quiz_history[-5:]), 1):
            st.markdown(f"**Play #{len(st.session_state.quiz_history)-idx+1}**: {record['score']}/{record['total']} ({record['percentage']}%) - *{record['category']}*")
    else:
        st.caption("No quizzes played yet. Take your first challenge!")
        
    st.divider()
    st.markdown("### 🎮 Rules & Features")
    st.caption("- +1 Point for every correct answer.\n- 50:50 Lifeline removes 2 incorrect choices.\n- Hint Lifeline reveals a subtle clue.\n- Instant explanations provided!")

# App Title & Header
st.markdown('<div class="quiz-title">✨ GENERAL KNOWLEDGE QUIZ</div>', unsafe_allow_html=True)
st.markdown('<div class="quiz-subtitle">Test your general culture knowledge with instant feedback & fun trivia!</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# SCREEN 1: SETUP & WELCOME SCREEN (FRONT PAGE CONTROLS)
# ----------------------------------------------------
if st.session_state.game_state == "setup":
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding-bottom: 1.5rem;">
        <h2 style="color: #38bdf8; margin-bottom: 0.5rem;">Ready to Challenge Yourself?</h2>
        <p style="color: #cbd5e1; font-size: 1.05rem; margin-bottom: 0;">
            Customize your game session below and press <b>START QUIZ NOW</b>!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Front Page Prominent Quiz Controls Card
    st.markdown("""
    <div class="controls-card">
        <h3 style="color: #c084fc; margin-top: 0; margin-bottom: 1rem; font-size: 1.3rem; display: flex; align-items: center; gap: 8px;">
            ⚙️ Configure Your Quiz
        </h3>
    """, unsafe_allow_html=True)

    c_col1, c_col2 = st.columns([1, 1])

    with c_col1:
        # PROMINENT MAIN PAGE SLIDER FOR NUMBER OF QUESTIONS
        quiz_length = st.select_slider(
            "📊 Select Number of Questions:",
            options=[3, 5, 10, 15],
            value=3,
            help="Choose how many questions to play in this round. Quick mode is 3 Qs!"
        )

    with c_col2:
        # PROMINENT MAIN PAGE CATEGORY SELECTOR
        selected_cat = st.selectbox(
            "🏷️ Select Category Domain:",
            options=get_categories(),
            index=0,
            help="Filter questions by domain or select All Categories."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Stat Badges
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-value">{quiz_length} Qs</div>
            <div class="stat-label">Session Length</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-value">{len(QUESTIONS)}+</div>
            <div class="stat-label">Question Bank</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-value">100%</div>
            <div class="stat-label">Randomized</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    st.write("")
    
    start_btn = st.button("🚀 START QUIZ NOW", use_container_width=True)
    if start_btn:
        # Load questions
        st.session_state.questions = filter_questions(category=selected_cat, count=quiz_length)
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.user_answers = []
        st.session_state.answered = False
        st.session_state.selected_option = None
        st.session_state.lifeline_5050_used = False
        st.session_state.lifeline_hint_used = False
        st.session_state.show_hint = False
        st.session_state.disabled_options = []
        st.session_state.game_state = "playing"
        st.rerun()

# ----------------------------------------------------
# SCREEN 2: ACTIVE QUIZ QUESTION SCREEN
# ----------------------------------------------------
elif st.session_state.game_state == "playing":
    total_q = len(st.session_state.questions)
    curr_q = st.session_state.questions[st.session_state.current_index]
    
    # Progress Bar & Live Stats Header
    progress_val = (st.session_state.current_index + (1 if st.session_state.answered else 0)) / total_q
    st.progress(progress_val)
    
    col_stat1, col_stat2, col_stat3 = st.columns([2, 2, 2])
    with col_stat1:
        st.markdown(f"**Question**: <span style='color: #38bdf8; font-weight: 700;'>{st.session_state.current_index + 1} / {total_q}</span>", unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f"**Score**: <span style='color: #4ade80; font-weight: 700;'>{st.session_state.score} pts</span>", unsafe_allow_html=True)
    with col_stat3:
        st.markdown(f"<div style='text-align: right;'><span class='category-badge'>{curr_q['category']}</span></div>", unsafe_allow_html=True)
        
    st.write("")
    
    # Question Container Card
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: #ffffff; font-size: 1.35rem; line-height: 1.4; margin-top: 0;">
            {curr_q['question']}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Lifelines Section
    lifeline_col1, lifeline_col2, lifeline_col3 = st.columns([2, 2, 3])
    with lifeline_col1:
        btn_5050 = st.button("🪄 50:50 Lifeline", disabled=st.session_state.lifeline_5050_used or st.session_state.answered, use_container_width=True)
        if btn_5050 and not st.session_state.lifeline_5050_used:
            st.session_state.lifeline_5050_used = True
            wrong_opts = [opt for opt in curr_q["options"] if opt != curr_q["answer"]]
            st.session_state.disabled_options = random.sample(wrong_opts, 2)
            st.rerun()
            
    with lifeline_col2:
        btn_hint = st.button("💡 Get Hint", disabled=st.session_state.lifeline_hint_used or st.session_state.answered, use_container_width=True)
        if btn_hint and not st.session_state.lifeline_hint_used:
            st.session_state.lifeline_hint_used = True
            st.session_state.show_hint = True
            st.rerun()
            
    if st.session_state.show_hint:
        st.info(f"🔑 **Hint**: {curr_q['hint']}")
        
    # Prepare Option Choices (Filter out 50:50 eliminated options)
    available_options = [opt for opt in curr_q["options"] if opt not in st.session_state.disabled_options]
    
    # Radio Selection
    user_choice = st.radio(
        "Select your answer:",
        options=available_options,
        index=None if st.session_state.selected_option is None else (available_options.index(st.session_state.selected_option) if st.session_state.selected_option in available_options else None),
        key=f"radio_q_{st.session_state.current_index}",
        disabled=st.session_state.answered
    )
    
    st.write("")
    
    # Submit / Next Navigation Buttons
    if not st.session_state.answered:
        submit_btn = st.button("CHECK ANSWER ✔️", use_container_width=True, disabled=(user_choice is None))
        if submit_btn and user_choice:
            st.session_state.answered = True
            st.session_state.selected_option = user_choice
            st.session_state.is_correct = (user_choice == curr_q["answer"])
            
            if st.session_state.is_correct:
                st.session_state.score += 1
                st.session_state.audio_trigger = "correct"
            else:
                st.session_state.audio_trigger = "wrong"
                
            # Record result
            st.session_state.user_answers.append({
                "question": curr_q["question"],
                "category": curr_q["category"],
                "selected": user_choice,
                "answer": curr_q["answer"],
                "is_correct": st.session_state.is_correct,
                "explanation": curr_q["explanation"]
            })
            st.rerun()
    else:
        # Show Feedback Box
        if st.session_state.is_correct:
            st.markdown(f"""
            <div class="correct-box">
                🎉 <b>Correct!</b> Excellent job.
                <div style="font-weight: 400; margin-top: 0.4rem; color: #cbd5e1;">{curr_q['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="wrong-box">
                ❌ <b>Incorrect!</b> The correct answer was: <b>{curr_q['answer']}</b>
                <div style="font-weight: 400; margin-top: 0.4rem; color: #cbd5e1;">{curr_q['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        next_text = "NEXT QUESTION ➡️" if (st.session_state.current_index + 1 < total_q) else "VIEW FINAL SCORE 🏆"
        next_btn = st.button(next_text, use_container_width=True)
        
        if next_btn:
            if st.session_state.current_index + 1 < total_q:
                st.session_state.current_index += 1
                st.session_state.answered = False
                st.session_state.selected_option = None
                st.session_state.show_hint = False
                st.session_state.disabled_options = []
                st.rerun()
            else:
                st.session_state.game_state = "completed"
                # Record to score history
                st.session_state.quiz_history.append({
                    "score": st.session_state.score,
                    "total": total_q,
                    "percentage": int((st.session_state.score / total_q) * 100),
                    "category": curr_q["category"]
                })
                if st.session_state.score / total_q >= 0.6:
                    st.session_state.audio_trigger = "win"
                st.rerun()

# ----------------------------------------------------
# SCREEN 3: QUIZ COMPLETE & SCORE BREAKDOWN SCREEN
# ----------------------------------------------------
elif st.session_state.game_state == "completed":
    total_q = len(st.session_state.questions)
    percentage = int((st.session_state.score / total_q) * 100)
    
    # Celebrate if high score!
    if percentage >= 66:
        st.balloons()
        
    # Result Title based on score
    if percentage == 100:
        badge_title = "👑 GRANDMASTER TRIVIA MASTER!"
        subtext = "Flawless score! You know your general knowledge inside out."
    elif percentage >= 66:
        badge_title = "🌟 KNOWLEDGE EXPLORER!"
        subtext = "Great job! You have a solid grasp of general culture."
    else:
        badge_title = "🎓 KNOWLEDGE SEEKER!"
        subtext = "Good effort! Keep practicing to boost your general culture score."

    st.markdown(f"""
    <div class="result-banner">
        <h3 style="color: #c084fc; margin-top: 0;">{badge_title}</h3>
        <p style="color: #94a3b8;">{subtext}</p>
        <div class="score-number">{st.session_state.score} / {total_q}</div>
        <p style="color: #38bdf8; font-size: 1.3rem; font-weight: 700;">Score Accuracy: {percentage}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.markdown("### 📝 Detailed Answer Review")
    
    for idx, ans in enumerate(st.session_state.user_answers, 1):
        status_icon = "✅" if ans["is_correct"] else "❌"
        border_color = "rgba(34, 197, 94, 0.4)" if ans["is_correct"] else "rgba(239, 68, 68, 0.4)"
        
        st.markdown(f"""
        <div class="glass-card" style="border-color: {border_color}; padding: 1.2rem 1.5rem;">
            <div style="font-weight: 700; color: #f8fafc;">
                {status_icon} Question {idx}: {ans['question']}
            </div>
            <div style="font-size: 0.95rem; margin-top: 0.5rem; color: #cbd5e1;">
                Your Answer: <b style="color: {'#4ade80' if ans['is_correct'] else '#f87171'};">{ans['selected']}</b> | 
                Correct Answer: <b style="color: #4ade80;">{ans['answer']}</b>
            </div>
            <div style="font-size: 0.88rem; margin-top: 0.4rem; color: #94a3b8; font-style: italic;">
                💡 {ans['explanation']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    play_again_btn = st.button("🔄 PLAY AGAIN (NEW QUESTIONS)", use_container_width=True)
    if play_again_btn:
        st.session_state.game_state = "setup"
        st.rerun()
