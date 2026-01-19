"""
Streamlit Flashcard App for Complex Topics
Main application entry point.

A Streamlit-based flashcard application that uses AI (Claude API) 
to generate educational flashcards on any topic.
"""

import streamlit as st
import os
from database import init_database

# App configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Flashcard App for Complex Topics",
    page_icon="🎴",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# STEP 1: PASSWORD AUTHENTICATION
# ═══════════════════════════════════════════════════════════════

def check_password():
    """Returns `True` if the user has the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        correct_password = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")
        
        if not correct_password:
            st.session_state["password_correct"] = True
            return
            
        if st.session_state.get("password_input") == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        correct_password = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")
        if not correct_password:
            return True
            
        st.markdown("""
        <div style='text-align: center; padding: 30px 0;'>
            <h1>🎴 Flashcard App</h1>
            <h3>🔐 Authentication Required</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password_input",
            placeholder="Enter password to access the app"
        )
        st.caption("💡 Contact the app owner for access credentials.")
        return False
    
    if not st.session_state.get("password_correct", False):
        st.markdown("""
        <div style='text-align: center; padding: 30px 0;'>
            <h1>🎴 Flashcard App</h1>
            <h3>🔐 Authentication Required</h3>
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
    
    return True


# ═══════════════════════════════════════════════════════════════
# STEP 2: API KEY INPUT WITH VALIDATION
# ═══════════════════════════════════════════════════════════════

def validate_api_key(api_key: str) -> tuple[bool, str]:
    """
    Validate the Claude API key by making a minimal API call.
    
    Returns:
        Tuple of (is_valid, message)
    """
    import anthropic
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        # Make a minimal API call to validate the key
        # Using a tiny prompt to minimize cost (~$0.0001)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=5,
            messages=[{"role": "user", "content": "Hi"}]
        )
        return True, "✅ API key is valid!"
    except anthropic.AuthenticationError:
        return False, "❌ Invalid API key. Please check and try again."
    except anthropic.PermissionDeniedError:
        return False, "❌ API key doesn't have permission. Check your Anthropic account."
    except anthropic.RateLimitError:
        return False, "⚠️ Rate limited. The key seems valid but you've hit usage limits."
    except anthropic.APIStatusError as e:
        if "credit" in str(e).lower() or "balance" in str(e).lower():
            return False, "❌ No credits remaining on this API key. Please add credits at console.anthropic.com"
        return False, f"❌ API Error: {str(e)}"
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"


def check_api_key():
    """Returns `True` if user has provided a valid API key."""
    
    # Check if API key is already in session and validated
    if st.session_state.get("user_api_key") and st.session_state.get("api_key_validated"):
        return True
    
    # Show API key input page
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1>🎴 Flashcard App</h1>
        <h3>🔑 Enter Your Claude API Key</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Instructions
    st.markdown("""
    ### How to Get Your API Key
    
    1. **Go to Anthropic Console**: [console.anthropic.com](https://console.anthropic.com/)
    2. **Sign up or Log in** to your account
    3. **Navigate to API Keys**: Click on "API Keys" in the sidebar
    4. **Create a new key**: Click "Create Key" and copy it
    5. **Paste below** and click "Validate & Continue"
    
    > 💡 **Note**: You'll be charged based on your own API usage. 
    > The app has a built-in spending limit to protect you.
    """)
    
    st.markdown("---")
    
    # API Key input
    api_key = st.text_input(
        "🔑 Claude API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        help="Your API key starts with 'sk-ant-api03-'"
    )
    
    # Spending limit input
    spending_limit = st.number_input(
        "💰 Spending Limit (USD)",
        min_value=1.0,
        max_value=100.0,
        value=5.0,
        step=1.0,
        help="The app will stop generating when this limit is reached"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✅ Validate & Continue", type="primary", use_container_width=True):
            if not api_key:
                st.error("❌ Please enter your API key")
            elif not api_key.startswith("sk-ant-"):
                st.error("❌ Invalid API key format. It should start with 'sk-ant-'")
            else:
                # Validate the API key
                with st.spinner("🔄 Validating API key..."):
                    is_valid, message = validate_api_key(api_key)
                
                if is_valid:
                    st.session_state["user_api_key"] = api_key
                    st.session_state["user_spending_limit"] = spending_limit
                    st.session_state["api_key_validated"] = True
                    st.success(message + " Redirecting...")
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        st.link_button("🔗 Get API Key", "https://console.anthropic.com/", use_container_width=True)
    
    st.markdown("---")
    
    # Security note
    st.info("""
    🔒 **Security Note**: Your API key is stored only in your browser session. 
    It is never saved to any database or server. When you close the browser, 
    the key is gone.
    """)
    
    # Common issues
    with st.expander("❓ Common Issues"):
        st.markdown("""
        **"Invalid API key"**
        - Make sure you copied the entire key (starts with `sk-ant-api03-`)
        - Check that you're using a Claude API key, not OpenAI
        
        **"No credits remaining"**
        - Go to [console.anthropic.com](https://console.anthropic.com/)
        - Add credits to your account under Billing
        
        **"Permission denied"**
        - Your API key may have been revoked
        - Create a new key in the Anthropic console
        """)
    
    return False


# ═══════════════════════════════════════════════════════════════
# MAIN APP FLOW
# ═══════════════════════════════════════════════════════════════

# Step 1: Check password
if not check_password():
    st.stop()

# Step 2: Check API key
if not check_api_key():
    st.stop()

# Step 3: Initialize database and show main app
init_database()

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
    <p>Built with ❤️ using Streamlit and Claude AI</p>
    <p style='font-size: 0.8em;'>© 2026 Streamlit Flashcard App for Complex Topics</p>
</div>
""", unsafe_allow_html=True)

# Show API key status in sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔑 API Status")
    if st.session_state.get("user_api_key"):
        st.success("✅ API Key Active")
        st.caption(f"💰 Limit: ${st.session_state.get('user_spending_limit', 5.0):.2f}")
        if st.button("🔄 Change API Key", use_container_width=True):
            del st.session_state["user_api_key"]
            st.rerun()
