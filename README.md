# API AI Hackathon

A compact, account-free hackathon for API practitioners who are new to AI.

Participants receive a working but unreliable implementation in `api_hackathon/workshop.py`. They improve it across four levels by filtering unsupported AI output, protecting API data, and verifying recommendations against deterministic evidence.

The default `FixtureAI` uses pre-generated responses, including deliberate hallucinations. No network, API key, or paid account is required. Ollama is optional.

## Quick start

Requires Python 3.10+ and no third-party packages.

```powershell
python demo.py
python score.py --team "Team One"
python scoreboard.py
```

| URL | What you get |
|---|---|
| `http://localhost:8080` | Live scoreboard — click any row to expand per-check detail |
| `http://localhost:8080/api/v1` | Swagger UI for the Orders API v1 spec |
| `http://localhost:8080/api/v2` | Swagger UI for the Orders API v2 spec |

`score.py` also writes `report.html` in the project folder after every run — open it in any browser for a visual breakdown of every check. Pass `--open` to open it automatically.

```powershell
python score.py --team "Team One" --open
```

### Score every team (facilitator)

Collect each team's `workshop.py` into `submissions/<Team Name>/`:

```text
submissions/
  Team Alpha/workshop.py
  Team Beta/workshop.py
```

Then score them all onto the shared board:

```powershell
python score.py --all
python scoreboard.py
```

That updates `scoreboard.json` for every team folder and writes per-team reports under `reports/`. The live page at http://localhost:8080 shows the full ranking for the room.

Score one submission file without copying into the kit:

```powershell
python score.py --team "Team Alpha" --file "path\to\their\workshop.py"
```

Run the solved version:

```powershell
python demo.py --solution
python score.py --team "Reference" --impl solution
python -m unittest discover
```

Optional real AI via Amazon Bedrock (requires AWS credentials):

```powershell
python demo.py --bedrock
```

Optional local AI:

```powershell
ollama pull llama3.2
python demo.py --ollama
```

The scored workshop remains fixture-based so every team receives identical inputs.

## Four levels

| Level | Task | Points |
|---|---|---:|
| 1 | Verify AI-generated OpenAPI findings and remove hallucinations | 20 |
| 2 | Turn AI test ideas into valid negative API tests | 25 |
| 3 | Verify a production incident diagnosis against the actual log file | 30 |
| 4 | Verify breaking API changes across two contracts | 25 |

Teams edit only `api_hackathon/workshop.py`. The reference is in `api_hackathon/reference_solution.py`.

## Suggested 3-hour session

- 25 min: AI basics, context, hallucinations, structured output, data safety
- 20 min: guided Level 1 walkthrough
- 80 min: team levels
- 20 min: adversarial peer review
- 25 min: demonstrations and recognition
- 10 min: lessons and reusable workplace practices

Use the scoreboard for energy, not speed. Give recognition for strongest verification, best AI-failure detection, most reusable workflow, and clearest demonstration.

## Project map

```text
api_hackathon/workshop.py           participant implementation
api_hackathon/reference_solution.py solved example
api_hackathon/ai.py                 fixture AI + Bedrock + optional Ollama adapters
data/                               synthetic specs, logs, and AI responses
submissions/                        one folder per team for batch scoring
score.py                            automated 100-point scoring (+ --all)
scoreboard.py                       dependency-free local scoreboard (refreshes every 10 s)
demo.py                             run every level and print raw AI output
interact.py                         interactive AI assistant with per-level chat (Bedrock)
tests/                              kit verification
```

All artifacts are synthetic. Do not replace them with production payloads, credentials, or confidential logs during the event.
