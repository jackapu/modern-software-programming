import os
import pytest

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


# --- Tests for extract_action_items_llm() ---


def test_llm_extract_bullet_list():
    """LLM should extract action items from bullet-pointed text."""
    text = "- Buy groceries\n- Fix the login bug\n- Deploy to staging"
    items = extract_action_items_llm(text)
    assert len(items) >= 2
    joined = " ".join(items).lower()
    assert "groceries" in joined
    assert "login" in joined or "bug" in joined


def test_llm_extract_keyword_prefixed():
    """LLM should extract action items from keyword-prefixed lines."""
    text = "TODO: Write unit tests\nAction: Review the pull request\nNext: Update documentation"
    items = extract_action_items_llm(text)
    assert len(items) >= 2
    joined = " ".join(items).lower()
    assert "test" in joined
    assert "review" in joined or "pull request" in joined


def test_llm_extract_empty_input():
    """LLM should return an empty list for empty input."""
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   ") == []


def test_llm_extract_no_action_items():
    """LLM should return an empty or minimal list for text with no clear actions."""
    text = "The weather is nice today. I had a great lunch."
    items = extract_action_items_llm(text)
    assert isinstance(items, list)
    assert len(items) == 0


def test_llm_extract_checkbox_format():
    """LLM should extract action items from checkbox-style notes."""
    text = "- [ ] Set up database\n- [ ] Write migration script\n- [x] Create project repo"
    items = extract_action_items_llm(text)
    assert len(items) >= 1
    joined = " ".join(items).lower()
    assert "database" in joined or "migration" in joined
