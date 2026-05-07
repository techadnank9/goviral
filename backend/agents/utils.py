import json
import re

def extract_json(raw: str) -> dict:
    """Parse JSON from LLM output, handling markdown fences and trailing text."""
    text = raw.strip()
    # Extract from ```...``` fences
    fence = re.search(r"```(?:json|JSON)?\s*([\s\S]+?)```", text)
    if fence:
        text = fence.group(1).strip()
    # Find first { ... } block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[extract_json] failed to parse: {e}\nRaw (first 300): {raw[:300]}")
        raise
