import os
import sqlite3
import pytest
from unittest.mock import patch
from neural_flash import db
import time

@pytest.fixture
def mock_db(tmp_path):
    db_file = tmp_path / "test_flashcards.db"

    with patch("neural_flash.db.DB_FILE", str(db_file)):
        db.init_db()
        yield db_file

def test_add_card_and_get_all(mock_db):
    db.add_card("What is 2+2?", "4", "math.txt")
    cards = db.get_all_cards()

    assert len(cards) == 1
    assert cards[0]["question"] == "What is 2+2?"
    assert cards[0]["answer"] == "4"
    assert cards[0]["source_file"] == "math.txt"

def test_get_due_cards(mock_db):
    current_time = time.time()

    # Due card
    db.add_card("Due?", "Yes", "test.txt")

    # Not due card
    conn = db.get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO cards (question, answer, source_file, next_review) VALUES (?, ?, ?, ?)",
        ("Not due?", "Yes", "test.txt", current_time + 10000)
    )
    conn.commit()
    conn.close()

    due_cards = db.get_due_cards(current_time)
    assert len(due_cards) == 1
    assert due_cards[0]["question"] == "Due?"

def test_update_card_review(mock_db):
    db.add_card("Q", "A", "test.txt")
    cards = db.get_all_cards()
    card_id = cards[0]["id"]

    db.update_card_review(card_id, 1, 6, 2.6, 1234567890.0)

    updated_card = db.get_card(card_id)
    assert updated_card["repetition"] == 1
    assert updated_card["interval"] == 6
    assert updated_card["ease_factor"] == 2.6
    assert updated_card["next_review"] == 1234567890.0

def test_update_card_mnemonic(mock_db):
    db.add_card("Q", "A", "test.txt")
    cards = db.get_all_cards()
    card_id = cards[0]["id"]

    db.update_card_mnemonic(card_id, "Test Mnemonic")

    updated_card = db.get_card(card_id)
    assert updated_card["mnemonic"] == "Test Mnemonic"
