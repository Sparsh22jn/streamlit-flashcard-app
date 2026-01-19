"""
Flashcard App - Minimal Design
Clean, ChatGPT-style interface for generating flashcards.
"""

import streamlit as st
import os
from database import init_database

# App configuration
st.set_page_config(
    page_title="Smart FlashCards",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimal CSS
st.markdown("""
<style>
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Clean typography */
    .main-title {
        font-size: 2.5rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .subtitle {
        font-size: 1rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Auth container */
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Clean input styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #ddd;
        padding: 12px 16px;
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: #10a37f;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 500;
    }
    .stButton > button[kind="primary"]:hover {
        background: #0d8a6b;
    }
    
    /* Secondary button */
    .stButton > button {
        border-radius: 12px;
        padding: 10px 20px;
    }
    
    /* Sidebar minimal */
    [data-testid="stSidebar"] {
        background: #fafafa;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════

def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Validate Claude API key with minimal API call."""
    import anthropic
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=5,
            messages=[{"role": "user", "content": "Hi"}]
        )
        return True, "Valid"
    except anthropic.AuthenticationError:
        return False, "Invalid API key"
    except anthropic.PermissionDeniedError:
        return False, "Permission denied"
    except anthropic.RateLimitError:
        return False, "Rate limited"
    except anthropic.APIStatusError as e:
        if "credit" in str(e).lower():
            return False, "No credits remaining"
        return False, str(e)
    except Exception as e:
        return False, str(e)


def check_password():
    """Simple password check."""
    correct_password = os.getenv("APP_PASSWORD", "")
    if not correct_password:
        try:
            correct_password = st.secrets.get("APP_PASSWORD", "")
        except:
            correct_password = ""
    
    if not correct_password:
        return True
    
    if st.session_state.get("password_correct"):
        return True
    
    st.markdown('<p class="main-title">🧠 Smart FlashCards</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Enter password to continue</p>', unsafe_allow_html=True)
    
    password = st.text_input("Password", type="password", label_visibility="collapsed", 
                             placeholder="Enter password")
    
    if st.button("Continue", type="primary", use_container_width=True):
        if password == correct_password:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Incorrect password")
    
    return False


def check_api_key():
    """API key input with validation."""
    if st.session_state.get("user_api_key") and st.session_state.get("api_key_validated"):
        return True
    
    st.markdown('<p class="main-title">🧠 Smart FlashCards</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Enter your Claude API key to get started</p>', unsafe_allow_html=True)
    
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        label_visibility="collapsed"
    )
    
    spending_limit = st.slider(
        "Spending limit (USD)",
        min_value=1.0,
        max_value=50.0,
        value=5.0,
        step=1.0,
        help="App stops generating when this limit is reached"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Start", type="primary", use_container_width=True):
            if not api_key:
                st.error("Please enter your API key")
            elif not api_key.startswith("sk-ant-"):
                st.error("Invalid format (should start with sk-ant-)")
            else:
                with st.spinner("Validating..."):
                    is_valid, message = validate_api_key(api_key)
                
                if is_valid:
                    st.session_state["user_api_key"] = api_key
                    st.session_state["user_spending_limit"] = spending_limit
                    st.session_state["api_key_validated"] = True
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        st.link_button("Get key →", "https://console.anthropic.com/", use_container_width=True)
    
    with st.expander("How to get an API key"):
        st.markdown("""
        1. Go to [console.anthropic.com](https://console.anthropic.com/)
        2. Sign up or log in
        3. Navigate to **API Keys**
        4. Click **Create Key** and copy it
        """)
    
    return False


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if not check_password():
    st.stop()

if not check_api_key():
    st.stop()

init_database()

# Redirect to Generate page as main landing
st.switch_page("pages/1_Generate.py")
