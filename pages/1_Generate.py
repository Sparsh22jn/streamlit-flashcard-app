"""
Generate Flashcards - Minimal ChatGPT-style Interface
"""

import streamlit as st
import os
from dotenv import load_dotenv
from database import init_database, create_cardset, save_flashcards_bulk, get_all_cardsets
from flashcard_generator import generate_flashcards
from utils import get_base_css, render_header

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
    page_title="Generate | Smart FlashCards",
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
        padding-bottom: 1rem;
        max-width: 700px;
    }
    
    header[data-testid="stHeader"] {
        height: 0;
    }
    
    /* Input area */
    .stTextArea textarea {
        border-radius: 16px;
        padding: 16px;
        font-size: 1rem;
        min-height: 100px;
    }
    
    /* Generate button */
    .stButton > button[kind="primary"] {
        padding: 14px 28px;
        font-weight: 500;
        font-size: 1rem;
    }
    
    /* Success card */
    .success-card {
        background: linear-gradient(135deg, #10a37f 0%, #0d8a6b 100%);
        border-radius: 16px;
        padding: 24px;
        color: white !important;
        text-align: center;
        margin: 1rem 0;
    }
    .success-card h3, .success-card p {
        color: white !important;
    }
    
    /* Preview card */
    .preview-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border-left: 4px solid #10a37f;
    }
    .preview-q {
        font-weight: 600;
        color: #333 !important;
        margin-bottom: 8px;
    }
    .preview-a {
        color: #666 !important;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Dark mode specific overrides
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .success-card {
            background: linear-gradient(135deg, #238636 0%, #1a7f37 100%) !important;
            box-shadow: 0 0 20px rgba(35, 134, 54, 0.3);
        }
        .preview-card {
            background: #161b22 !important;
            border-left-color: #238636 !important;
        }
        .preview-q { color: #c9d1d9 !important; }
        .preview-a { color: #8b949e !important; }
    </style>
    """, unsafe_allow_html=True)

# Initialize state
if 'generated_cards' not in st.session_state:
    st.session_state.generated_cards = None
if 'last_topic' not in st.session_state:
    st.session_state.last_topic = None
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = ""

# Minimal navigation in sidebar
with st.sidebar:
    st.markdown("### 🎨 Theme")
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="dark_toggle_gen")
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Navigation")
    if st.button("📚 My Decks", use_container_width=True):
        st.switch_page("pages/2_Decks.py")
    if st.button("📖 Review", use_container_width=True):
        st.switch_page("pages/3_Review.py")
    
    st.markdown("---")
    st.caption(f"💰 Limit: ${st.session_state.get('user_spending_limit', 5.0):.2f}")
    if st.button("🔄 Change API Key", use_container_width=True):
        del st.session_state["user_api_key"]
        del st.session_state["api_key_validated"]
        st.switch_page("app.py")

# Main content - Header
render_header()
st.caption("AI-powered flashcards for smarter learning", help=None)

# Handle topic suggestion - set directly in widget state before rendering
if 'selected_topic' in st.session_state and st.session_state.selected_topic:
    st.session_state.topic_input = st.session_state.selected_topic
    st.session_state.selected_topic = ""  # Clear after use

# Topic input
topic = st.text_area(
    "Topic",
    placeholder="e.g., Python decorators, The French Revolution, Quantum physics...",
    label_visibility="collapsed",
    height=80,
    key="topic_input"
)

# Options row
col1, col2 = st.columns(2)

with col1:
    num_cards = st.select_slider(
        "Cards",
        options=[5, 10, 15, 20, 25, 30],
        value=10,
        help="Number of flashcards to generate"
    )

with col2:
    complexity = st.selectbox(
        "Level",
        ["Beginner", "Intermediate", "Advanced"],
        index=1,
        help="Complexity level of the content"
    )

# Generate button
st.markdown("<br>", unsafe_allow_html=True)
generate_clicked = st.button("Generate →", type="primary", use_container_width=True)

# Handle generation
if generate_clicked:
    if not topic or len(topic.strip()) < 3:
        st.error("Please enter a topic (at least 3 characters)")
    else:
        with st.spinner(f"Creating {num_cards} flashcards..."):
            result = generate_flashcards(topic.strip(), num_cards, complexity)
            
            if result["success"]:
                flashcards = result["flashcards"]
                
                # Save to database
                cardset_id = create_cardset(topic.strip(), len(flashcards), complexity)
                save_flashcards_bulk(cardset_id, topic.strip(), flashcards, complexity)
                
                st.session_state.generated_cards = flashcards
                st.session_state.last_topic = topic.strip()
                st.session_state.last_cardset_id = cardset_id
                
                # Success message
                st.markdown(f"""
                <div class="success-card">
                    <h3>✅ Created {len(flashcards)} flashcards</h3>
                    <p>{topic.strip()}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Cost info
                if "cost_info" in result:
                    cost = result["cost_info"]
                    st.caption(f"💰 Cost: ${cost['this_call']:.4f} | Remaining: ${cost['remaining_budget']:.2f}")
                
                # Preview first 3 cards
                st.markdown("### Preview")
                for i, card in enumerate(flashcards[:3]):
                    st.markdown(f"""
                    <div class="preview-card">
                        <div class="preview-q">Q: {card['question'][:100]}{'...' if len(card['question']) > 100 else ''}</div>
                        <div class="preview-a">A: {card['answer'][:150]}{'...' if len(card['answer']) > 150 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if len(flashcards) > 3:
                    st.caption(f"+ {len(flashcards) - 3} more cards")
                
                # Navigation buttons
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📚 View All Decks", use_container_width=True):
                        st.switch_page("pages/2_Decks.py")
                with col_b:
                    if st.button("📖 Start Reviewing", use_container_width=True, type="primary"):
                        st.session_state.selected_cardset = cardset_id
                        st.switch_page("pages/3_Review.py")
            else:
                st.error(f"Failed: {result['error']}")

# Suggestions (when no cards generated)
if st.session_state.generated_cards is None:
    st.markdown("---")
    st.markdown("### 💡 Try these topics")
    
    suggestions = [
        "Python list comprehensions",
        "World War II key events",
        "Machine learning basics",
        "Photosynthesis",
        "Spanish irregular verbs",
        "Data structures"
    ]
    
    # Display as clickable buttons that auto-fill the input
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.selected_topic = suggestion
                st.rerun()

# Quick link to decks
existing_sets = get_all_cardsets()
if existing_sets:
    st.markdown("---")
    st.markdown(f"📚 You have **{len(existing_sets)}** deck{'s' if len(existing_sets) > 1 else ''} → ", unsafe_allow_html=True)
    if st.button("View My Decks"):
        st.switch_page("pages/2_Decks.py")
