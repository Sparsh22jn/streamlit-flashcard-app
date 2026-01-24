"""
Decks Page - View all flashcard sets as icons/cards
"""

import streamlit as st
import os
from dotenv import load_dotenv
from database import init_database, get_all_cardsets, delete_cardset
from utils import get_complexity_emoji, get_base_css, render_header

load_dotenv()

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
    page_title="My Decks | Smart FlashCards",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize dark mode
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Apply theme CSS
st.markdown(get_base_css(st.session_state.dark_mode), unsafe_allow_html=True)

# Page-specific CSS
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        max-width: 800px;
    }
    
    /* Deck card */
    .deck-card {
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
</style>
""", unsafe_allow_html=True)

# Dark mode specific overrides
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .deck-card {
            background: #161b22 !important;
            border: 1px solid #30363d !important;
        }
        .deck-card:hover {
            border-color: #238636 !important;
            box-shadow: 0 4px 16px rgba(35, 134, 54, 0.2) !important;
        }
        .deck-topic { color: #c9d1d9 !important; }
        .deck-meta { color: #8b949e !important; }
        .deck-badge { 
            background: #21262d !important; 
            color: #8b949e !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .deck-card {
            background: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
        }
        .deck-card:hover {
            border-color: #10a37f !important;
            box-shadow: 0 4px 16px rgba(16,163,127,0.15) !important;
        }
        .deck-topic { color: #1a1a1a !important; }
        .deck-meta { color: #666666 !important; }
        .deck-badge { 
            background: #f0f0f0 !important; 
            color: #555555 !important;
        }
        .empty-state { color: #666666 !important; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🎨 Theme")
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="dark_toggle_decks")
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Navigation")
    if st.button("✨ Generate", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Generate.py")
    if st.button("📖 Review", use_container_width=True):
        st.switch_page("pages/3_Review.py")
    
    st.markdown("---")
    st.caption(f"💰 Limit: ${st.session_state.get('user_spending_limit', 5.0):.2f}")

# Main content - Header
render_header()
st.caption("Your flashcard collections")

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
