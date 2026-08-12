import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load_text(name: str) -> str:
    return (DATA / name).read_text(encoding="utf-8")
