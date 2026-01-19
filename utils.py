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
    Get CSS for Anki-style card flip animation.
    
    Returns:
        CSS string for card styling
    """
    return """
    <style>
    /* Main container */
    .anki-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    /* Card flip container */
    .flip-card {
        background-color: transparent;
        width: 100%;
        max-width: 650px;
        height: 350px;
        perspective: 1000px;
        cursor: pointer;
        margin: 20px auto;
    }
    
    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s cubic-bezier(0.4, 0.0, 0.2, 1);
        transform-style: preserve-3d;
    }
    
    .flip-card.flipped .flip-card-inner {
        transform: rotateY(180deg);
    }
    
    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        box-sizing: border-box;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }
    
    .flip-card-front {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
    }
    
    .flip-card-back {
        background: linear-gradient(145deg, #134e5e 0%, #71b280 100%);
        color: white;
        transform: rotateY(180deg);
    }
    
    .card-type-label {
        position: absolute;
        top: 20px;
        left: 25px;
        font-size: 0.75em;
        text-transform: uppercase;
        letter-spacing: 3px;
        opacity: 0.7;
        font-weight: 600;
    }
    
    .card-text {
        font-size: 1.35em;
        line-height: 1.7;
        padding: 10px 20px;
        max-height: 250px;
        overflow-y: auto;
    }
    
    .tap-hint {
        position: absolute;
        bottom: 18px;
        font-size: 0.75em;
        opacity: 0.5;
        letter-spacing: 1px;
    }
    
    /* Progress bar */
    .progress-container {
        width: 100%;
        max-width: 650px;
        margin: 0 auto 10px auto;
    }
    
    .progress-bar-bg {
        background: #e0e0e0;
        border-radius: 10px;
        height: 6px;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 10px;
        transition: width 0.4s ease;
    }
    
    .progress-text {
        text-align: center;
        font-size: 0.9em;
        color: #666;
        margin-top: 8px;
    }
    
    /* Navigation buttons */
    .nav-btn {
        background: linear-gradient(145deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-size: 1em;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .nav-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .nav-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }
    
    /* Rating buttons - Anki style */
    .rating-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 20px;
        flex-wrap: wrap;
    }
    
    .rating-btn {
        padding: 12px 20px;
        border: none;
        border-radius: 12px;
        font-size: 0.9em;
        cursor: pointer;
        transition: all 0.2s ease;
        min-width: 100px;
    }
    
    .rating-btn.again {
        background: #ff6b6b;
        color: white;
    }
    
    .rating-btn.hard {
        background: #ffa502;
        color: white;
    }
    
    .rating-btn.good {
        background: #2ed573;
        color: white;
    }
    
    .rating-btn.easy {
        background: #1e90ff;
        color: white;
    }
    
    .rating-btn:hover {
        transform: scale(1.05);
        filter: brightness(1.1);
    }
    
    /* Scrollbar styling for card content */
    .card-text::-webkit-scrollbar {
        width: 6px;
    }
    
    .card-text::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 3px;
    }
    
    .card-text::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.3);
        border-radius: 3px;
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
