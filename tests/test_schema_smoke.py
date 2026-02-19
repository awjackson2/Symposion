import json
from pathlib import Path

def test_message_schema_exists():
    p = Path("schemas/message.schema.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert "properties" in data and "sender" in data["properties"]
