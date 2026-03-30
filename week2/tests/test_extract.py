import os
import json
import pytest
from unittest.mock import patch

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# --- Unit tests for extract_action_items_llm ---


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_empty_input(mock_chat):
    """Empty or whitespace-only input returns [] without calling LLM."""
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   \n\t  ") == []
    mock_chat.assert_not_called()


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_bullet_list(mock_chat):
    """Input with bullet lists; LLM returns extracted items."""
    text = """
    Meeting notes:
    - Set up database
    * Implement API extract endpoint
    • Write unit tests
    """
    mock_chat.return_value = {
        "message": {
            "content": json.dumps({"action_items": ["Set up database", "Implement API extract endpoint", "Write unit tests"]})
        }
    }
    items = extract_action_items_llm(text)
    assert items == ["Set up database", "Implement API extract endpoint", "Write unit tests"]
    mock_chat.assert_called_once()


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_keyword_prefixed(mock_chat):
    """Input with todo:, action:, next: prefixes."""
    text = """
    todo: Review pull request
    action: Deploy to staging
    next: Update documentation
    """
    mock_chat.return_value = {
        "message": {
            "content": json.dumps({"action_items": ["Review pull request", "Deploy to staging", "Update documentation"]})
        }
    }
    items = extract_action_items_llm(text)
    assert "Review pull request" in items
    assert "Deploy to staging" in items
    assert "Update documentation" in items
    mock_chat.assert_called_once()


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_numbered_list(mock_chat):
    """Input with numbered lists."""
    text = """
    1. Fix login bug
    2. Add validation
    3. Refactor auth module
    """
    mock_chat.return_value = {
        "message": {
            "content": json.dumps({"action_items": ["Fix login bug", "Add validation", "Refactor auth module"]})
        }
    }
    items = extract_action_items_llm(text)
    assert items == ["Fix login bug", "Add validation", "Refactor auth module"]
    mock_chat.assert_called_once()


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_no_action_items(mock_chat):
    """Input with no actionable content; LLM returns empty list."""
    text = "Just some meeting notes. No tasks here. Discussed the weather."
    mock_chat.return_value = {
        "message": {
            "content": json.dumps({"action_items": []})
        }
    }
    items = extract_action_items_llm(text)
    assert items == []
    mock_chat.assert_called_once()


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_fallback_on_error(mock_chat):
    """When LLM raises exception, fallback to heuristic extract_action_items."""
    text = """
    - Set up database
    * Write tests
    """
    mock_chat.side_effect = Exception("Ollama connection failed")
    items = extract_action_items_llm(text)
    assert "Set up database" in items
    assert "Write tests" in items
    mock_chat.assert_called_once()


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_malformed_json_fallback(mock_chat):
    """When LLM returns invalid JSON, fallback to heuristic extraction."""
    text = "- Fix bug\n* Add feature"
    mock_chat.return_value = {
        "message": {
            "content": "Sorry, I cannot parse that."
        }
    }
    items = extract_action_items_llm(text)
    assert "Fix bug" in items
    assert "Add feature" in items
