from dataclasses import dataclass
import json

@dataclass
class ProgressEvent:
    stage: str
    message: str
    pct: int

def format_sse(event_type: str, data: dict | str) -> str:
    payload = data if isinstance(data, str) else json.dumps(data)
    return f"event: {event_type}\ndata: {payload}\n\n"
