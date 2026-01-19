"""
Review Flashcards - With Dark Mode & Swipe Gestures
"""

import streamlit as st
import streamlit.components.v1 as components
import os
from database import (
    init_database, 
    get_all_cardsets, 
    get_flashcards_by_set,
    get_cardset_by_id,
    update_review_stats,
    init_spaced_repetition_table,
    update_card_progress,
    get_next_intervals,
    get_explanation,
    save_explanation,
    get_mnemonic,
    save_mnemonic,
)
from flashcard_generator import generate_eli_explanation, generate_mnemonic
from utils import get_complexity_emoji

# Auth check
def check_auth():
    correct_password = os.getenv("APP_PASSWORD", "")
    if not correct_password:
        try:
            correct_password = st.secrets.get("APP_PASSWORD", "")
        except:
            correct_password = ""
    if correct_password and not st.session_state.get("password_correct", False):
        st.switch_page("app.py")
        return False
    if not st.session_state.get("user_api_key"):
        st.switch_page("app.py")
        return False
    return True

if not check_auth():
    st.stop()

init_database()
init_spaced_repetition_table()

# Page config
st.set_page_config(
    page_title="Review | Smart FlashCards",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize dark mode in session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

dark = st.session_state.dark_mode

# Dynamic CSS based on theme
def get_theme_css():
    if dark:
        return """
        <style>
            /* Dark mode base */
            .stApp {
                background-color: #0d1117 !important;
            }
            
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            [data-testid="stSidebarNav"] li:first-child {display: none;}
            
            .block-container {
                padding-top: 1rem;
                max-width: 700px;
            }
            
            /* Dark sidebar */
            [data-testid="stSidebar"] {
                background-color: #161b22 !important;
            }
            [data-testid="stSidebar"] * {
                color: #c9d1d9 !important;
            }
            
            /* Progress bar dark */
            .progress-bar {
                height: 4px;
                background: #30363d;
                border-radius: 2px;
                margin-bottom: 8px;
            }
            .progress-fill {
                height: 100%;
                background: #10a37f;
                border-radius: 2px;
                transition: width 0.3s;
                box-shadow: 0 0 10px #10a37f;
            }
            .progress-text {
                text-align: center;
                font-size: 0.85rem;
                color: #8b949e;
                margin-bottom: 1.5rem;
            }
            
            /* Question card - dark with glow */
            .q-card {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: white;
                border-radius: 20px;
                padding: 40px 32px;
                min-height: 240px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                border: 1px solid #30363d;
                box-shadow: 0 0 30px rgba(88, 166, 255, 0.15);
            }
            
            /* Answer card - dark with green glow */
            .a-card {
                background: linear-gradient(135deg, #0d1f22 0%, #1a3a2a 100%);
                color: white;
                border-radius: 20px;
                padding: 40px 32px;
                min-height: 240px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                border: 1px solid #238636;
                box-shadow: 0 0 30px rgba(16, 163, 127, 0.3);
            }
            
            .card-label {
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                opacity: 0.7;
                margin-bottom: 16px;
            }
            .card-content {
                font-size: 1.15rem;
                line-height: 1.7;
            }
            
            /* ELI5 card dark */
            .eli5-card {
                background: linear-gradient(135deg, #3d1a45 0%, #4a1942 100%);
                color: white;
                border-radius: 16px;
                padding: 24px;
                margin-top: 12px;
                text-align: center;
                border: 1px solid #f093fb55;
                box-shadow: 0 0 20px rgba(240, 147, 251, 0.2);
            }
            
            /* Mnemonic card dark */
            .mnem-card {
                background: linear-gradient(135deg, #1e1a45 0%, #2d1f5e 100%);
                color: white;
                border-radius: 16px;
                padding: 24px;
                margin-top: 12px;
                text-align: left;
                border: 1px solid #667eea55;
                box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
            }
            .mnem-card .card-content {
                font-size: 0.95rem;
                text-align: left;
            }
            
            /* Rating labels dark */
            .rating-label {
                font-size: 0.75rem;
                color: #8b949e;
                text-align: center;
            }
            
            /* Buttons dark */
            .stButton > button {
                border-radius: 12px;
                background-color: #21262d !important;
                border: 1px solid #30363d !important;
                color: #c9d1d9 !important;
            }
            .stButton > button:hover {
                background-color: #30363d !important;
                border-color: #8b949e !important;
            }
            .stButton > button[kind="primary"] {
                background: #238636 !important;
                border: none !important;
                box-shadow: 0 0 15px rgba(35, 134, 54, 0.4);
            }
            .stButton > button[kind="primary"]:hover {
                background: #2ea043 !important;
            }
            
            /* Swipe hint dark */
            .swipe-hint {
                text-align: center;
                color: #8b949e;
                font-size: 0.8rem;
                margin: 10px 0;
                padding: 8px;
                background: #161b22;
                border-radius: 8px;
            }
            
            /* General text */
            p, span, div, h1, h2, h3, h4 {
                color: #c9d1d9 !important;
            }
        </style>
        """
    else:
        return """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            [data-testid="stSidebarNav"] li:first-child {display: none;}
            
            .block-container {
                padding-top: 1rem;
                max-width: 700px;
            }
            
            /* Progress bar */
            .progress-bar {
                height: 4px;
                background: #e0e0e0;
                border-radius: 2px;
                margin-bottom: 8px;
            }
            .progress-fill {
                height: 100%;
                background: #10a37f;
                border-radius: 2px;
                transition: width 0.3s;
            }
            .progress-text {
                text-align: center;
                font-size: 0.85rem;
                color: #888;
                margin-bottom: 1.5rem;
            }
            
            /* Question card */
            .q-card {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: white;
                border-radius: 20px;
                padding: 40px 32px;
                min-height: 240px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
            }
            
            /* Answer card */
            .a-card {
                background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
                color: white;
                border-radius: 20px;
                padding: 40px 32px;
                min-height: 240px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
            }
            
            .card-label {
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                opacity: 0.7;
                margin-bottom: 16px;
            }
            .card-content {
                font-size: 1.15rem;
                line-height: 1.7;
            }
            
            /* ELI5 card */
            .eli5-card {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border-radius: 16px;
                padding: 24px;
                margin-top: 12px;
                text-align: center;
            }
            
            /* Mnemonic card */
            .mnem-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 16px;
                padding: 24px;
                margin-top: 12px;
                text-align: left;
            }
            .mnem-card .card-content {
                font-size: 0.95rem;
                text-align: left;
            }
            
            /* Rating labels */
            .rating-label {
                font-size: 0.75rem;
                color: #888;
                text-align: center;
            }
            
            /* Buttons */
            .stButton > button {
                border-radius: 12px;
            }
            .stButton > button[kind="primary"] {
                background: #10a37f;
                border: none;
            }
            
            /* Swipe hint */
            .swipe-hint {
                text-align: center;
                color: #888;
                font-size: 0.8rem;
                margin: 10px 0;
                padding: 8px;
                background: #f5f5f5;
                border-radius: 8px;
            }
        </style>
        """

st.markdown(get_theme_css(), unsafe_allow_html=True)

# Swipe gesture JavaScript (touch, mouse, keyboard) - using components.html for JS execution
components.html("""
<script>
(function() {
    // Wait for page to fully load
    if (window.swipeInitialized) return;
    window.swipeInitialized = true;
    
    let startX = 0;
    let isDragging = false;
    const minSwipeDistance = 50;
    
    // Get parent document (Streamlit's iframe parent)
    const doc = window.parent.document;
    
    // Touch events (mobile)
    doc.addEventListener('touchstart', e => {
        startX = e.changedTouches[0].screenX;
    }, {passive: true});
    
    doc.addEventListener('touchend', e => {
        const endX = e.changedTouches[0].screenX;
        handleSwipe(endX - startX);
    }, {passive: true});
    
    // Mouse events (desktop drag)
    doc.addEventListener('mousedown', e => {
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'INPUT') return;
        startX = e.screenX;
        isDragging = true;
    });
    
    doc.addEventListener('mouseup', e => {
        if (isDragging) {
            const endX = e.screenX;
            handleSwipe(endX - startX);
            isDragging = false;
        }
    });
    
    // Keyboard events
    doc.addEventListener('keydown', e => {
        // Prevent if typing in input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        switch(e.key) {
            case ' ':  // Space = Show answer / Flip
            case 'Enter':
                e.preventDefault();
                const showBtn = Array.from(doc.querySelectorAll('button')).find(b => 
                    b.textContent.includes('Show Answer') || b.textContent.includes('Flip'));
                if (showBtn) showBtn.click();
                break;
            case '1':  // 1 = Again
                clickButton('Again');
                break;
            case '2':  // 2 = Hard
                clickButton('Hard');
                break;
            case '3':  // 3 = Good
                clickButton('Good');
                break;
            case '4':  // 4 = Easy
                clickButton('Easy');
                break;
            case 'ArrowLeft':  // Left arrow = Again
                clickButton('Again');
                break;
            case 'ArrowRight':  // Right arrow = Good
                clickButton('Good');
                break;
            case 'ArrowUp':  // Up arrow = Easy
                clickButton('Easy');
                break;
            case 'ArrowDown':  // Down arrow = Hard
                clickButton('Hard');
                break;
        }
    });
    
    function clickButton(text) {
        const btn = Array.from(doc.querySelectorAll('button')).find(b => b.textContent.includes(text));
        if (btn) btn.click();
    }
    
    function handleSwipe(distance) {
        if (Math.abs(distance) < minSwipeDistance) return;
        
        if (distance > 0) {
            // Swipe right - Good
            clickButton('Good');
        } else {
            // Swipe left - Again
            clickButton('Again');
        }
    }
    
    console.log('Smart FlashCards: Gestures initialized');
})();
</script>
""", height=0)

# Initialize session state
if 'current_card_index' not in st.session_state:
    st.session_state.current_card_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'selected_cardset' not in st.session_state:
    st.session_state.selected_cardset = None
if 'session_stats' not in st.session_state:
    st.session_state.session_stats = {'again': 0, 'hard': 0, 'good': 0, 'easy': 0}
if 'show_eli5' not in st.session_state:
    st.session_state.show_eli5 = False
if 'show_mnemonic' not in st.session_state:
    st.session_state.show_mnemonic = False

# Get all cardsets
cardsets = get_all_cardsets()

if not cardsets:
    st.markdown("### 📖 Review")
    st.info("No decks found. Create your first deck to start studying!")
    if st.button("✨ Create Deck", type="primary"):
        st.switch_page("pages/1_Generate.py")
    st.stop()

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🎨 Theme")
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="dark_toggle")
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Navigation")
    if st.button("✨ Generate", use_container_width=True):
        st.switch_page("pages/1_Generate.py")
    if st.button("📚 My Decks", use_container_width=True):
        st.switch_page("pages/2_Decks.py")
    
    st.markdown("---")
    st.markdown("### 📚 Select Deck")
    
    cardset_options = {
        f"{get_complexity_emoji(cs['complexity_level'])} {cs['topic'][:25]}{'...' if len(cs['topic']) > 25 else ''}": cs['cardset_id']
        for cs in cardsets
    }
    
    selected_option = st.selectbox(
        "Deck",
        options=list(cardset_options.keys()),
        index=0,
        label_visibility="collapsed"
    )
    
    selected_cardset_id = cardset_options[selected_option]
    
    if st.session_state.selected_cardset != selected_cardset_id:
        st.session_state.selected_cardset = selected_cardset_id
        st.session_state.current_card_index = 0
        st.session_state.show_answer = False
        st.session_state.session_stats = {'again': 0, 'hard': 0, 'good': 0, 'easy': 0}
    
    st.markdown("---")
    
    # Session stats
    stats = st.session_state.session_stats
    total = sum(stats.values())
    if total > 0:
        st.caption(f"📊 This session: {total} reviewed")
        st.caption(f"🟢 {stats['good']} good • 🔴 {stats['again']} again")

# Get flashcards
flashcards = get_flashcards_by_set(st.session_state.selected_cardset)
cardset_info = get_cardset_by_id(st.session_state.selected_cardset)

if not flashcards:
    st.error("No flashcards found in this deck.")
    st.stop()

total_cards = len(flashcards)
current_index = st.session_state.current_card_index
current_card = flashcards[current_index]

# Progress bar
progress_pct = ((current_index + 1) / total_cards) * 100
st.markdown(f"""
<div class="progress-bar">
    <div class="progress-fill" style="width: {progress_pct}%"></div>
</div>
<div class="progress-text">{current_index + 1} / {total_cards}</div>
""", unsafe_allow_html=True)

# Get intervals for rating buttons
intervals = get_next_intervals(current_card['id'])

# Display flashcard
if not st.session_state.show_answer:
    # Question side
    st.markdown(f"""
    <div class="q-card">
        <div class="card-label">Question</div>
        <div class="card-content">{current_card['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Show Answer", use_container_width=True, type="primary"):
        st.session_state.show_answer = True
        update_review_stats(current_card['id'])
        st.rerun()
else:
    # Answer side
    st.markdown(f"""
    <div class="a-card">
        <div class="card-label">Answer</div>
        <div class="card-content">{current_card['answer']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Controls hint
    st.markdown("""
    <div class="swipe-hint">
        ⌨️ <b>Space</b> flip • <b>1-4</b> or <b>←↓↑→</b> rate • 🖱️ Drag or 📱 Swipe
    </div>
    """, unsafe_allow_html=True)
    
    # ELI5 / Mnemonic buttons
    eli_col, mnem_col = st.columns(2)
    
    with eli_col:
        if st.button("🧒 Explain Simply", use_container_width=True):
            st.session_state.show_eli5 = not st.session_state.show_eli5
            st.session_state.show_mnemonic = False
            st.rerun()
    
    with mnem_col:
        if st.button("🧠 Memory Trick", use_container_width=True):
            st.session_state.show_mnemonic = not st.session_state.show_mnemonic
            st.session_state.show_eli5 = False
            st.rerun()
    
    # Show ELI5
    if st.session_state.show_eli5:
        card_id = current_card['id']
        existing_eli5 = get_explanation(card_id, 'eli5')
        
        if existing_eli5:
            st.markdown(f"""
            <div class="eli5-card">
                <div class="card-label">🧒 Explain Like I'm 5</div>
                <div class="card-content">{existing_eli5}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Creating simple explanation..."):
                result = generate_eli_explanation(
                    current_card['question'], 
                    current_card['answer'], 
                    level=5
                )
                
                if result['success']:
                    save_explanation(card_id, 'eli5', result['explanation'])
                    st.markdown(f"""
                    <div class="eli5-card">
                        <div class="card-label">🧒 Explain Like I'm 5</div>
                        <div class="card-content">{result['explanation']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"💰 ${result['cost_info']['this_call']:.4f}")
                else:
                    st.error(f"Error: {result['error']}")
    
    # Show Mnemonic
    if st.session_state.show_mnemonic:
        card_id = current_card['id']
        existing_mnemonic = get_mnemonic(card_id)
        
        if existing_mnemonic:
            st.markdown(f"""
            <div class="mnem-card">
                <div class="card-label">🧠 Memory Trick</div>
                <div class="card-content">{existing_mnemonic}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Creating memory trick..."):
                result = generate_mnemonic(
                    current_card['question'], 
                    current_card['answer']
                )
                
                if result['success']:
                    save_mnemonic(card_id, result['mnemonic'])
                    st.markdown(f"""
                    <div class="mnem-card">
                        <div class="card-label">🧠 Memory Trick</div>
                        <div class="card-content">{result['mnemonic']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"💰 ${result['cost_info']['this_call']:.4f}")
                else:
                    st.error(f"Error: {result['error']}")
    
    # Rating buttons
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**How well did you remember?**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    def rate_card(rating):
        update_card_progress(current_card['id'], rating)
        st.session_state.session_stats[rating] += 1
        if rating != 'again' and current_index < total_cards - 1:
            st.session_state.current_card_index += 1
        st.session_state.show_answer = False
        st.session_state.show_eli5 = False
        st.session_state.show_mnemonic = False
        st.rerun()
    
    with col1:
        st.markdown(f'<p class="rating-label">{intervals["again"]}</p>', unsafe_allow_html=True)
        if st.button("🔴 Again", use_container_width=True, key="btn_again"):
            rate_card('again')
    
    with col2:
        st.markdown(f'<p class="rating-label">{intervals["hard"]}</p>', unsafe_allow_html=True)
        if st.button("🟠 Hard", use_container_width=True, key="btn_hard"):
            rate_card('hard')
    
    with col3:
        st.markdown(f'<p class="rating-label">{intervals["good"]}</p>', unsafe_allow_html=True)
        if st.button("🟢 Good", use_container_width=True, key="btn_good"):
            rate_card('good')
    
    with col4:
        st.markdown(f'<p class="rating-label">{intervals["easy"]}</p>', unsafe_allow_html=True)
        if st.button("🔵 Easy", use_container_width=True, key="btn_easy"):
            rate_card('easy')

# Navigation
st.markdown("<br>", unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("← Prev", use_container_width=True, disabled=(current_index == 0)):
        st.session_state.current_card_index -= 1
        st.session_state.show_answer = False
        st.session_state.show_eli5 = False
        st.session_state.show_mnemonic = False
        st.rerun()

with nav_col2:
    if st.session_state.show_answer:
        if st.button("Flip", use_container_width=True):
            st.session_state.show_answer = False
            st.session_state.show_eli5 = False
            st.session_state.show_mnemonic = False
            st.rerun()

with nav_col3:
    if st.button("Next →", use_container_width=True, disabled=(current_index == total_cards - 1)):
        st.session_state.current_card_index += 1
        st.session_state.show_answer = False
        st.session_state.show_eli5 = False
        st.session_state.show_mnemonic = False
        st.rerun()

# Completion
if current_index == total_cards - 1 and st.session_state.show_answer:
    st.markdown("---")
    st.success("🎉 Deck completed!")
    
    stats = st.session_state.session_stats
    total_reviewed = sum(stats.values())
    if total_reviewed > 0:
        st.markdown(f"""
        **Session:** {total_reviewed} cards  
        🟢 Good: {stats['good']} • 🔵 Easy: {stats['easy']} • 🟠 Hard: {stats['hard']} • 🔴 Again: {stats['again']}
        """)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔁 Study Again", use_container_width=True, type="primary"):
            st.session_state.current_card_index = 0
            st.session_state.show_answer = False
            st.session_state.session_stats = {'again': 0, 'hard': 0, 'good': 0, 'easy': 0}
            st.rerun()
    with col_b:
        if st.button("📚 All Decks", use_container_width=True):
            st.switch_page("pages/2_Decks.py")
