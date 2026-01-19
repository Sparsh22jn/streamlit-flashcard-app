"""
Generate Flashcards - Minimal ChatGPT-style Interface
"""

import streamlit as st
import os
from database import init_database, create_cardset, save_flashcards_bulk, get_all_cardsets
from flashcard_generator import generate_flashcards

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
    page_title="Smart FlashCards",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimal CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide app.py from sidebar */
    [data-testid="stSidebarNav"] li:first-child {display: none;}
    
    /* Fix layout */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 700px;
    }
    
    /* Reduce header padding */
    header[data-testid="stHeader"] {
        height: 0;
    }
    
    /* Main title */
    .gen-title {
        font-size: 1.8rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 0.25rem;
        margin-top: 0;
    }
    .gen-subtitle {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    
    /* Input area */
    .stTextArea textarea {
        border-radius: 16px;
        border: 1px solid #ddd;
        padding: 16px;
        font-size: 1rem;
        min-height: 100px;
    }
    .stTextArea textarea:focus {
        border-color: #10a37f;
        box-shadow: 0 0 0 1px #10a37f;
    }
    
    /* Options row */
    .options-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Generate button */
    .stButton > button[kind="primary"] {
        background: #10a37f;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 500;
        font-size: 1rem;
    }
    .stButton > button[kind="primary"]:hover {
        background: #0d8a6b;
    }
    
    /* Suggestion chips */
    .chip {
        display: inline-block;
        background: #f0f0f0;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85rem;
        color: #444;
        cursor: pointer;
        transition: all 0.2s;
    }
    .chip:hover {
        background: #e0e0e0;
    }
    
    /* Success card */
    .success-card {
        background: linear-gradient(135deg, #10a37f 0%, #0d8a6b 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        text-align: center;
        margin: 1rem 0;
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
        color: #333;
        margin-bottom: 8px;
    }
    .preview-a {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Nav link */
    .nav-link {
        text-align: center;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize dark mode
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Dark mode CSS override
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .stApp { background-color: #0d1117 !important; }
        [data-testid="stSidebar"] { background-color: #161b22 !important; }
        [data-testid="stSidebar"] * { color: #c9d1d9 !important; }
        p, span, div, h1, h2, h3, h4, label { color: #c9d1d9 !important; }
        .gen-title, .gen-subtitle { color: #c9d1d9 !important; }
        .stTextArea textarea { 
            background-color: #161b22 !important; 
            color: #c9d1d9 !important;
            border-color: #30363d !important;
        }
        .stButton > button {
            background-color: #21262d !important;
            border: 1px solid #30363d !important;
            color: #c9d1d9 !important;
        }
        .stButton > button[kind="primary"] {
            background: #238636 !important;
            border: none !important;
        }
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

# Main content
st.markdown('<p class="gen-title">🧠 Smart FlashCards</p>', unsafe_allow_html=True)
st.markdown('<p class="gen-subtitle">AI-powered flashcards for smarter learning</p>', unsafe_allow_html=True)

# Topic input
topic = st.text_area(
    "Topic",
    placeholder="e.g., Python decorators, The French Revolution, Quantum physics...",
    label_visibility="collapsed",
    height=80
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
    
    # Display as chips
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.topic_suggestion = suggestion
                st.rerun()
    
    # Load suggestion into input if clicked
    if 'topic_suggestion' in st.session_state:
        topic = st.session_state.topic_suggestion
        del st.session_state.topic_suggestion
        st.rerun()

# Quick link to decks
existing_sets = get_all_cardsets()
if existing_sets:
    st.markdown("---")
    st.markdown(f"📚 You have **{len(existing_sets)}** deck{'s' if len(existing_sets) > 1 else ''} → ", unsafe_allow_html=True)
    if st.button("View My Decks"):
        st.switch_page("pages/2_Decks.py")
