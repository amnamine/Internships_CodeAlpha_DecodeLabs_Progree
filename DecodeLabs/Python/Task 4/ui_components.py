"""
UI Styling, CSS Injections, Animations, and Visual Components for Streamlit Quiz App
"""
import streamlit as st

def inject_custom_css():
    """Injects high-end, responsive custom CSS for glassmorphism, animations, borders, fonts, and colors."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&display=swap');

    /* Global Typography & Background setup */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #311042 70%, #0f172a 100%);
        background-attachment: fixed;
        color: #f8fafc;
    }

    /* Animated Custom Header Title */
    .quiz-title {
        font-size: 3.2rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc, #f472b6);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease infinite;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .quiz-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Glassmorphism Card Container */
    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 2.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.25);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .glass-card:hover {
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.35);
    }

    /* Controls Panel Box */
    .controls-card {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.6), rgba(49, 16, 66, 0.6));
        border: 1.5px solid rgba(168, 85, 247, 0.3);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    /* Question Pill / Category Badge */
    .category-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.3));
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 9999px;
        color: #e0e7ff;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    /* Live Stat Metric Badges */
    .stat-badge {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stat-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #38bdf8;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Slider Custom Styling */
    div[data-testid="stSlider"] label {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #e0e7ff !important;
    }
    
    div[data-baseweb="slider"] {
        padding-top: 10px !important;
    }

    /* Selectbox Custom Styling */
    div[data-testid="stSelectbox"] label {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #e0e7ff !important;
    }

    div[data-baseweb="select"] > div {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1.5px solid rgba(168, 85, 247, 0.4) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
    }

    /* Custom Streamlit Radio Buttons / Choice Options Styling */
    div[data-testid="stRadio"] > label {
        display: none;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 12px;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: rgba(30, 41, 59, 0.75) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        padding: 14px 22px !important;
        color: #f1f5f9 !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        width: 100% !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: rgba(99, 102, 241, 0.25) !important;
        border-color: #818cf8 !important;
        transform: translateX(4px) !important;
    }

    /* Selected state for radio option */
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.45), rgba(168, 85, 247, 0.45)) !important;
        border-color: #c084fc !important;
        box-shadow: 0 0 18px rgba(168, 85, 247, 0.4) !important;
    }

    /* Custom Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.5px !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 30px rgba(168, 85, 247, 0.65) !important;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* Progress bar custom styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        border-radius: 10px;
    }

    /* Score Result Banner */
    .result-banner {
        text-align: center;
        padding: 2.5rem 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(168, 85, 247, 0.4);
        border-radius: 24px;
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.2);
    }
    
    .score-number {
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #4ade80, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin: 1rem 0;
    }

    /* Feedback Alerts */
    .correct-box {
        background: rgba(34, 197, 94, 0.15);
        border: 1.5px solid #22c55e;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        color: #4ade80;
        font-weight: 600;
        margin-top: 1rem;
        animation: fadeIn 0.3s ease-in;
    }

    .wrong-box {
        background: rgba(239, 68, 68, 0.15);
        border: 1.5px solid #ef4444;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        color: #f87171;
        font-weight: 600;
        margin-top: 1rem;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def play_audio_effect(effect_type="correct"):
    """Injects a subtle HTML5 Web Audio API synthesizer sound effect."""
    sound_js = f"""
    <script>
    (function() {{
        try {{
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            const ctx = new AudioContext();
            
            if ('{effect_type}' === 'correct') {{
                const playTone = (freq, start, dur) => {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.value = freq;
                    gain.gain.setValueAtTime(0.15, ctx.currentTime + start);
                    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + start + dur);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(ctx.currentTime + start);
                    osc.stop(ctx.currentTime + start + dur);
                }};
                playTone(523.25, 0, 0.12);
                playTone(659.25, 0.12, 0.25);
            }} else if ('{effect_type}' === 'wrong') {{
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(150, ctx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 0.3);
                gain.gain.setValueAtTime(0.2, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.3);
            }} else {{
                const notes = [523.25, 659.25, 783.99, 1046.50];
                notes.forEach((n, idx) => {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.frequency.value = n;
                    gain.gain.setValueAtTime(0.1, ctx.currentTime + idx*0.08);
                    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + idx*0.08 + 0.4);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(ctx.currentTime + idx*0.08);
                    osc.stop(ctx.currentTime + idx*0.08 + 0.4);
                }});
            }}
        }} catch (e) {{}}
    }})();
    </script>
    """
    st.components.v1.html(sound_js, height=0, width=0)
