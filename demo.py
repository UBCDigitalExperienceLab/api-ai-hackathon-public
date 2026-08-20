import argparse
import importlib
import json

from api_hackathon.ai import BedrockFixtureAI, FixtureAI, OllamaAI
from api_hackathon.artifacts import load_json, load_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all four hackathon levels.")
    parser.add_argument("--solution", action="store_true")
    parser.add_argument("--ollama", action="store_true")
    parser.add_argument("--bedrock", action="store_true")
    args = parser.parse_args()

    module = importlib.import_module(
        "api_hackathon.reference_solution" if args.solution else "api_hackathon.workshop"
    )
    if args.ollama:
        ai = OllamaAI()
    elif args.bedrock:
        ai = BedrockFixtureAI()
    else:
        ai = FixtureAI()
    v1, v2 = load_json("openapi-v1.json"), load_json("openapi-v2.json")

    outputs = {
        "level_1_contract_review": module.review_contract(v1, ai),
        "level_2_negative_tests": module.design_negative_tests(v1, ai),
        "level_3_incident": module.diagnose_incident(load_text("incident.log"), ai),
        "level_4_migration": module.review_migration(v1, v2, ai),
    }
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
