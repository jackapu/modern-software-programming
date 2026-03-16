from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str, model: str = "llama3.1:8b") -> List[str]:
    """Extract action items from text using an Ollama LLM with structured JSON output."""
    if not text or not text.strip():
        return []

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract action items from text. "
                    'Respond with a JSON object: {"action_items": ["item1", "item2"]}. '
                    'If none, respond with: {"action_items": []}.'
                ),
            },
            {
                "role": "user",
                "content": f"Extract action items from this text:\n\n{text}",
            },
        ],
        format="json",
    )

    # Parse the structured JSON response
    raw = response.message.content
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []

    # Handle various response formats: [...], {"action_items": [...]}, or {key: str, ...}
    if isinstance(parsed, list):
        items = parsed
    elif isinstance(parsed, dict):
        # First try to find a list value (e.g. {"action_items": [...]})
        list_val = next((v for v in parsed.values() if isinstance(v, list)), None)
        if list_val is not None:
            items = list_val
        else:
            # Fallback: collect all string values (e.g. {"task1": "Buy groceries", ...})
            items = [v for v in parsed.values() if isinstance(v, str)]
    else:
        return []

    # Return only non-empty string items, deduplicated
    seen: set[str] = set()
    unique: List[str] = []
    for item in items:
        if isinstance(item, str) and item.strip():
            lowered = item.strip().lower()
            if lowered not in seen:
                seen.add(lowered)
                unique.append(item.strip())
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
