"""
Decks Page - View all flashcard sets as icons/cards
"""

import streamlit as st
import os
from database import init_database, get_all_cardsets, delete_cardset
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

# Page config
st.set_page_config(
    page_title="My Decks",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimal CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }
    
    /* Title */
    .decks-title {
        font-size: 2rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .decks-subtitle {
        text-align: center;
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    
    /* Deck card */
    .deck-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .deck-card:hover {
        border-color: #10a37f;
        box-shadow: 0 4px 16px rgba(16,163,127,0.15);
        transform: translateY(-2px);
    }
    
    /* Deck icon */
    .deck-icon {
        font-size: 2.5rem;
        margin-bottom: 12px;
    }
    
    /* Deck info */
    .deck-topic {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .deck-meta {
        font-size: 0.85rem;
        color: #888;
    }
    .deck-badge {
        display: inline-block;
        background: #f0f0f0;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        color: #666;
        margin-right: 6px;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #888;
    }
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* Action buttons */
    .stButton > button {
        border-radius: 12px;
    }
    .stButton > button[kind="primary"] {
        background: #10a37f;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("### Navigation")
    if st.button("✨ Generate", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Generate.py")
    if st.button("📖 Review", use_container_width=True):
        st.switch_page("pages/3_Review.py")
    
    st.markdown("---")
    st.caption(f"💰 Limit: ${st.session_state.get('user_spending_limit', 5.0):.2f}")

# Main content
st.markdown('<p class="decks-title">📚 My Decks</p>', unsafe_allow_html=True)
st.markdown('<p class="decks-subtitle">Your flashcard collections</p>', unsafe_allow_html=True)

# Get all cardsets
cardsets = get_all_cardsets()

if not cardsets:
    # Empty state
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>No decks yet</h3>
        <p>Create your first flashcard deck to get started</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("✨ Create Your First Deck", type="primary", use_container_width=True):
        st.switch_page("pages/1_Generate.py")
else:
    # Display stats
    total_cards = sum(cs['num_cards'] for cs in cardsets)
    st.markdown(f"**{len(cardsets)}** decks • **{total_cards}** cards total")
    
    st.markdown("---")
    
    # Display decks in grid
    cols = st.columns(2)
    
    for i, cardset in enumerate(cardsets):
        with cols[i % 2]:
            emoji = get_complexity_emoji(cardset['complexity_level'])
            
            # Deck card container
            with st.container():
                # Card visual
                st.markdown(f"""
                <div class="deck-card">
                    <div class="deck-icon">{emoji}</div>
                    <div class="deck-topic">{cardset['topic']}</div>
                    <div class="deck-meta">
                        <span class="deck-badge">{cardset['num_cards']} cards</span>
                        <span class="deck-badge">{cardset['complexity_level']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    if st.button("📖 Study", key=f"study_{cardset['cardset_id']}", use_container_width=True, type="primary"):
                        st.session_state.selected_cardset = cardset['cardset_id']
                        st.switch_page("pages/3_Review.py")
                
                with btn_col2:
                    if st.button("🗑️", key=f"del_{cardset['cardset_id']}", use_container_width=True):
                        st.session_state.delete_confirm = cardset['cardset_id']
                        st.rerun()
                
                # Delete confirmation
                if st.session_state.get('delete_confirm') == cardset['cardset_id']:
                    st.warning(f"Delete **{cardset['topic']}**?")
                    confirm_col1, confirm_col2 = st.columns(2)
                    with confirm_col1:
                        if st.button("Yes, delete", key=f"confirm_{cardset['cardset_id']}", type="primary"):
                            delete_cardset(cardset['cardset_id'])
                            del st.session_state.delete_confirm
                            st.rerun()
                    with confirm_col2:
                        if st.button("Cancel", key=f"cancel_{cardset['cardset_id']}"):
                            del st.session_state.delete_confirm
                            st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
    
    # Create new deck button
    st.markdown("---")
    if st.button("✨ Create New Deck", type="primary", use_container_width=True):
        st.switch_page("pages/1_Generate.py")
