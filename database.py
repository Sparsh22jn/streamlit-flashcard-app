"""
Database module for Streamlit Flashcard App for Complex Topics.
Handles all SQLite database operations.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import uuid


DATABASE_NAME = "flashcards.db"


def get_connection():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create cardsets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cardsets (
            cardset_id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            num_cards INTEGER NOT NULL,
            complexity_level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create flashcards table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cardset_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            complexity_level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            times_reviewed INTEGER DEFAULT 0,
            last_reviewed_at TIMESTAMP,
            explanation_eli5 TEXT,
            explanation_eli10 TEXT,
            mnemonic TEXT,
            FOREIGN KEY (cardset_id) REFERENCES cardsets (cardset_id)
        )
    """)
    
    # Add mnemonic column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE flashcards ADD COLUMN mnemonic TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()


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
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO cardsets (cardset_id, topic, num_cards, complexity_level)
        VALUES (?, ?, ?, ?)
    """, (cardset_id, topic, num_cards, complexity))
    
    conn.commit()
    conn.close()
    
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
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO flashcards (cardset_id, topic, question, answer, complexity_level)
        VALUES (?, ?, ?, ?, ?)
    """, (cardset_id, topic, question, answer, complexity))
    
    card_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return card_id


def save_flashcards_bulk(cardset_id: str, topic: str, flashcards: List[Dict], complexity: str):
    """
    Save multiple flashcards at once.
    
    Args:
        cardset_id: The ID of the cardset
        topic: The topic of the flashcards
        flashcards: List of dicts with 'question' and 'answer' keys
        complexity: Complexity level
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    for card in flashcards:
        cursor.execute("""
            INSERT INTO flashcards (cardset_id, topic, question, answer, complexity_level)
            VALUES (?, ?, ?, ?, ?)
        """, (cardset_id, topic, card['question'], card['answer'], complexity))
    
    conn.commit()
    conn.close()


def get_all_cardsets() -> List[Dict]:
    """
    Get all cardsets with metadata.
    
    Returns:
        List of cardset dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cardset_id, topic, num_cards, complexity_level, created_at
        FROM cardsets
        ORDER BY created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_flashcards_by_set(cardset_id: str) -> List[Dict]:
    """
    Get all flashcards in a specific cardset.
    
    Args:
        cardset_id: The ID of the cardset
    
    Returns:
        List of flashcard dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, cardset_id, topic, question, answer, complexity_level,
               created_at, times_reviewed, last_reviewed_at,
               explanation_eli5, explanation_eli10
        FROM flashcards
        WHERE cardset_id = ?
        ORDER BY id
    """, (cardset_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_cardset_by_id(cardset_id: str) -> Optional[Dict]:
    """
    Get a specific cardset by ID.
    
    Args:
        cardset_id: The ID of the cardset
    
    Returns:
        Cardset dictionary or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cardset_id, topic, num_cards, complexity_level, created_at
        FROM cardsets
        WHERE cardset_id = ?
    """, (cardset_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def update_review_stats(card_id: int):
    """
    Update the review statistics for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE flashcards
        SET times_reviewed = times_reviewed + 1,
            last_reviewed_at = ?
        WHERE id = ?
    """, (datetime.now(), card_id))
    
    conn.commit()
    conn.close()


def save_explanation(card_id: int, explanation_type: str, explanation_text: str):
    """
    Save an ELI5 or ELI10 explanation for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
        explanation_type: Either 'eli5' or 'eli10'
        explanation_text: The explanation text
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    column = f"explanation_{explanation_type}"
    cursor.execute(f"""
        UPDATE flashcards
        SET {column} = ?
        WHERE id = ?
    """, (explanation_text, card_id))
    
    conn.commit()
    conn.close()


def get_explanation(card_id: int, explanation_type: str) -> Optional[str]:
    """
    Get an existing explanation for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
        explanation_type: Either 'eli5' or 'eli10'
    
    Returns:
        The explanation text or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    column = f"explanation_{explanation_type}"
    cursor.execute(f"""
        SELECT {column}
        FROM flashcards
        WHERE id = ?
    """, (card_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0]:
        return row[0]
    return None


def save_mnemonic(card_id: int, mnemonic_text: str):
    """
    Save a mnemonic for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
        mnemonic_text: The mnemonic text
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE flashcards
        SET mnemonic = ?
        WHERE id = ?
    """, (mnemonic_text, card_id))
    
    conn.commit()
    conn.close()


def get_mnemonic(card_id: int) -> Optional[str]:
    """
    Get an existing mnemonic for a flashcard.
    
    Args:
        card_id: The ID of the flashcard
    
    Returns:
        The mnemonic text or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT mnemonic
        FROM flashcards
        WHERE id = ?
    """, (card_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0]:
        return row[0]
    return None


def delete_cardset(cardset_id: str):
    """
    Delete a cardset and all its flashcards.
    
    Args:
        cardset_id: The ID of the cardset to delete
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete flashcards first (foreign key constraint)
    cursor.execute("DELETE FROM flashcards WHERE cardset_id = ?", (cardset_id,))
    
    # Delete cardset
    cursor.execute("DELETE FROM cardsets WHERE cardset_id = ?", (cardset_id,))
    
    conn.commit()
    conn.close()


# ============================================
# Spaced Repetition Functions (Anki-style)
# ============================================

def init_spaced_repetition_table():
    """Initialize the spaced repetition tracking table."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER UNIQUE NOT NULL,
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 0,
            repetitions INTEGER DEFAULT 0,
            next_review_date TEXT,
            last_review_date TEXT,
            FOREIGN KEY (card_id) REFERENCES flashcards (id)
        )
    """)
    
    conn.commit()
    conn.close()


def get_card_progress(card_id: int) -> Optional[Dict]:
    """Get spaced repetition progress for a card."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM card_progress WHERE card_id = ?
    """, (card_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
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
    from datetime import datetime, timedelta
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get existing progress or create new
    cursor.execute("SELECT * FROM card_progress WHERE card_id = ?", (card_id,))
    row = cursor.fetchone()
    
    if row:
        progress = dict(row)
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
    cursor.execute("""
        INSERT INTO card_progress (card_id, ease_factor, interval_days, repetitions, next_review_date, last_review_date)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(card_id) DO UPDATE SET
            ease_factor = excluded.ease_factor,
            interval_days = excluded.interval_days,
            repetitions = excluded.repetitions,
            next_review_date = excluded.next_review_date,
            last_review_date = excluded.last_review_date
    """, (card_id, ease_factor, interval, reps, next_review.isoformat(), now.isoformat()))
    
    conn.commit()
    conn.close()
    
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
    from datetime import datetime
    
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Get cards that are due or new (no progress entry)
    cursor.execute("""
        SELECT f.*, cp.next_review_date, cp.interval_days, cp.ease_factor, cp.repetitions
        FROM flashcards f
        LEFT JOIN card_progress cp ON f.id = cp.card_id
        WHERE f.cardset_id = ?
        AND (cp.next_review_date IS NULL OR cp.next_review_date <= ?)
        ORDER BY cp.next_review_date ASC NULLS FIRST
    """, (cardset_id, now))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

