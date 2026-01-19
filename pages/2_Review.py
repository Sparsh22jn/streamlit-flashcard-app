"""
Flashcard Review Page - Anki Style
Interactive flashcard viewer with spaced repetition.
Click the card or button to flip it.
Swipe left for ELI5, swipe right for Mnemonics.
"""

import streamlit as st
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

# Authentication check
def check_auth():
    """Check if user is authenticated and has API key."""
    correct_password = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")
    if correct_password and not st.session_state.get("password_correct", False):
        st.warning("🔐 Please login from the main page first.")
        return False
    if not st.session_state.get("user_api_key"):
        st.warning("🔑 Please enter your API key on the main page first.")
        return False
    return True

if not check_auth():
    st.stop()

# Initialize database
init_database()
init_spaced_repetition_table()

# Page configuration
st.set_page_config(
    page_title="Review Flashcards",
    page_icon="📖",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
/* Progress bar */
.progress-container {
    max-width: 700px;
    margin: 0 auto 20px auto;
}
.progress-bar {
    height: 6px;
    background: #e0e0e0;
    border-radius: 3px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3498db, #2ecc71);
    transition: width 0.3s ease;
}
.progress-text {
    text-align: center;
    font-size: 0.85rem;
    color: #666;
    margin-top: 8px;
}

/* Question card style */
.question-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    border-radius: 16px;
    padding: 40px 30px;
    min-height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

/* Answer card style */
.answer-card {
    background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
    color: white;
    border-radius: 16px;
    padding: 40px 30px;
    min-height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.card-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    opacity: 0.7;
    margin-bottom: 20px;
}
.card-content {
    font-size: 1.25rem;
    line-height: 1.7;
}

/* ELI5 card style */
.eli5-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border-radius: 16px;
    padding: 30px 25px;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    margin-top: 15px;
}

/* Mnemonic card style */
.mnemonic-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 16px;
    padding: 30px 25px;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-start;
    text-align: left;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    margin-top: 15px;
}
.mnemonic-card .card-content {
    font-size: 1rem;
    line-height: 1.8;
    text-align: left;
    width: 100%;
}

/* Swipe hint buttons */
.swipe-container {
    display: flex;
    justify-content: space-between;
    margin-top: 15px;
    gap: 10px;
}
</style>
""", unsafe_allow_html=True)

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
if 'eli5_loading' not in st.session_state:
    st.session_state.eli5_loading = False
if 'mnemonic_loading' not in st.session_state:
    st.session_state.mnemonic_loading = False

# Get all cardsets
cardsets = get_all_cardsets()

if not cardsets:
    st.title("📖 Review Flashcards")
    st.warning("📭 No flashcard sets found!")
    st.info("👈 Go to **Generate** page to create your first flashcard set!")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("📚 Flashcard Sets")
    
    cardset_options = {
        f"{get_complexity_emoji(cs['complexity_level'])} {cs['topic']}": cs['cardset_id']
        for cs in cardsets
    }
    
    selected_option = st.selectbox(
        "Select a set:",
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
    
    flashcards = get_flashcards_by_set(selected_cardset_id)
    cardset_info = get_cardset_by_id(selected_cardset_id)
    
    if flashcards:
        total_cards = len(flashcards)
        st.caption(f"{total_cards} cards • {cardset_info['complexity_level']}")
        
        st.divider()
        
        # Session stats
        st.subheader("📊 Session Stats")
        stats = st.session_state.session_stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Again", stats['again'])
            st.metric("Good", stats['good'])
        with col2:
            st.metric("Hard", stats['hard'])
            st.metric("Easy", stats['easy'])
        
        st.divider()
        
        # Jump to card
        st.subheader("🔢 Jump to Card")
        jump_to = st.number_input(
            "Card number:",
            min_value=1,
            max_value=total_cards,
            value=st.session_state.current_card_index + 1,
            label_visibility="collapsed"
        )
        if st.button("Go", use_container_width=True):
            st.session_state.current_card_index = jump_to - 1
            st.session_state.show_answer = False
            st.rerun()

# Main content
if not flashcards:
    st.error("No flashcards found in this set.")
    st.stop()

total_cards = len(flashcards)
current_index = st.session_state.current_card_index
current_card = flashcards[current_index]

# Progress bar
progress_pct = ((current_index + 1) / total_cards) * 100
st.markdown(f"""
<div class="progress-container">
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_pct}%"></div>
    </div>
    <div class="progress-text">Card {current_index + 1} of {total_cards}</div>
</div>
""", unsafe_allow_html=True)

# Get intervals for rating buttons
intervals = get_next_intervals(current_card['id'])

# Display the flashcard
if not st.session_state.show_answer:
    # QUESTION SIDE
    st.markdown(f"""
    <div class="question-card">
        <div class="card-label">❓ Question</div>
        <div class="card-content">{current_card['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Big reveal button
    if st.button("👆 Tap to Reveal Answer", use_container_width=True, type="primary", key="flip_btn"):
        st.session_state.show_answer = True
        update_review_stats(current_card['id'])
        st.rerun()

else:
    # ANSWER SIDE
    st.markdown(f"""
    <div class="answer-card">
        <div class="card-label">💡 Answer</div>
        <div class="card-content">{current_card['answer']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # ELI5 and MNEMONIC BUTTONS (Swipe Left/Right Feature)
    # ═══════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    
    eli_col, mnem_col = st.columns(2)
    
    with eli_col:
        if st.button("⬅️ 🧒 Explain Simply (ELI5)", use_container_width=True, key="btn_eli5"):
            st.session_state.show_eli5 = not st.session_state.show_eli5
            st.session_state.show_mnemonic = False
            st.rerun()
    
    with mnem_col:
        if st.button("🧠 Memory Trick ➡️", use_container_width=True, key="btn_mnemonic"):
            st.session_state.show_mnemonic = not st.session_state.show_mnemonic
            st.session_state.show_eli5 = False
            st.rerun()
    
    # Show ELI5 Explanation
    if st.session_state.show_eli5:
        card_id = current_card['id']
        
        # Check if explanation exists in database
        existing_eli5 = get_explanation(card_id, 'eli5')
        
        if existing_eli5:
            st.markdown(f"""
            <div class="eli5-card">
                <div class="card-label">🧒 Explain Like I'm 5</div>
                <div class="card-content">{existing_eli5}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Generate new explanation
            with st.spinner("🧒 Creating simple explanation..."):
                result = generate_eli_explanation(
                    current_card['question'], 
                    current_card['answer'], 
                    level=5
                )
                
                if result['success']:
                    # Save to database
                    save_explanation(card_id, 'eli5', result['explanation'])
                    st.markdown(f"""
                    <div class="eli5-card">
                        <div class="card-label">🧒 Explain Like I'm 5</div>
                        <div class="card-content">{result['explanation']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"💰 Cost: ${result['cost_info']['this_call']:.4f} | Total: ${result['cost_info']['total_spent']:.2f}")
                else:
                    st.error(f"Could not generate explanation: {result['error']}")
    
    # Show Mnemonic
    if st.session_state.show_mnemonic:
        card_id = current_card['id']
        
        # Check if mnemonic exists in database
        existing_mnemonic = get_mnemonic(card_id)
        
        if existing_mnemonic:
            st.markdown(f"""
            <div class="mnemonic-card">
                <div class="card-label">🧠 Memory Trick</div>
                <div class="card-content">{existing_mnemonic}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Generate new mnemonic
            with st.spinner("🧠 Creating memory trick..."):
                result = generate_mnemonic(
                    current_card['question'], 
                    current_card['answer']
                )
                
                if result['success']:
                    # Save to database
                    save_mnemonic(card_id, result['mnemonic'])
                    st.markdown(f"""
                    <div class="mnemonic-card">
                        <div class="card-label">🧠 Memory Trick</div>
                        <div class="card-content">{result['mnemonic']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"💰 Cost: ${result['cost_info']['this_call']:.4f} | Total: ${result['cost_info']['total_spent']:.2f}")
                else:
                    st.error(f"Could not generate mnemonic: {result['error']}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Anki-style rating buttons
    st.markdown("### How well did you remember?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.caption(f"⏱️ {intervals['again']}")
        if st.button("🔴 Again", use_container_width=True, key="btn_again"):
            update_card_progress(current_card['id'], 'again')
            st.session_state.session_stats['again'] += 1
            st.session_state.show_answer = False
            st.session_state.show_eli5 = False
            st.session_state.show_mnemonic = False
            st.rerun()
    
    with col2:
        st.caption(f"⏱️ {intervals['hard']}")
        if st.button("🟠 Hard", use_container_width=True, key="btn_hard"):
            update_card_progress(current_card['id'], 'hard')
            st.session_state.session_stats['hard'] += 1
            if current_index < total_cards - 1:
                st.session_state.current_card_index += 1
            st.session_state.show_answer = False
            st.session_state.show_eli5 = False
            st.session_state.show_mnemonic = False
            st.rerun()
    
    with col3:
        st.caption(f"⏱️ {intervals['good']}")
        if st.button("🟢 Good", use_container_width=True, key="btn_good"):
            update_card_progress(current_card['id'], 'good')
            st.session_state.session_stats['good'] += 1
            if current_index < total_cards - 1:
                st.session_state.current_card_index += 1
            st.session_state.show_answer = False
            st.session_state.show_eli5 = False
            st.session_state.show_mnemonic = False
            st.rerun()
    
    with col4:
        st.caption(f"⏱️ {intervals['easy']}")
        if st.button("🔵 Easy", use_container_width=True, key="btn_easy"):
            update_card_progress(current_card['id'], 'easy')
            st.session_state.session_stats['easy'] += 1
            if current_index < total_cards - 1:
                st.session_state.current_card_index += 1
            st.session_state.show_answer = False
            st.session_state.show_eli5 = False
            st.session_state.show_mnemonic = False
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Previous", use_container_width=True, disabled=(current_index == 0)):
        st.session_state.current_card_index -= 1
        st.session_state.show_answer = False
        st.session_state.show_eli5 = False
        st.session_state.show_mnemonic = False
        st.rerun()

with col2:
    if st.session_state.show_answer:
        if st.button("🔄 Show Question", use_container_width=True):
            st.session_state.show_answer = False
            st.session_state.show_eli5 = False
            st.session_state.show_mnemonic = False
            st.rerun()

with col3:
    if st.button("Next ➡️", use_container_width=True, disabled=(current_index == total_cards - 1)):
        st.session_state.current_card_index += 1
        st.session_state.show_answer = False
        st.session_state.show_eli5 = False
        st.session_state.show_mnemonic = False
        st.rerun()

# Completion message
if current_index == total_cards - 1 and st.session_state.show_answer:
    st.markdown("---")
    st.success("🎉 Congratulations! You've completed this deck!")
    
    stats = st.session_state.session_stats
    total_reviewed = sum(stats.values())
    if total_reviewed > 0:
        st.markdown(f"""
        ### 📊 Session Summary
        - **Total cards reviewed:** {total_reviewed}
        - 🔴 **Again:** {stats['again']} ({stats['again']/total_reviewed*100:.0f}%)
        - 🟠 **Hard:** {stats['hard']} ({stats['hard']/total_reviewed*100:.0f}%)
        - 🟢 **Good:** {stats['good']} ({stats['good']/total_reviewed*100:.0f}%)
        - 🔵 **Easy:** {stats['easy']} ({stats['easy']/total_reviewed*100:.0f}%)
        """)
    
    if st.button("🔁 Study Again", use_container_width=True, type="primary"):
        st.session_state.current_card_index = 0
        st.session_state.show_answer = False
        st.session_state.show_eli5 = False
        st.session_state.show_mnemonic = False
        st.session_state.session_stats = {'again': 0, 'hard': 0, 'good': 0, 'easy': 0}
        st.rerun()

