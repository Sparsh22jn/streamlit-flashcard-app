"""
Flashcard Generation Page
Allows users to create new flashcard sets using AI.
"""

import streamlit as st
import os
from database import init_database, create_cardset, save_flashcards_bulk, get_all_cardsets
from flashcard_generator import generate_flashcards
from utils import validate_topic, get_complexity_emoji

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

# Page configuration
st.set_page_config(
    page_title="Generate Flashcards",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Generate Flashcards")
st.markdown("Create AI-powered flashcards on any topic!")

st.markdown("---")

# Input form
with st.form("flashcard_form"):
    st.subheader("What would you like to learn?")
    
    # Topic input
    topic = st.text_input(
        "Topic / Subject / Concept",
        placeholder="e.g., Python decorators, The French Revolution, Quantum entanglement...",
        help="Enter any topic you want to create flashcards for"
    )
    
    # Number of cards slider
    num_cards = st.slider(
        "How many flashcards?",
        min_value=5,
        max_value=50,
        value=10,
        step=5,
        help="Choose how many flashcards to generate"
    )
    
    # Complexity dropdown
    complexity = st.selectbox(
        "Complexity Level",
        options=["Beginner", "Intermediate", "Advanced"],
        index=1,
        help="Beginner: Basic concepts | Intermediate: Applications | Advanced: Deep theory"
    )
    
    # Display complexity description
    complexity_descriptions = {
        "Beginner": "🌱 Focus on definitions and basic concepts",
        "Intermediate": "🌿 Include applications and real-world connections",
        "Advanced": "🌳 Cover edge cases, optimizations, and deep theory"
    }
    st.caption(complexity_descriptions[complexity])
    
    # Submit button
    submitted = st.form_submit_button("🚀 Generate Flashcards", use_container_width=True)

# Handle form submission
if submitted:
    # Validate input
    is_valid, error_message = validate_topic(topic)
    
    if not is_valid:
        st.error(f"❌ {error_message}")
    else:
        # Show generation progress
        with st.spinner(f"🤖 Generating {num_cards} flashcards about '{topic}'..."):
            # Call Claude API
            result = generate_flashcards(topic, num_cards, complexity)
            
            if result["success"]:
                flashcards = result["flashcards"]
                
                # Create cardset in database
                cardset_id = create_cardset(topic, len(flashcards), complexity)
                
                # Save flashcards
                save_flashcards_bulk(cardset_id, topic, flashcards, complexity)
                
                # Success message
                st.success(f"✅ Successfully generated {len(flashcards)} flashcards!")
                st.info(f"📋 Cardset ID: `{cardset_id}`")
                
                # Show cost information
                if "cost_info" in result:
                    cost = result["cost_info"]
                    st.caption(f"💰 Cost: ${cost['this_call']:.4f} | Total spent: ${cost['total_spent']:.2f} | Remaining: ${cost['remaining_budget']:.2f}")
                
                # Display generated flashcards
                st.markdown("---")
                st.subheader(f"Preview: {get_complexity_emoji(complexity)} {topic}")
                
                for i, card in enumerate(flashcards, 1):
                    with st.expander(f"Card {i}: {card['question'][:50]}...", expanded=(i <= 3)):
                        st.markdown("**Question:**")
                        st.markdown(card['question'])
                        st.markdown("**Answer:**")
                        st.markdown(card['answer'])
                
                # Navigation prompt
                st.markdown("---")
                st.info("👈 Go to **Review** page in the sidebar to study these flashcards!")
                
            else:
                st.error(f"❌ Failed to generate flashcards: {result['error']}")
                st.markdown("""
                **Troubleshooting tips:**
                - Check that your ANTHROPIC_API_KEY is set correctly
                - Try a different topic or fewer cards
                - Check your API quota at console.anthropic.com
                """)

# Show existing cardsets
st.markdown("---")
st.subheader("📚 Your Flashcard Sets")

cardsets = get_all_cardsets()

if cardsets:
    for cardset in cardsets:
        emoji = get_complexity_emoji(cardset['complexity_level'])
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{emoji} {cardset['topic']}**")
            with col2:
                st.caption(f"{cardset['num_cards']} cards")
            with col3:
                st.caption(cardset['complexity_level'])
        st.divider()
else:
    st.info("No flashcard sets yet. Generate your first set above! ☝️")

# Tips section
st.markdown("---")
st.markdown("### 💡 Tips for Better Flashcards")

tips = [
    "**Be specific**: 'Python list comprehensions' works better than just 'Python'",
    "**Match complexity to your level**: Start with Beginner if you're new to a topic",
    "**Optimal number**: 10-20 cards is usually ideal for a study session",
    "**Break down large topics**: Create multiple sets for comprehensive subjects"
]

for tip in tips:
    st.markdown(f"• {tip}")
