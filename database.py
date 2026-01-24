"""
Database module for Streamlit Flashcard App for Complex Topics.
Handles all Supabase database operations.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid
import os
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

# Initialize Supabase client
from supabase import create_client, Client


def get_supabase_client() -> Client:
    """Get Supabase client using credentials from secrets or environment."""
    # Try Streamlit secrets first (for deployed app)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variables (for local development)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError(
            "Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY "
            "in Streamlit secrets or environment variables."
        )
    
    return create_client(url, key)


@st.cache_resource
def get_client() -> Client:
    """Get cached Supabase client."""
    return get_supabase_client()


def init_database():
    """
    Initialize database connection (tables already created in Supabase).
    This function is kept for compatibility but tables are managed in Supabase dashboard.
    """
    # Tables are created in Supabase dashboard, just verify connection
    try:
        client = get_client()
        # Quick connectivity check
        client.table("cardsets").select("cardset_id").limit(1).execute()
    except Exception as e:
        st.error(f"Database connection error: {e}")
        raise


def create_cardset(topic: str, num_cards: int, complexity: str) -> str:
    """
    Create a new cardset and return its ID.
    
    Args:
        topic: The topic of the flashcard set
        num_cards: Number of cards in the set
        complexity: Complexity level (Beginner, Intermediate, Advanced)
    
    Returns:
        The unique cardset_id
    """
    cardset_id = str(uuid.uuid4())[:8]  # Short unique ID
    
    client = get_client()
    client.table("cardsets").insert({
        "cardset_id": cardset_id,
        "topic": topic,
        "num_cards": num_cards,
        "complexity_level": complexity
    }).execute()
    
    return cardset_id


def save_flashcard(cardset_id: str, topic: str, question: str, answer: str, complexity: str) -> int:
    """
    Save a single flashcard to the database.
    
    Args:
        cardset_id: The ID of the cardset this card belongs to
        topic: The topic of the flashcard
        question: The question text
        answer: The answer text
        complexity: Complexity level
    
    Returns:
        The ID of the inserted flashcard
    """
    client = get_client()
    result = client.table("flashcards").insert({
        "cardset_id": cardset_id,
        "topic": topic,
        "question": question,
        "answer": answer,
        "complexity_level": complexity
    }).execute()
    
    return result.data[0]["id"]


def save_flashcards_bulk(cardset_id: str, topic: str, flashcards: List[Dict], complexity: str):
    """
    Save multiple flashcards at once.
    
    Args:
        cardset_id: The ID of the cardset
        topic: The topic of the flashcards
        flashcards: List of dicts with 'question' and 'answer' keys
        complexity: Complexity level
    """
    client = get_client()
    
    cards_to_insert = [
        {
            "cardset_id": cardset_id,
            "topic": topic,
            "question": card["question"],
            "answer": card["answer"],
            "complexity_level": complexity
        }
        for card in flashcards
    ]
    
    client.table("flashcards").insert(cards_to_insert).execute()


def get_all_cardsets() -> List[Dict]:
    """
    Get all cardsets with metadata.
    
    Returns:
        List of cardset dictionaries
    """
    client = get_client()
    result = client.table("cardsets").select("*").order("created_at", desc=True).execute()
    
    return result.data


def get_flashcards_by_set(cardset_id: str) -> List[Dict]:
    """
    Get all flashcards in a specific cardset.
    
    Args:
        cardset_id: The ID of the cardset
    
    Returns:
        List of flashcard dictionaries
    """
    client = get_client()
    result = client.table("flashcards").select(
        "id, cardset_id, topic, question, answer, complexity_level, "
        "created_at, times_reviewed, last_reviewed_at, "
        "explanation_eli5, explanation_eli10, mnemonic"
    ).eq("cardset_id", cardset_id).order("id").execute()
    
    return result.data


def get_cardset_by_id(cardset_id: str) -> Optional[Dict]:
    """
    Get a specific cardset by ID.
    
    Args:
        cardset_id: The ID of the cardset
    
    Returns:
        Cardset dictionary or None if not found
    """
    client = get_client()
    result = client.table("cardsets").select("*").eq("cardset_id", cardset_id).execute()
    
    if result.data:
        return result.data[0]
    return None


def get_review_order(cardset_id: str) -> str:
    """
    Get the review order preference for a cardset.
    
    Args:
        cardset_id: The ID of the cardset
    
    Returns:
        'ordered' or 'random' (defaults to 'ordered' if not set)
    """
    client = get_client()
    try:
        result = client.table("cardsets").select("review_order").eq("cardset_id", cardset_id).execute()
        if result.data and result.data[0].get("review_order"):
            return result.data[0]["review_order"]
    except Exception:
        # Column might not exist yet
        pass
    return "ordered"


def set_review_order(cardset_id: str, order: str):
    """
    Set the review order preference for a cardset.
    
    Args:
        cardset_id: The ID of the cardset
        order: 'ordered' or 'random'
    """
    client = get_client()
    try:
        client.table("cardsets").update({
            "review_order": order
        }).eq("cardset_id", cardset_id).execute()
    except Exception as e:
        # Column might not exist - user needs to add it in Supabase
        st.warning(f"Could not save review order preference. Please add 'review_order' column (type: text) to the cardsets table in Supabase.")


def update_review_stats(card_id: int):
    """
    Update the review statistics for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
    """
    client = get_client()
    
    # First get current times_reviewed
    result = client.table("flashcards").select("times_reviewed").eq("id", card_id).execute()
    current_reviews = result.data[0]["times_reviewed"] if result.data else 0
    
    # Update with incremented value
    client.table("flashcards").update({
        "times_reviewed": (current_reviews or 0) + 1,
        "last_reviewed_at": datetime.now().isoformat()
    }).eq("id", card_id).execute()


def save_explanation(card_id: int, explanation_type: str, explanation_text: str):
    """
    Save an ELI5 or ELI10 explanation for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
        explanation_type: Either 'eli5' or 'eli10'
        explanation_text: The explanation text
    """
    client = get_client()
    column = f"explanation_{explanation_type}"
    
    client.table("flashcards").update({
        column: explanation_text
    }).eq("id", card_id).execute()


def get_explanation(card_id: int, explanation_type: str) -> Optional[str]:
    """
    Get an existing explanation for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
        explanation_type: Either 'eli5' or 'eli10'
    
    Returns:
        The explanation text or None if not found
    """
    client = get_client()
    column = f"explanation_{explanation_type}"
    
    result = client.table("flashcards").select(column).eq("id", card_id).execute()
    
    if result.data and result.data[0].get(column):
        return result.data[0][column]
    return None


def save_mnemonic(card_id: int, mnemonic_text: str):
    """
    Save a mnemonic for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
        mnemonic_text: The mnemonic text
    """
    client = get_client()
    
    client.table("flashcards").update({
        "mnemonic": mnemonic_text
    }).eq("id", card_id).execute()


def get_mnemonic(card_id: int) -> Optional[str]:
    """
    Get an existing mnemonic for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
    
    Returns:
        The mnemonic text or None if not found
    """
    client = get_client()
    
    result = client.table("flashcards").select("mnemonic").eq("id", card_id).execute()
    
    if result.data and result.data[0].get("mnemonic"):
        return result.data[0]["mnemonic"]
    return None


def delete_cardset(cardset_id: str):
    """
    Delete a cardset and all its flashcards.
    
    Args:
        cardset_id: The ID of the cardset to delete
    """
    client = get_client()
    
    # Get all flashcard IDs for this cardset to delete their progress
    flashcards = client.table("flashcards").select("id").eq("cardset_id", cardset_id).execute()
    card_ids = [f["id"] for f in flashcards.data]
    
    # Delete card progress for these flashcards
    if card_ids:
        client.table("card_progress").delete().in_("card_id", card_ids).execute()
    
    # Delete flashcards (CASCADE should handle this, but being explicit)
    client.table("flashcards").delete().eq("cardset_id", cardset_id).execute()
    
    # Delete cardset
    client.table("cardsets").delete().eq("cardset_id", cardset_id).execute()


# ============================================
# Spaced Repetition Functions (Anki-style)
# ============================================

def init_spaced_repetition_table():
    """
    Initialize spaced repetition tracking (table already created in Supabase).
    This function is kept for compatibility.
    """
    # Table is created in Supabase dashboard
    pass


def get_card_progress(card_id: int) -> Optional[Dict]:
    """Get spaced repetition progress for a card."""
    client = get_client()
    
    result = client.table("card_progress").select("*").eq("card_id", card_id).execute()
    
    if result.data:
        return result.data[0]
    return None


def update_card_progress(card_id: int, rating: str) -> Dict:
    """
    Update card progress based on user rating (Anki SM-2 algorithm).
    
    Args:
        card_id: The flashcard ID
        rating: One of 'again', 'hard', 'good', 'easy'
    
    Returns:
        Dict with new interval and next review date
    """
    client = get_client()
    
    # Get existing progress or create new
    result = client.table("card_progress").select("*").eq("card_id", card_id).execute()
    
    if result.data:
        progress = result.data[0]
    else:
        progress = {
            'card_id': card_id,
            'ease_factor': 2.5,
            'interval_days': 0,
            'repetitions': 0
        }
    
    # SM-2 Algorithm implementation
    ease_factor = progress['ease_factor']
    interval = progress['interval_days']
    reps = progress['repetitions']
    
    # Rating multipliers and ease adjustments
    if rating == 'again':
        # Failed - reset to beginning
        interval = 0  # Will show again in same session or next minute
        ease_factor = max(1.3, ease_factor - 0.2)
        reps = 0
        next_interval_minutes = 1  # Show again in 1 minute
    elif rating == 'hard':
        # Struggled but got it
        if interval == 0:
            interval = 1
        else:
            interval = max(1, int(interval * 1.2))
        ease_factor = max(1.3, ease_factor - 0.15)
        reps += 1
        next_interval_minutes = interval * 24 * 60
    elif rating == 'good':
        # Normal recall
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = int(interval * ease_factor)
        reps += 1
        next_interval_minutes = interval * 24 * 60
    elif rating == 'easy':
        # Easy recall - bonus interval
        if reps == 0:
            interval = 4
        elif reps == 1:
            interval = 10
        else:
            interval = int(interval * ease_factor * 1.3)
        ease_factor = min(3.0, ease_factor + 0.15)
        reps += 1
        next_interval_minutes = interval * 24 * 60
    
    # Calculate next review date
    now = datetime.now()
    if rating == 'again':
        next_review = now + timedelta(minutes=1)
    else:
        next_review = now + timedelta(days=interval)
    
    # Upsert progress
    progress_data = {
        "card_id": card_id,
        "ease_factor": ease_factor,
        "interval_days": interval,
        "repetitions": reps,
        "next_review_date": next_review.isoformat(),
        "last_review_date": now.isoformat()
    }
    
    # Try to update, if no rows affected, insert
    existing = client.table("card_progress").select("id").eq("card_id", card_id).execute()
    
    if existing.data:
        client.table("card_progress").update(progress_data).eq("card_id", card_id).execute()
    else:
        client.table("card_progress").insert(progress_data).execute()
    
    # Also update the flashcards table
    update_review_stats(card_id)
    
    return {
        'interval_days': interval,
        'ease_factor': ease_factor,
        'next_review': next_review.isoformat(),
        'repetitions': reps
    }


def get_next_intervals(card_id: int) -> Dict[str, str]:
    """
    Get the next interval for each rating option.
    
    Returns:
        Dict with 'again', 'hard', 'good', 'easy' intervals as strings
    """
    progress = get_card_progress(card_id)
    
    if not progress:
        # New card defaults
        return {
            'again': '<1m',
            'hard': '1d',
            'good': '1d',
            'easy': '4d'
        }
    
    ease = progress['ease_factor']
    interval = progress['interval_days']
    reps = progress['repetitions']
    
    def format_interval(days):
        if days == 0:
            return '<1m'
        elif days == 1:
            return '1d'
        elif days < 30:
            return f'{days}d'
        elif days < 365:
            months = days // 30
            return f'{months}mo'
        else:
            years = days / 365
            return f'{years:.1f}y'
    
    # Calculate intervals for each option
    if reps == 0:
        again_int, hard_int, good_int, easy_int = 0, 1, 1, 4
    elif reps == 1:
        again_int = 0
        hard_int = max(1, int(interval * 1.2))
        good_int = 6
        easy_int = 10
    else:
        again_int = 0
        hard_int = max(1, int(interval * 1.2))
        good_int = int(interval * ease)
        easy_int = int(interval * ease * 1.3)
    
    return {
        'again': format_interval(again_int),
        'hard': format_interval(hard_int),
        'good': format_interval(good_int),
        'easy': format_interval(easy_int)
    }


def get_due_cards(cardset_id: str) -> List[Dict]:
    """Get cards that are due for review."""
    client = get_client()
    
    now = datetime.now().isoformat()
    
    # Get all flashcards for this cardset
    flashcards_result = client.table("flashcards").select("*").eq("cardset_id", cardset_id).execute()
    flashcards = flashcards_result.data
    
    if not flashcards:
        return []
    
    # Get card IDs
    card_ids = [f["id"] for f in flashcards]
    
    # Get progress for these cards
    progress_result = client.table("card_progress").select("*").in_("card_id", card_ids).execute()
    progress_map = {p["card_id"]: p for p in progress_result.data}
    
    # Filter and combine: cards with no progress (new) or due cards
    due_cards = []
    for card in flashcards:
        progress = progress_map.get(card["id"])
        if progress is None:
            # New card - no progress entry
            card["next_review_date"] = None
            card["interval_days"] = None
            card["ease_factor"] = None
            card["repetitions"] = None
            due_cards.append(card)
        elif progress["next_review_date"] is None or progress["next_review_date"] <= now:
            # Due for review
            card["next_review_date"] = progress["next_review_date"]
            card["interval_days"] = progress["interval_days"]
            card["ease_factor"] = progress["ease_factor"]
            card["repetitions"] = progress["repetitions"]
            due_cards.append(card)
    
    # Sort: new cards first (None), then by next_review_date
    due_cards.sort(key=lambda x: (x["next_review_date"] is not None, x["next_review_date"] or ""))
    
    return due_cards

