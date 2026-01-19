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
            FOREIGN KEY (cardset_id) REFERENCES cardsets (cardset_id)
        )
    """)
    
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
