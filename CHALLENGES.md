# Participant brief

AI output is untrusted input. Your job is not to produce more output; it is to make the output useful and defensible.

Edit `api_hackathon/workshop.py`. Run `python score.py --team "Your team"` after each level.

## Level 1 — Contract reviewer

The model reports OpenAPI risks, including one invented endpoint. Return only findings whose operation and evidence pointer exist in the contract.

## Level 2 — Negative-test designer

The model proposes negative tests, including one for an endpoint that does not exist. Keep valid operations, safe failure statuses, and a consistent test-case structure.

## Level 3 — Safety and incident response

Redact tokens, email addresses, and instruction-like payload text before it reaches AI. Then select an incident diagnosis only when every cited evidence fragment appears in the logs.

## Level 4 — Migration reviewer

Compare API v1 and v2. Verify removed operations and newly required parameters. Reject claims where the underlying schemas are unchanged.

## Five-minute demonstration

1. Show one unreliable baseline result.
2. Explain your verification approach.
3. Run the scorer.
4. Show one AI mistake your code catches.
5. State where this pattern could help in daily API work.
