"""
Claude API integration for Streamlit Flashcard App for Complex Topics.
Handles AI-powered flashcard generation and explanations.
"""

import os
import json
import re
from typing import List, Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_client() -> Anthropic:
    """Get an Anthropic client instance."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    return Anthropic(api_key=api_key)


def generate_flashcards_prompt(topic: str, num_cards: int, complexity: str) -> str:
    """
    Generate the prompt for flashcard creation.
    
    Args:
        topic: The topic to create flashcards for
        num_cards: Number of flashcards to generate
        complexity: Complexity level (Beginner, Intermediate, Advanced)
    
    Returns:
        The formatted prompt string
    """
    return f"""You are an expert educator creating flashcards for learning complex topics.

Topic: {topic}
Number of flashcards: {num_cards}
Complexity level: {complexity}

Generate exactly {num_cards} flashcards about {topic} at a {complexity} level.

Requirements:
- Questions should test understanding, not just memorization
- Answers should be clear, concise, and accurate
- Include a mix of conceptual and practical questions
- For {complexity} level:
  * Beginner: Focus on definitions, basic concepts, and fundamental principles
  * Intermediate: Include applications, connections between concepts, and real-world examples
  * Advanced: Cover edge cases, optimizations, deep theory, and nuanced understanding

Return ONLY valid JSON in this exact format (no markdown, no code blocks, just pure JSON):
{{
  "flashcards": [
    {{
      "question": "What is...",
      "answer": "..."
    }}
  ]
}}"""


def parse_json_response(response_text: str) -> Optional[Dict]:
    """
    Safely parse JSON from Claude's response.
    
    Args:
        response_text: The raw response text from Claude
    
    Returns:
        Parsed JSON dictionary or None if parsing fails
    """
    # Try to find JSON in the response
    try:
        # First, try direct parsing
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'\{[\s\S]*"flashcards"[\s\S]*\}'
    ]
    
    for pattern in json_patterns:
        match = re.search(pattern, response_text)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                continue
    
    return None


def generate_flashcards(topic: str, num_cards: int, complexity_level: str) -> Dict:
    """
    Generate flashcards using Claude API.
    
    Args:
        topic: The topic to create flashcards for
        num_cards: Number of flashcards to generate
        complexity_level: Complexity level (Beginner, Intermediate, Advanced)
    
    Returns:
        Dictionary with 'success' boolean and either 'flashcards' list or 'error' message
    """
    try:
        client = get_client()
        prompt = generate_flashcards_prompt(topic, num_cards, complexity_level)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        parsed = parse_json_response(response_text)
        
        if parsed and "flashcards" in parsed:
            flashcards = parsed["flashcards"]
            
            # Validate flashcard structure
            valid_cards = []
            for card in flashcards:
                if "question" in card and "answer" in card:
                    valid_cards.append({
                        "question": card["question"],
                        "answer": card["answer"]
                    })
            
            if valid_cards:
                return {
                    "success": True,
                    "flashcards": valid_cards
                }
            else:
                return {
                    "success": False,
                    "error": "No valid flashcards found in response"
                }
        else:
            return {
                "success": False,
                "error": "Could not parse flashcards from AI response"
            }
            
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"API error: {str(e)}"
        }


def generate_eli_explanation(question: str, answer: str, level: int) -> Dict:
    """
    Generate an ELI5 or ELI10 explanation for a flashcard.
    
    Args:
        question: The flashcard question
        answer: The flashcard answer
        level: Either 5 (ELI5) or 10 (ELI10)
    
    Returns:
        Dictionary with 'success' boolean and either 'explanation' or 'error'
    """
    age_description = "5-year-old" if level == 5 else "10-year-old"
    
    prompt = f"""You are an expert at explaining complex topics to children.

Original Question: {question}
Original Answer: {answer}

Please explain this concept as if you were talking to a {age_description} child.

Requirements:
- Use simple words and short sentences
- Use analogies and examples from everyday life
- {"Avoid technical terms completely" if level == 5 else "Minimize technical terms and explain any you use"}
- Make it engaging and fun
- Keep it concise (2-4 sentences for ELI5, 3-5 sentences for ELI10)

Provide ONLY the explanation, no preamble or metadata."""

    try:
        client = get_client()
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        explanation = message.content[0].text.strip()
        
        return {
            "success": True,
            "explanation": explanation
        }
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"API error: {str(e)}"
        }
