"""
Utility functions for Streamlit Flashcard App for Complex Topics.
"""

from datetime import datetime
from typing import Optional


def format_datetime(dt_string: Optional[str]) -> str:
    """
    Format a datetime string for display.
    
    Args:
        dt_string: ISO format datetime string or None
    
    Returns:
        Formatted date string or 'Never' if None
    """
    if not dt_string:
        return "Never"
    
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except (ValueError, TypeError):
        return str(dt_string)


def format_date_short(dt_string: Optional[str]) -> str:
    """
    Format a datetime string in short form.
    
    Args:
        dt_string: ISO format datetime string or None
    
    Returns:
        Short formatted date string
    """
    if not dt_string:
        return "Unknown"
    
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%m/%d/%Y")
    except (ValueError, TypeError):
        return str(dt_string)


def get_complexity_emoji(complexity: str) -> str:
    """
    Get an emoji for the complexity level.
    
    Args:
        complexity: Complexity level string
    
    Returns:
        Appropriate emoji
    """
    emojis = {
        "Beginner": "🌱",
        "Intermediate": "🌿",
        "Advanced": "🌳"
    }
    return emojis.get(complexity, "📚")


def get_complexity_color(complexity: str) -> str:
    """
    Get a color for the complexity level.
    
    Args:
        complexity: Complexity level string
    
    Returns:
        Color string for Streamlit
    """
    colors = {
        "Beginner": "green",
        "Intermediate": "orange", 
        "Advanced": "red"
    }
    return colors.get(complexity, "blue")


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to a maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_topic(topic: str) -> tuple[bool, str]:
    """
    Validate a topic input.
    
    Args:
        topic: The topic string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not topic:
        return False, "Topic cannot be empty"
    
    if len(topic.strip()) < 3:
        return False, "Topic must be at least 3 characters"
    
    if len(topic) > 500:
        return False, "Topic must be less than 500 characters"
    
    return True, ""


def get_card_flip_css() -> str:
    """
    Get CSS for card flip animation.
    
    Returns:
        CSS string for card styling
    """
    return """
    <style>
    .flashcard-container {
        perspective: 1000px;
        margin: 20px auto;
        max-width: 600px;
    }
    
    .flashcard {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 40px;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: white;
        font-size: 1.2em;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .flashcard:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    .flashcard-question {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .flashcard-answer {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .card-label {
        font-size: 0.7em;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 15px;
        opacity: 0.8;
    }
    
    .card-content {
        font-size: 1.1em;
        line-height: 1.6;
    }
    
    .progress-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 8px;
        margin: 10px 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    </style>
    """


def get_explanation_css() -> str:
    """
    Get CSS for explanation cards.
    
    Returns:
        CSS string for explanation styling
    """
    return """
    <style>
    .eli-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        color: #333;
    }
    
    .eli5-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    }
    
    .eli10-card {
        background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
    }
    
    .eli-title {
        font-weight: bold;
        margin-bottom: 10px;
        font-size: 0.9em;
    }
    
    .eli-content {
        line-height: 1.6;
    }
    </style>
    """
