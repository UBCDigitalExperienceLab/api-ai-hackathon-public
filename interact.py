"""Interactive AI assistant for the API Hackathon.

Run:
    python interact.py

Pick a level, watch the AI stream its findings, then ask follow-up
questions about that level before moving on to workshop.py.
"""

import json
import sys

import boto3

from api_hackathon.artifacts import load_json, load_text

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

LEVELS = [
    (1, "Contract review",   20, "contract_review"),
    (2, "Negative tests",    25, "negative_tests"),
    (3, "Safety + incident", 30, "incident_diagnosis"),
    (4, "Migration review",  25, "migration_review"),
]

LEVEL_DESCRIPTIONS = {
    1: (
        "The AI reviewed the OpenAPI v1 spec and reported potential problems. "
        "Some findings may point to endpoints or locations that do not exist. "
        "Your job: keep only findings whose path, method, and evidence_pointer "
        "resolve to real locations in the spec."
    ),
    2: (
        "The AI proposed negative test cases for the API. "
        "Some tests target endpoints that do not exist. "
        "Your job: keep only tests whose path and method exist in the spec, "
        "with a valid client-error status code."
    ),
    3: (
        "The AI diagnosed a production incident from logs and produced two candidates. "
        "Only one candidate is supported by the actual log file. "
        "Your job: select the diagnosis whose every evidence fragment appears verbatim in the logs."
    ),
    4: (
        "The AI compared API v1 and v2 and listed breaking changes. "
        "One change is fabricated — it claims a schema changed when both versions are identical. "
        "Your job: verify each claim by comparing the two specs directly."
    ),
}


def stream(client, system_text, messages):
    """Stream a Bedrock response and return the full text."""
    response = client.converse_stream(
        modelId=MODEL_ID,
        system=[{"text": system_text}],
        messages=messages,
    )
    full_text = ""
    for event in response["stream"]:
        if "contentBlockDelta" in event:
            chunk = event["contentBlockDelta"]["delta"].get("text", "")
            print(chunk, end="", flush=True)
            full_text += chunk
    print()
    return full_text


def load_level_data(level_num):
    """Return (task_key, source_data_summary, fixture_findings) for a level."""
    v1 = load_json("openapi-v1.json")
    fixtures = load_json("ai-fixtures.json")

    if level_num == 1:
        return (
            "contract_review",
            f"OpenAPI v1 spec:\n{json.dumps(v1, indent=2)}",
            fixtures["contract_review"],
        )
    if level_num == 2:
        return (
            "negative_tests",
            f"OpenAPI v1 spec:\n{json.dumps(v1, indent=2)}",
            fixtures["negative_tests"],
        )
    if level_num == 3:
        logs = load_text("incident.log")
        return (
            "incident_diagnosis",
            f"Incident log:\n{logs}",
            fixtures["incident_diagnosis"],
        )
    if level_num == 4:
        v2 = load_json("openapi-v2.json")
        return (
            "migration_review",
            f"API v1 spec:\n{json.dumps(v1, indent=2)}\n\nAPI v2 spec:\n{json.dumps(v2, indent=2)}",
            fixtures["migration_review"],
        )


def show_findings(client, level_num, level_name, fixture_findings):
    """Stream fixture findings via a real Bedrock call."""
    fixture_json = json.dumps(fixture_findings, indent=2)
    system = (
        "You are an AI API analysis assistant presenting your findings to a developer. "
        "You have just completed your analysis and produced the results below. "
        "Introduce what you found in one or two sentences, then show the full JSON. "
        "Do not add commentary after the JSON.\n\n"
        f"Your findings:\n{fixture_json}"
    )
    messages = [{
        "role": "user",
        "content": [{"text": f"Show me your analysis for Level {level_num}: {level_name}."}],
    }]

    print(f"\n{'─' * 56}")
    print(f"  Level {level_num} — {level_name}")
    print(f"{'─' * 56}\n")
    return stream(client, system, messages)


def chat_loop(client, level_num, level_name, source_data, fixture_findings):
    """Free-form chat about a level."""
    fixture_json = json.dumps(fixture_findings, indent=2)
    system = (
        f"You are a concise coding assistant helping a developer with Level {level_num} "
        f"of an API hackathon: {level_name}.\n\n"
        f"The AI produced these findings (some may be hallucinations):\n{fixture_json}\n\n"
        f"The authoritative source data is:\n{source_data}\n\n"
        "Help the developer understand the findings, spot hallucinations, and write "
        "Python verification code for workshop.py. Be brief and practical. "
        "Never reveal which specific item is the hallucination directly — "
        "guide them to discover it by checking the source data themselves."
    )

    conversation = []

    print(f"\n{'─' * 56}")
    print("  Ask me anything about this level.")
    print("  Type 'done' to return to the level menu.")
    print(f"{'─' * 56}")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("done", "exit", "quit"):
            break

        conversation.append({
            "role": "user",
            "content": [{"text": user_input}],
        })

        print("\nAI: ", end="", flush=True)
        reply = stream(client, system, conversation)

        conversation.append({
            "role": "assistant",
            "content": [{"text": reply}],
        })


def show_menu():
    print(f"\n{'═' * 56}")
    print("   API AI Hackathon — Interactive Assistant")
    print(f"{'═' * 56}")
    print("\n   Which level do you want to work on?\n")
    for num, name, pts, _ in LEVELS:
        print(f"     {num}  {name:<25} ({pts} pts)")
    print(f"\n     q  Quit")
    print()


def main():
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    while True:
        show_menu()
        try:
            choice = input("   Enter a number: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.\n")
            sys.exit(0)

        if choice in ("q", "quit", "exit"):
            print("\nGoodbye.\n")
            break

        if not choice.isdigit() or int(choice) not in range(1, 5):
            print("   Invalid choice. Enter 1, 2, 3, or 4.\n")
            continue

        level_num = int(choice)
        _, level_name, _, _ = LEVELS[level_num - 1]

        print(f"\n   {LEVEL_DESCRIPTIONS[level_num]}")

        task_key, source_data, fixture_findings = load_level_data(level_num)
        show_findings(client, level_num, level_name, fixture_findings)
        chat_loop(client, level_num, level_name, source_data, fixture_findings)


if __name__ == "__main__":
    main()
