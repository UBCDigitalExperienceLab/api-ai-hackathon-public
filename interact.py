"""Interactive AI assistant for the API Hackathon.

Run:
    python interact.py

Pick a level, see which functions you have started, watch the AI
stream its findings, then ask follow-up questions. Type a level
number (1-4) at any time to jump to another level.
"""

import importlib
import json
import sys

import boto3

from api_hackathon.artifacts import load_json, load_text

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

LEVELS = [
    (1, "Contract review",   20, "contract_review",   "L1"),
    (2, "Negative tests",    25, "negative_tests",     "L2"),
    (3, "Safety + incident", 30, "incident_diagnosis", "L3"),
    (4, "Migration review",  25, "migration_review",   "L4"),
]

# Functions that belong to each level and their unmodified default snippets.
# If the default snippet is still present in the function body, it has not been started.
LEVEL_FUNCTIONS = {
    1: [
        ("review_contract",       'return ai.ask("contract_review", spec)'),
    ],
    2: [
        ("design_negative_tests", 'return ai.ask("negative_tests", spec)'),
    ],
    3: [
        ("sanitize_for_ai",       "return payload"),
        ("diagnose_incident",     'return ai.ask("incident_diagnosis", logs)[0]'),
    ],
    4: [
        ("review_migration",      'return ai.ask("migration_review", {"v1": v1, "v2": v2})'),
    ],
}

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


def get_implementation_status():
    """
    Read workshop.py and check which functions still contain their default
    placeholder. Returns {func_name: bool} where True means started.
    """
    try:
        with open("api_hackathon/workshop.py") as f:
            source = f.read()
    except OSError:
        return {}

    status = {}
    for funcs in LEVEL_FUNCTIONS.values():
        for func_name, default_snippet in funcs:
            func_start = source.find(f"def {func_name}(")
            if func_start == -1:
                status[func_name] = False
                continue
            next_func = source.find("\ndef ", func_start + 1)
            func_body = source[func_start:next_func] if next_func != -1 else source[func_start:]
            status[func_name] = default_snippet not in func_body
    return status


def show_menu(impl_status):
    started_total = sum(1 for v in impl_status.values() if v)
    total_funcs = len(impl_status)
    print(f"\n{'═' * 60}")
    print("   API AI Hackathon — Interactive Assistant")
    print(f"   Functions started: {started_total}/{total_funcs}")
    print(f"{'═' * 60}")
    print("\n   Which level do you want to work on?\n")
    for num, name, max_pts, _, _ in LEVELS:
        funcs = LEVEL_FUNCTIONS[num]
        started = sum(1 for fn, _ in funcs if impl_status.get(fn, False))
        total = len(funcs)
        if started == 0:
            marker = "    "
        elif started == total:
            marker = "done"
        else:
            marker = "part"
        print(f"     {num}  {name:<25}  [{marker}]  {started}/{total} function(s) started")
    print(f"\n     q  Quit\n")


def show_level_status(impl_status, level_num):
    """Print per-function start status for a level."""
    funcs = LEVEL_FUNCTIONS[level_num]
    print()
    for func_name, _ in funcs:
        started = impl_status.get(func_name, False)
        mark = "started    " if started else "not started"
        print(f"  [{mark}]  {func_name}")
    print()


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
        return "contract_review", f"OpenAPI v1 spec:\n{json.dumps(v1, indent=2)}", fixtures["contract_review"]
    if level_num == 2:
        return "negative_tests", f"OpenAPI v1 spec:\n{json.dumps(v1, indent=2)}", fixtures["negative_tests"]
    if level_num == 3:
        logs = load_text("incident.log")
        return "incident_diagnosis", f"Incident log:\n{logs}", fixtures["incident_diagnosis"]
    if level_num == 4:
        v2 = load_json("openapi-v2.json")
        return "migration_review", (
            f"API v1 spec:\n{json.dumps(v1, indent=2)}\n\nAPI v2 spec:\n{json.dumps(v2, indent=2)}"
        ), fixtures["migration_review"]


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
    print(f"\n{'─' * 60}")
    print(f"  Level {level_num} — {level_name}")
    print(f"{'─' * 60}\n")
    return stream(client, system, messages)


def chat_loop(client, level_num, level_name, source_data, fixture_findings):
    """
    Free-form chat about a level.

    Returns:
      None       go back to main menu
      int (1-4)  switch directly to that level
    """
    fixture_json = json.dumps(fixture_findings, indent=2)
    system = (
        f"You are a concise coding assistant for an API hackathon. "
        f"The hackathon has 4 levels the participant can access in any order:\n"
        f"  Level 1 — Contract review (20 pts)\n"
        f"  Level 2 — Negative tests (25 pts)\n"
        f"  Level 3 — Safety + incident (30 pts)\n"
        f"  Level 4 — Migration review (25 pts)\n\n"
        f"The participant is currently on Level {level_num}: {level_name}. "
        f"They can type a level number (1-4) at any time to switch levels.\n\n"
        f"The AI produced these findings for Level {level_num} (some may be hallucinations):\n{fixture_json}\n\n"
        f"The authoritative source data is:\n{source_data}\n\n"
        "Help the developer understand the findings, spot hallucinations, and write "
        "Python verification code for workshop.py. Be brief and practical. "
        "Never directly name which item is the hallucination — guide them to find it themselves."
    )
    conversation = []

    print(f"\n{'─' * 60}")
    print("  Ask me anything about this level.")
    print("  Type a level number (1-4) to switch levels.")
    print("  Type 'menu' or 'done' to return to the main menu.")
    print(f"{'─' * 60}")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if not user_input:
            continue

        lower = user_input.lower()

        if lower in ("menu", "done", "exit", "quit"):
            return None

        if user_input in ("1", "2", "3", "4"):
            target = int(user_input)
            if target == level_num:
                print(f"  You are already on Level {level_num}.")
                continue
            return target

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


def run_level(client, level_num):
    """Show status and findings for a level, then start chat. Returns next destination."""
    _, level_name, _, _, _ = LEVELS[level_num - 1]
    print(f"\n  {LEVEL_DESCRIPTIONS[level_num]}")
    impl_status = get_implementation_status()
    show_level_status(impl_status, level_num)
    task_key, source_data, fixture_findings = load_level_data(level_num)
    show_findings(client, level_num, level_name, fixture_findings)
    return chat_loop(client, level_num, level_name, source_data, fixture_findings)


def main():
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    destination = "menu"

    while True:
        if destination is None or destination == "menu":
            impl_status = get_implementation_status()
            show_menu(impl_status)
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

            destination = int(choice)

        else:
            destination = run_level(client, destination)


if __name__ == "__main__":
    main()
