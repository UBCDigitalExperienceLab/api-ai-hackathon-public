# API AI Workshop

**Start here.** This README is the only entry point for the workshop. Open it first, then follow Quick start. Other markdown files are optional extras — you do not need them to begin.

A workshop for API practitioners who are new to AI.

Participants receive a working but unreliable implementation in `api_hackathon/workshop.py`. They improve it across four levels by filtering unsupported AI output and verifying recommendations against deterministic evidence.

The default `FixtureAI` uses pre-generated responses, including deliberate hallucinations. Scoring always uses those fixtures so every team gets the same inputs. Amazon Bedrock is optional for exploration via `interact.py`.

**Dry-run participants:** do not open or use `api_hackathon/reference_solution.py`. It is a facilitator file. Looking at it will spoil the workshop if you want a genuine experience later.

## First 10 minutes

Do these in order. When you finish, you have a running progress page and a first score.

1. Confirm Python 3.10+ (`python --version`). Install it first if it is missing.
2. Install dependencies with `pip install boto3`.
3. From the repo root, run `python scoreboard.py` and leave that terminal open.
4. Open `http://localhost:8081/guide` — that is the on-screen activity script.
5. In a second terminal, run `python score.py --team "Your Team" --open`. You should see about 55/100 on the unmodified starter.
6. Optional: run `python interact.py` if you have Workshop Studio credentials. Scoring does not need it.

You are ready to edit Level 1 in `api_hackathon/workshop.py`.

## Quick start

Requires Python 3.10+. `interact.py` also needs `boto3` and Workshop Studio credentials.

```powershell
pip install boto3
python scoreboard.py
```

Then, with Studio credentials set in the same terminal:

```powershell
python interact.py
python score.py --team "Team One" --open
```

| URL | What you get |
|---|---|
| `http://localhost:8081/guide` | Getting Started — activity walkthrough (Guide tab) |
| `http://localhost:8081` | Progress page — click any row for per-check detail |
| `http://localhost:8081/api/v1` | Swagger UI for the Orders API v1 spec (reference only) |
| `http://localhost:8081/api/v2` | Swagger UI for the Orders API v2 spec (reference only) |

The Orders API is not running. Use Swagger to see which endpoints exist. "Try it out" will return 404.

`score.py` writes `report.html` after every run. Pass `--open` to open it automatically.

## Dry-run setup

1. Join Workshop Studio with the event join link (no access code to type).
2. The AWS environment is available **Friday 21 August, 3:00 pm to Monday 24 August, 3:00 pm (Pacific)**. Studio CLI credentials last for that same window.
3. One teammate forks this repo. Everyone clones **the fork**, not this upstream repo. Replace `YOUR-ORG` with the fork owner's GitHub name, or copy the URL from the fork's green **Code** button.
4. Studio VS Code is single-user. Edit on your own machine if needed. Download VS Code from https://code.visualstudio.com/download if you do not have it.
5. Share Studio CLI credentials so everyone can run activity scripts that call Bedrock (`interact.py`). Do not commit credentials.
6. On a personal machine you do not need `source /environment/.venv/bin/activate` — that path exists only in Studio. Use Python 3.10+ and `pip install boto3`.

Work on `main`. Push only `api_hackathon/workshop.py`.

## How to work each level

1. Run `python interact.py` and pick a level. Ask follow-up questions; the assistant will not give away the answer.
2. Use the Guide tab at `http://localhost:8081/guide` as the on-screen activity script.
3. Edit the matching function in `api_hackathon/workshop.py`.
4. Run `python score.py --team "Your Team"` to check progress.

Facilitators review the latest `workshop.py` on the team fork.

```powershell
python score.py --team "Team Alpha" --file "path\to\their\workshop.py"
```

Or collect files into `submissions/<Team Name>/workshop.py` and run `python score.py --all`.

## Four levels

| Level | Task | Points |
|---|---|---:|
| 1 | Verify AI-generated OpenAPI findings and remove hallucinations | 20 |
| 2 | Turn AI test ideas into valid negative API tests | 25 |
| 3 | Verify a production incident diagnosis against the actual log file | 30 |
| 4 | Verify breaking API changes across two contracts | 25 |

Teams edit only `api_hackathon/workshop.py`. Level-by-level checks live in `TASKS.md` if you want more detail after you start.

## Other documents (optional)

Skip these until you have scored at least once. They are not a second starting point.

| File | Who it is for |
|---|---|
| `TASKS.md` | Extra tips and the exact keep/drop rules for each level |
| `CHALLENGES.md` | A short restatement of the same four levels |
| `OVERVIEW.md` | Decision-makers who want the workshop rationale |

## Project map

```text
README.md                           start here
api_hackathon/workshop.py           participant implementation — the only file to edit
api_hackathon/ai.py                 fixture AI + Bedrock + optional Ollama adapters
data/                               synthetic specs, logs, and AI responses
interact.py                         interactive assistant (Bedrock)
score.py                            progress checks (always uses FixtureAI)
scoreboard.py                       local progress page + Guide + Swagger (port 8081)
demo.py                             run every level and print raw AI output
TASKS.md                            optional level descriptions and tips
docs/online-session-slides.pdf      dry-run session slides
```

All artifacts are synthetic. Do not replace them with production payloads, credentials, or confidential logs during the event.
