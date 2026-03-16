# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: Zeyuan Pu
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
Write a function named extract_action_items_llm() that utilized Ollama to extract actions from a input text. It should perform the same feature as extract_action_items().
```

Generated Code Snippets:
```python
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
```

### Exercise 2: Add Unit Tests
Prompt: 
```
❯ Add unit test for the new added extract_action_items_llm() in text_extract.py 
```

Generated Code Snippets:
```python
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
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
TODO
```

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
TODO
```

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
TODO
```

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 