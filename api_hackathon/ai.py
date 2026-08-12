import json
import urllib.request

from .artifacts import load_json


class BedrockFixtureAI:
    """Real Bedrock API call seeded with fixture findings so hallucinations are preserved."""

    def __init__(self, model_id: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"):
        import boto3
        self.client = boto3.client("bedrock-runtime", region_name="us-east-1")
        self.model_id = model_id
        self.fixtures = load_json("ai-fixtures.json")

    def ask(self, task: str, _context) -> list[dict]:
        fixture_json = json.dumps(self.fixtures[task])
        response = self.client.converse(
            modelId=self.model_id,
            system=[{
                "text": (
                    "You are an API analysis assistant. "
                    "You have already completed this analysis and produced the following findings. "
                    f"Return them exactly as a JSON array with no changes:\n{fixture_json}"
                )
            }],
            messages=[{
                "role": "user",
                "content": [{"text": f"Return your findings for task: {task}"}]
            }]
        )
        text = response["output"]["message"]["content"][0]["text"]
        start, end = text.find("["), text.rfind("]") + 1
        return json.loads(text[start:end])


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
