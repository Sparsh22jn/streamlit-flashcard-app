"""
Flashcard Review Page
Interactive flashcard viewer with flip animation and ELI5/ELI10 explanations.
"""

import streamlit as st
from database import (
    init_database, 
    get_all_cardsets, 
    get_flashcards_by_set,
    get_cardset_by_id,
    update_review_stats,
    save_explanation,
    get_explanation
)
from flashcard_generator import generate_eli_explanation
from utils import (
    get_complexity_emoji, 
    format_date_short,
    get_card_flip_css,
    get_explanation_css
)

# Initialize database
init_database()

# Page configuration
st.set_page_config(
    page_title="Review Flashcards",
    page_icon="📖",
    layout="centered"
)

# Inject custom CSS
st.markdown(get_card_flip_css(), unsafe_allow_html=True)
st.markdown(get_explanation_css(), unsafe_allow_html=True)

st.title("📖 Review Flashcards")
st.markdown("Study your flashcards and track your progress!")

st.markdown("---")

# Initialize session state
if 'current_card_index' not in st.session_state:
    st.session_state.current_card_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'selected_cardset' not in st.session_state:
    st.session_state.selected_cardset = None

# Get all cardsets
cardsets = get_all_cardsets()

if not cardsets:
    st.warning("📭 No flashcard sets found!")
    st.info("👈 Go to **Generate** page to create your first flashcard set!")
    st.stop()

# Cardset selector
st.subheader("Select a Flashcard Set")

# Format cardset options for dropdown
cardset_options = {
    f"{get_complexity_emoji(cs['complexity_level'])} {cs['topic']} ({cs['num_cards']} cards) - {format_date_short(cs['created_at'])}": cs['cardset_id']
    for cs in cardsets
}

selected_option = st.selectbox(
    "Choose a set to study:",
    options=list(cardset_options.keys()),
    index=0
)

selected_cardset_id = cardset_options[selected_option]

# Check if cardset changed
if st.session_state.selected_cardset != selected_cardset_id:
    st.session_state.selected_cardset = selected_cardset_id
    st.session_state.current_card_index = 0
    st.session_state.show_answer = False

# Load flashcards
flashcards = get_flashcards_by_set(selected_cardset_id)
cardset_info = get_cardset_by_id(selected_cardset_id)

if not flashcards:
    st.error("No flashcards found in this set.")
    st.stop()

total_cards = len(flashcards)
current_index = st.session_state.current_card_index
current_card = flashcards[current_index]

st.markdown("---")

# Progress indicator
st.subheader(f"Card {current_index + 1} of {total_cards}")

# Progress bar
progress = (current_index + 1) / total_cards
st.progress(progress)

# Display complexity and topic
st.caption(f"{get_complexity_emoji(cardset_info['complexity_level'])} {cardset_info['complexity_level']} • {cardset_info['topic']}")

st.markdown("---")

# Flashcard display
if st.session_state.show_answer:
    # Show Answer
    st.markdown(f"""
    <div class="flashcard-container">
        <div class="flashcard flashcard-answer">
            <div>
                <div class="card-label">💡 Answer</div>
                <div class="card-content">{current_card['answer']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Show Question
    st.markdown(f"""
    <div class="flashcard-container">
        <div class="flashcard flashcard-question">
            <div>
                <div class="card-label">❓ Question</div>
                <div class="card-content">{current_card['question']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Navigation buttons
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Previous", use_container_width=True, disabled=(current_index == 0)):
        st.session_state.current_card_index -= 1
        st.session_state.show_answer = False
        st.rerun()

with col2:
    flip_label = "🔄 Show Question" if st.session_state.show_answer else "🔄 Show Answer"
    if st.button(flip_label, use_container_width=True):
        st.session_state.show_answer = not st.session_state.show_answer
        # Update review stats when answer is revealed
        if st.session_state.show_answer:
            update_review_stats(current_card['id'])
        st.rerun()

with col3:
    if st.button("➡️ Next", use_container_width=True, disabled=(current_index == total_cards - 1)):
        st.session_state.current_card_index += 1
        st.session_state.show_answer = False
        st.rerun()

# ELI5 / ELI10 Section (only show when answer is visible)
if st.session_state.show_answer:
    st.markdown("---")
    st.subheader("🧒 Need a simpler explanation?")
    
    col_eli5, col_eli10 = st.columns(2)
    
    with col_eli5:
        if st.button("👶 Explain Like I'm 5", use_container_width=True):
            # Check if explanation exists
            existing = get_explanation(current_card['id'], 'eli5')
            
            if existing:
                st.session_state.eli5_explanation = existing
            else:
                with st.spinner("Generating simple explanation..."):
                    result = generate_eli_explanation(
                        current_card['question'],
                        current_card['answer'],
                        5
                    )
                    if result['success']:
                        save_explanation(current_card['id'], 'eli5', result['explanation'])
                        st.session_state.eli5_explanation = result['explanation']
                    else:
                        st.error(f"Failed to generate explanation: {result['error']}")
            st.rerun()
    
    with col_eli10:
        if st.button("🧒 Explain Like I'm 10", use_container_width=True):
            # Check if explanation exists
            existing = get_explanation(current_card['id'], 'eli10')
            
            if existing:
                st.session_state.eli10_explanation = existing
            else:
                with st.spinner("Generating explanation..."):
                    result = generate_eli_explanation(
                        current_card['question'],
                        current_card['answer'],
                        10
                    )
                    if result['success']:
                        save_explanation(current_card['id'], 'eli10', result['explanation'])
                        st.session_state.eli10_explanation = result['explanation']
                    else:
                        st.error(f"Failed to generate explanation: {result['error']}")
            st.rerun()
    
    # Display existing explanations
    eli5_text = current_card.get('explanation_eli5') or st.session_state.get('eli5_explanation')
    eli10_text = current_card.get('explanation_eli10') or st.session_state.get('eli10_explanation')
    
    if eli5_text:
        st.markdown(f"""
        <div class="eli-card eli5-card">
            <div class="eli-title">👶 ELI5 (Explain Like I'm 5)</div>
            <div class="eli-content">{eli5_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    if eli10_text:
        st.markdown(f"""
        <div class="eli-card eli10-card">
            <div class="eli-title">🧒 ELI10 (Explain Like I'm 10)</div>
            <div class="eli-content">{eli10_text}</div>
        </div>
        """, unsafe_allow_html=True)

# Keyboard shortcuts info
st.markdown("---")
st.caption("💡 **Tip:** Click 'Show Answer' to reveal the answer, then navigate to the next card!")

# Jump to card
st.markdown("---")
with st.expander("🔢 Jump to specific card"):
    jump_to = st.number_input(
        "Enter card number:",
        min_value=1,
        max_value=total_cards,
        value=current_index + 1
    )
    if st.button("Go to Card"):
        st.session_state.current_card_index = jump_to - 1
        st.session_state.show_answer = False
        st.rerun()

# Card statistics
with st.expander("📊 Card Statistics"):
    st.markdown(f"""
    - **Times Reviewed:** {current_card['times_reviewed']}
    - **Last Reviewed:** {current_card['last_reviewed_at'] or 'Never'}
    - **Created:** {current_card['created_at']}
    """)
