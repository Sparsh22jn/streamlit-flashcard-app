"""
Claude API integration for Streamlit Flashcard App for Complex Topics.
Handles AI-powered flashcard generation and explanations using Claude 3.5 Sonnet.
Includes cost tracking with spending limit protection.
"""

import os
import json
import re
from typing import List, Dict, Optional
from pathlib import Path
import anthropic
import streamlit as st

# Model configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 8192  # Increased for comprehensive flashcard generation

# Cost configuration (per million tokens)
INPUT_COST_PER_MILLION = 3.00   # $3 per 1M input tokens
OUTPUT_COST_PER_MILLION = 15.00  # $15 per 1M output tokens

# Cost tracking file
COST_TRACKER_FILE = Path(__file__).parent / ".cost_tracker.json"


def get_spending_limit() -> float:
    """Get spending limit from session state or default."""
    return st.session_state.get("user_spending_limit", 10.0)


def get_total_spent() -> float:
    """Get the total amount spent so far."""
    if COST_TRACKER_FILE.exists():
        try:
            with open(COST_TRACKER_FILE, "r") as f:
                data = json.load(f)
                return data.get("total_spent", 0.0)
        except (json.JSONDecodeError, IOError):
            return 0.0
    return 0.0


def get_cost_details() -> Dict:
    """Get detailed cost tracking information."""
    spending_limit = get_spending_limit()
    if COST_TRACKER_FILE.exists():
        try:
            with open(COST_TRACKER_FILE, "r") as f:
                data = json.load(f)
                data["spending_limit"] = spending_limit
                return data
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "total_spent": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "api_calls": 0,
        "spending_limit": spending_limit
    }


def update_cost_tracker(input_tokens: int, output_tokens: int) -> float:
    """
    Update the cost tracker with new token usage.
    
    Returns:
        The cost of this API call
    """
    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
    call_cost = input_cost + output_cost
    
    # Load existing data
    data = get_cost_details()
    
    # Update totals
    data["total_spent"] = data.get("total_spent", 0.0) + call_cost
    data["total_input_tokens"] = data.get("total_input_tokens", 0) + input_tokens
    data["total_output_tokens"] = data.get("total_output_tokens", 0) + output_tokens
    data["api_calls"] = data.get("api_calls", 0) + 1
    data["spending_limit"] = get_spending_limit()
    
    # Save updated data
    with open(COST_TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    return call_cost


def check_spending_limit() -> tuple[bool, str]:
    """
    Check if spending limit has been reached.
    
    Returns:
        Tuple of (is_allowed, message)
    """
    spending_limit = get_spending_limit()
    total_spent = get_total_spent()
    if total_spent >= spending_limit:
        return False, f"Spending limit of ${spending_limit:.2f} reached! Total spent: ${total_spent:.2f}. Increase your limit or reset the tracker."
    
    remaining = spending_limit - total_spent
    return True, f"Budget remaining: ${remaining:.2f} of ${spending_limit:.2f}"


def reset_cost_tracker():
    """Reset the cost tracker to zero."""
    data = {
        "total_spent": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "api_calls": 0,
        "spending_limit": get_spending_limit()
    }
    with open(COST_TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_client():
    """Get configured Anthropic client using session state API key."""
    # First try session state (user-provided key)
    api_key = st.session_state.get("user_api_key")
    
    # Fallback to environment variable (for backward compatibility)
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError("No API key found. Please enter your Claude API key on the main page.")
    
    return anthropic.Anthropic(api_key=api_key)


def generate_flashcards_prompt(topic: str, num_cards: int, complexity: str) -> str:
    """
    Generate the prompt for flashcard creation using industry-standard 
    learning science principles (SuperMemo's 20 Rules, Active Recall, etc.)
    
    Args:
        topic: The topic to create flashcards for
        num_cards: Number of flashcards to generate
        complexity: Complexity level (Beginner, Intermediate, Advanced)
    
    Returns:
        The formatted prompt string
    """
    return f"""You are a world-class learning scientist and expert educator specializing in creating 
optimized flashcards for long-term retention. You follow SuperMemo's "20 Rules of Formulating Knowledge" 
and evidence-based learning principles.

═══════════════════════════════════════════════════════════════════
TOPIC: {topic}
TARGET CARDS: {num_cards}
COMPLEXITY: {complexity}
═══════════════════════════════════════════════════════════════════

YOUR MISSION: Create {num_cards} masterfully crafted flashcards that will enable complete mastery 
of "{topic}" from foundational concepts to nuanced understanding.

══════════════════════════════════════════════════════════════════
📚 MANDATORY FLASHCARD DESIGN PRINCIPLES (Follow Strictly)
══════════════════════════════════════════════════════════════════

1. MINIMUM INFORMATION PRINCIPLE
   - Each card tests ONE atomic concept only
   - If an answer has multiple parts, split into separate cards
   - Simple cards = faster reviews = better retention
   
2. USE CLOZE DELETIONS & ACTIVE RECALL
   - Frame questions to force active retrieval, not recognition
   - "What is X?" → "X is the process of ___ that enables ___"
   - Never ask yes/no questions without requiring explanation

3. BUILD KNOWLEDGE HIERARCHICALLY  
   - Start with foundational definitions
   - Progress to relationships between concepts
   - Then applications and edge cases
   - Create "prerequisite chains" where Card N builds on Card N-1

4. AVOID ORPHAN KNOWLEDGE
   - Every concept must connect to others
   - Include cards that explicitly link concepts: "How does X relate to Y?"
   - Create "bridge cards" between sub-topics

5. USE CONCRETE EXAMPLES
   - Abstract concepts need concrete anchors
   - Include real-world scenarios and use cases
   - For technical topics: include code snippets or formulas where applicable

6. EMPLOY MULTIPLE ENCODING
   - Test same concept from different angles
   - Include: definitions, examples, counter-examples, applications
   - Use analogies and metaphors for difficult concepts

7. INCLUDE COMMON MISCONCEPTIONS
   - "What is a common mistake when..." 
   - "Why does X NOT work for Y?"
   - Address typical confusion points explicitly

8. ADD CONTEXT AND "WHY"
   - Don't just test "what" - test understanding
   - "Why is X important?" "When would you use X over Y?"
   - Include the reasoning, not just the fact

══════════════════════════════════════════════════════════════════
📊 CARD DISTRIBUTION FOR {complexity.upper()} LEVEL
══════════════════════════════════════════════════════════════════

{"BEGINNER Distribution:" if complexity == "Beginner" else ""}
{"- 40% Core Definitions: Essential vocabulary and foundational concepts" if complexity == "Beginner" else ""}
{"- 30% Simple Explanations: How things work at a basic level" if complexity == "Beginner" else ""}
{"- 20% Basic Examples: Concrete instances of abstract concepts" if complexity == "Beginner" else ""}
{"- 10% Connections: How concepts relate to each other" if complexity == "Beginner" else ""}

{"INTERMEDIATE Distribution:" if complexity == "Intermediate" else ""}
{"- 20% Review Definitions: Reinforce key terms with deeper context" if complexity == "Intermediate" else ""}
{"- 30% Mechanisms: How and why things work" if complexity == "Intermediate" else ""}
{"- 25% Applications: Real-world use cases and problem-solving" if complexity == "Intermediate" else ""}
{"- 15% Comparisons: X vs Y, trade-offs, when to use which" if complexity == "Intermediate" else ""}
{"- 10% Common Pitfalls: Mistakes to avoid, misconceptions" if complexity == "Intermediate" else ""}

{"ADVANCED Distribution:" if complexity == "Advanced" else ""}
{"- 15% Deep Theory: Mathematical foundations, formal definitions" if complexity == "Advanced" else ""}
{"- 25% Edge Cases: Boundary conditions, exceptions, limitations" if complexity == "Advanced" else ""}
{"- 25% Optimization: Best practices, performance, efficiency" if complexity == "Advanced" else ""}
{"- 20% Integration: Cross-cutting concerns, system design" if complexity == "Advanced" else ""}
{"- 15% Expert Knowledge: Nuances, debates in the field, cutting-edge" if complexity == "Advanced" else ""}

══════════════════════════════════════════════════════════════════
🎯 QUESTION TYPES TO INCLUDE (Vary for engagement)
══════════════════════════════════════════════════════════════════

Mix these question formats throughout your cards:

1. DEFINITION: "Define [concept] in the context of [topic]"
2. EXPLANATION: "Explain how [process] works"
3. COMPARISON: "What is the key difference between [A] and [B]?"
4. APPLICATION: "In what situation would you use [technique]?"
5. CAUSATION: "Why does [phenomenon] occur?"
6. CONSEQUENCE: "What happens if [condition]?"
7. PREREQUISITE: "What must be true before [X] can happen?"
8. ENUMERATION: "What are the [N] key components of [X]?" (split into N cards)
9. ANALOGY: "How is [concept] similar to [everyday thing]?"
10. TROUBLESHOOTING: "If [symptom], what is the likely cause?"

══════════════════════════════════════════════════════════════════
✍️ ANSWER QUALITY STANDARDS (COMPREHENSIVE ANSWERS REQUIRED)
══════════════════════════════════════════════════════════════════

EVERY answer MUST be THOROUGH and EDUCATIONAL. Treat each answer as a mini-lesson.

ANSWER LENGTH REQUIREMENTS:
- MINIMUM: 3-5 sentences for simple concepts
- STANDARD: 5-8 sentences for most concepts  
- COMPLEX: 8-12 sentences for advanced/nuanced topics
- Include examples, context, and implications in EVERY answer

ANSWER STRUCTURE (Follow this pattern):
1. DIRECT ANSWER: State the core answer clearly first
2. EXPLANATION: Explain WHY or HOW (the mechanism/reasoning)
3. EXAMPLE: Provide a concrete example or use case
4. CONTEXT: Add relevant context (when to use, why it matters, connections)
5. EDGE CASE/NOTE: Mention important caveats, exceptions, or pro tips

EXAMPLE OF A GOOD COMPREHENSIVE ANSWER:
Question: "What is memoization in programming?"
Answer: "Memoization is an optimization technique that stores the results of expensive 
function calls and returns the cached result when the same inputs occur again. It works 
by maintaining a lookup table (usually a hash map) where keys are function inputs and 
values are computed outputs. For example, in a recursive Fibonacci function, without 
memoization calculating fib(50) would make billions of redundant calls, but with memoization 
it only computes each value once, reducing time complexity from O(2^n) to O(n). Memoization 
is particularly valuable for recursive algorithms with overlapping subproblems, such as 
dynamic programming solutions. However, it trades memory for speed—the cache can grow large 
for functions with many unique inputs. It's distinct from general caching in that it's 
specifically for pure functions where the same inputs always produce the same outputs."

WHAT TO INCLUDE IN ANSWERS:
✅ The complete conceptual explanation (not just a definition)
✅ Real-world analogies that make abstract concepts tangible
✅ Practical examples showing the concept in action
✅ Common use cases and when/why you'd apply this
✅ Relationships to other concepts in the topic
✅ Important gotchas, limitations, or common mistakes
✅ For technical topics: code snippets, formulas, or diagrams described in text
✅ Historical context or origin if it aids understanding
✅ Memory aids, mnemonics, or memorable phrases when applicable

For technical/programming topics:
- Include DETAILED code examples (5-15 lines) with comments
- Show both correct usage AND common incorrect patterns
- Explain the "why" behind syntax or design choices
- Include time/space complexity when relevant
- Mention related functions, libraries, or alternatives

══════════════════════════════════════════════════════════════════
🚫 ANTI-PATTERNS TO AVOID
══════════════════════════════════════════════════════════════════

NEVER create cards that:
- Test multiple concepts at once (split them!)
- Have vague questions ("Tell me about X")
- Have answers that could be confused with other concepts
- Require memorizing arbitrary lists without understanding
- Are trivially easy or impossibly hard for the level
- Duplicate information from other cards without adding value

══════════════════════════════════════════════════════════════════
📋 OUTPUT FORMAT
══════════════════════════════════════════════════════════════════

Return ONLY valid JSON in this exact format (no markdown, no code blocks, just pure JSON):
{{
  "flashcards": [
    {{
      "question": "Your precisely-worded question here",
      "answer": "Your concise, complete answer here"
    }}
  ]
}}

Now generate exactly {num_cards} exceptional flashcards for "{topic}" at {complexity} level."""


def parse_json_response(response_text: str) -> Optional[Dict]:
    """
    Safely parse JSON from Claude's response.
    
    Args:
        response_text: The raw response text from Claude
    
    Returns:
        Parsed JSON dictionary or None if parsing fails
    """
    # Clean the response text
    cleaned = response_text.strip()
    
    # Try to find JSON in the response
    try:
        # First, try direct parsing
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
    ]
    
    for pattern in json_patterns:
        match = re.search(pattern, cleaned)
        if match:
            try:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                continue
    
    # Try to find raw JSON object with flashcards
    # Find the first { and last } to extract JSON
    try:
        first_brace = cleaned.find('{')
        last_brace = cleaned.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_str = cleaned[first_brace:last_brace + 1]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Last resort: try to find flashcards array directly
    try:
        array_match = re.search(r'\[\s*\{[\s\S]*"question"[\s\S]*"answer"[\s\S]*\}\s*\]', cleaned)
        if array_match:
            return {"flashcards": json.loads(array_match.group(0))}
    except json.JSONDecodeError:
        pass
    
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
    # Check spending limit before making API call
    is_allowed, limit_message = check_spending_limit()
    if not is_allowed:
        return {
            "success": False,
            "error": limit_message
        }
    
    try:
        client = get_client()
        prompt = generate_flashcards_prompt(topic, num_cards, complexity_level)
        
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Track costs
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        call_cost = update_cost_tracker(input_tokens, output_tokens)
        
        response_text = response.content[0].text
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
                cost_details = get_cost_details()
                return {
                    "success": True,
                    "flashcards": valid_cards,
                    "cost_info": {
                        "this_call": call_cost,
                        "total_spent": cost_details["total_spent"],
                        "remaining_budget": get_spending_limit() - cost_details["total_spent"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No valid flashcards found in response",
                    "raw_response": response_text[:500]  # First 500 chars for debugging
                }
        else:
            return {
                "success": False,
                "error": f"Could not parse flashcards from AI response. Response starts with: {response_text[:200]}..."
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
    # Check spending limit before making API call
    is_allowed, limit_message = check_spending_limit()
    if not is_allowed:
        return {
            "success": False,
            "error": limit_message
        }
    
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
        
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Track costs
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        call_cost = update_cost_tracker(input_tokens, output_tokens)
        
        explanation = response.content[0].text.strip()
        
        cost_details = get_cost_details()
        return {
            "success": True,
            "explanation": explanation,
            "cost_info": {
                "this_call": call_cost,
                "total_spent": cost_details["total_spent"],
                "remaining_budget": get_spending_limit() - cost_details["total_spent"]
            }
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


def generate_mnemonic(question: str, answer: str) -> Dict:
    """
    Generate a memorable mnemonic, memory trick, or memory palace technique for a flashcard.
    
    Args:
        question: The flashcard question
        answer: The flashcard answer
    
    Returns:
        Dictionary with 'success' boolean and either 'mnemonic' or 'error'
    """
    # Check spending limit before making API call
    is_allowed, limit_message = check_spending_limit()
    if not is_allowed:
        return {
            "success": False,
            "error": limit_message
        }
    
    prompt = f"""You are a world-class memory champion and expert in mnemonic techniques.

═══════════════════════════════════════════════════════════════════
FLASHCARD TO MEMORIZE:
Question: {question}
Answer: {answer}
═══════════════════════════════════════════════════════════════════

Create a POWERFUL, MEMORABLE mnemonic device to help remember this information forever.

USE ONE OR MORE OF THESE PROVEN MEMORY TECHNIQUES:

1. **ACRONYM/ACROSTIC**: Create a catchy acronym or memorable sentence where first letters 
   spell out key terms (e.g., "Every Good Boy Does Fine" for musical notes E-G-B-D-F)

2. **VISUAL ASSOCIATION**: Create a vivid, bizarre, or exaggerated mental image that links 
   the question to the answer. The weirder and more emotional, the better!

3. **RHYME/SONG**: Create a short rhyme, jingle, or set it to a familiar tune
   (e.g., "In 1492, Columbus sailed the ocean blue")

4. **STORY/NARRATIVE**: Craft a mini-story that encodes the key information in a memorable 
   sequence of events

5. **METHOD OF LOCI (Memory Palace)**: Describe how to place elements in familiar locations 
   (your house, a route you know) to create spatial memory anchors

6. **CHUNKING + PATTERN**: Break complex info into memorable chunks with patterns
   (e.g., phone numbers: 555-123-4567)

7. **PEG SYSTEM**: Associate with numbers or familiar ordered list 
   (1=bun, 2=shoe, 3=tree, etc.)

8. **KEYWORD METHOD**: For abstract terms, find a similar-sounding concrete word and 
   create a visual link

═══════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════

**🧠 Technique Used:** [Name the technique(s)]

**✨ The Mnemonic:**
[Your creative mnemonic device - make it vivid, funny, or shocking for better recall]

**🎯 How It Works:**
[Brief explanation of how this helps remember the answer]

**💡 Visualization Tip:**
[Optional: Add a specific mental image to reinforce the memory]

Make it MEMORABLE, CREATIVE, and EFFECTIVE. The goal is that the user will NEVER forget this!"""

    try:
        client = get_client()
        
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Track costs
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        call_cost = update_cost_tracker(input_tokens, output_tokens)
        
        mnemonic = response.content[0].text.strip()
        
        cost_details = get_cost_details()
        return {
            "success": True,
            "mnemonic": mnemonic,
            "cost_info": {
                "this_call": call_cost,
                "total_spent": cost_details["total_spent"],
                "remaining_budget": get_spending_limit() - cost_details["total_spent"]
            }
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
