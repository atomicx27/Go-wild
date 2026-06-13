import os
import json
import pytest
from unittest.mock import patch, MagicMock

import agent
from models import SessionLocal, Deck, Flashcard, init_db

# Initialize a clean DB in the test env
init_db()

def setup_function():
    # Clean up DB before each test
    db = SessionLocal()
    db.query(Flashcard).delete()
    db.query(Deck).delete()
    db.commit()
    db.close()

@patch('agent.requests.post')
def test_generate_flashcards_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {
            "content": json.dumps({
                "deck_name": "Test Deck",
                "flashcards": [
                    {"front": "Q1", "back": "A1"}
                ]
            })
        }
    }
    mock_post.return_value = mock_response

    result = agent.generate_flashcards("Some test text")
    assert result is not None
    assert result["deck_name"] == "Test Deck"
    assert len(result["flashcards"]) == 1
    assert result["flashcards"][0]["front"] == "Q1"

@patch('agent.requests.post')
def test_generate_flashcards_fallback(mock_post):
    mock_post.side_effect = Exception("Connection error")

    result = agent.generate_flashcards("Some test text")
    assert result is not None
    assert result["deck_name"] == "Mocked Deck"
    assert len(result["flashcards"]) == 2

@patch('agent.generate_flashcards')
def test_process_file(mock_generate, tmp_path):
    # Mock the LLM generation
    mock_generate.return_value = {
        "deck_name": "File Deck",
        "flashcards": [
            {"front": "F1", "back": "B1"},
            {"front": "F2", "back": "B2"}
        ]
    }

    # Create a temporary file
    test_file = tmp_path / "test_notes.txt"
    test_file.write_text("Hello world")

    # Call the processor
    agent.process_file(str(test_file))

    # Check the database
    db = SessionLocal()
    deck = db.query(Deck).filter(Deck.name == "File Deck").first()
    assert deck is not None

    cards = db.query(Flashcard).filter(Flashcard.deck_id == deck.id).all()
    assert len(cards) == 2
    assert cards[0].front == "F1"

    db.close()
