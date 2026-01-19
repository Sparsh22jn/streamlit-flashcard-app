"""
Streamlit Flashcard App for Complex Topics
Main application entry point.

A Streamlit-based flashcard application that uses AI (Claude API) 
to generate educational flashcards on any topic.
"""

import streamlit as st
import os
from database import init_database

# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION - Protect your API credits!
# ═══════════════════════════════════════════════════════════════

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Get password from environment variable or Streamlit secrets
        correct_password = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")
        
        if not correct_password:
            # No password set - allow access (for local development)
            st.session_state["password_correct"] = True
            return
            
        if st.session_state.get("password_input") == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run or password not yet verified
    if "password_correct" not in st.session_state:
        # Check if password is required
        correct_password = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")
        if not correct_password:
            # No password configured - skip authentication
            return True
            
        # Show password input
        st.markdown("""
        <div style='text-align: center; padding: 50px 0;'>
            <h1>🔐 Flashcard App</h1>
            <p>This app requires authentication.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password_input",
            placeholder="Enter password to access the app"
        )
        st.markdown("---")
        st.caption("💡 Contact the app owner for access credentials.")
        return False
    
    # Password was entered previously
    if not st.session_state.get("password_correct", False):
        # Password incorrect
        st.markdown("""
        <div style='text-align: center; padding: 50px 0;'>
            <h1>🔐 Flashcard App</h1>
            <p>This app requires authentication.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password_input",
            placeholder="Enter password to access the app"
        )
        st.error("😕 Password incorrect. Please try again.")
        return False
    
    # Password correct
    return True


# Check authentication before showing anything
if not check_password():
    st.stop()

# Initialize database on startup
init_database()

# App configuration
st.set_page_config(
    page_title="Flashcard App for Complex Topics",
    page_icon="🎴",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for the app
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px 0;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }
    
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Main page content
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.title("🎴 Flashcard App for Complex Topics")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
### Welcome! 👋

This app helps you learn complex topics by generating AI-powered flashcards. 
Whether you're studying algorithms, history, science, or any other subject, 
our intelligent flashcard generator creates personalized study materials tailored to your level.

""")

# Feature highlights
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='feature-card'>
        <h4>📝 Generate Flashcards</h4>
        <p>Create custom flashcards on any topic using AI. Choose your complexity level and number of cards.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
        <h4>📖 Review & Learn</h4>
        <p>Study your flashcards with an interactive flip interface. Track your progress as you learn.</p>
    </div>
    """, unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class='feature-card'>
        <h4>🧒 ELI5 / ELI10</h4>
        <p>Get simplified explanations for any concept. Perfect for building foundational understanding.</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='feature-card'>
        <h4>📱 Mobile Friendly</h4>
        <p>Study anywhere! The app works great on mobile devices and tablets.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Navigation instructions
st.info("👈 **Use the sidebar** to navigate between pages:\n\n"
        "- **Generate**: Create new flashcard sets\n"
        "- **Review**: Study your saved flashcards")

# Quick stats
st.markdown("### 📊 Quick Start")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(label="Complexity Levels", value="3", delta="Beginner → Advanced")

with col_b:
    st.metric(label="Cards per Set", value="5-50", delta="Customizable")

with col_c:
    st.metric(label="Topics", value="∞", delta="Any subject!")

st.markdown("---")

# Sample topics
st.markdown("### 💡 Sample Topics to Try")

sample_topics = [
    "Python list comprehensions",
    "World War II major events",
    "Photosynthesis process",
    "Machine learning basics",
    "Spanish irregular verbs",
    "Quantum computing fundamentals",
    "The French Revolution",
    "Data structures and algorithms"
]

# Display sample topics in a nice grid
topic_cols = st.columns(4)
for i, topic in enumerate(sample_topics):
    with topic_cols[i % 4]:
        st.markdown(f"• {topic}")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px 0;'>
    <p>Built with ❤️ using Streamlit and Google Gemini AI</p>
    <p style='font-size: 0.8em;'>© 2026 Streamlit Flashcard App for Complex Topics</p>
</div>
""", unsafe_allow_html=True)
