import json
import urllib.request

from .artifacts import load_json


class FixtureAI:
    """Free, deterministic stand-in for an AI model."""

    def __init__(self):
        self.responses = load_json("ai-fixtures.json")

    def ask(self, task: str, _context) -> list[dict]:
        return self.responses[task]


class OllamaAI:
    """Optional local model provider; no paid account required."""

    def __init__(self, model: str = "llama3.2", url: str = "http://localhost:11434"):
        self.model, self.url = model, url

    def ask(self, task: str, context) -> list[dict]:
        prompt = (
            f"Complete the API engineering task '{task}'. Return only a JSON array. "
            f"Use only this evidence:\n{json.dumps(context)}"
        )
        body = json.dumps(
            {"model": self.model, "prompt": prompt, "stream": False, "format": "json"}
        ).encode()
        request = urllib.request.Request(
            f"{self.url}/api/generate", data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            model_response = json.load(response)["response"]
        parsed = json.loads(model_response)
        return parsed if isinstance(parsed, list) else parsed["results"]
