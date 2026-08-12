# API AI Hackathon -- Overview for Decision Makers

This document explains what the hackathon is, why it matters, and how it runs.
No technical background is needed to read this.

---

## The problem it solves

AI tools are becoming common in software teams. Developers use them to review
APIs, write tests, analyse incidents, and compare versions. The problem is that
AI regularly makes things up -- it invents endpoints that do not exist, cites
evidence that is not in the logs, and fabricates changes between two versions
of a system.

If a developer trusts that output without checking it, the team acts on false
information.

This hackathon teaches one practical skill:

> **How to treat AI output as untrusted input and verify it before using it.**

---

## What participants do

Participants work in teams of two or three. Each team receives a small Python
file with five short functions. Each function already works -- it calls an AI
assistant and returns the result. The result contains deliberate mistakes.

The team's job is to add verification logic so that only provably correct
results are returned.

```
+------------------+        +-------------------+        +------------------+
|                  |        |                   |        |                  |
|   AI assistant   | -----> |  your code checks | -----> |  verified output |
|  (may hallucinate|        |  against real data|        |  safe to use     |
|   1-2 items)     |        |                   |        |                  |
+------------------+        +-------------------+        +------------------+
        ^                           ^
        |                           |
  Pre-written fixture         OpenAPI specs,
  responses (identical        log files, two
  for every team)             contract versions
```

No one connects to a real AI service. The AI responses are pre-written files
stored on each laptop. This means every team faces exactly the same mistakes,
results are reproducible, and no internet or API key is needed.

---

## The four levels

Each level takes about 15-20 minutes and builds on the same idea.

```
+-------+   +-------+   +-------+   +-------+
|       |   |       |   |       |   |       |
|  L1   |   |  L2   |   |  L3   |   |  L4   |
|       |   |       |   |       |   |       |
| Find  |   | Write |   | Verify|   | Diff  |
| real  |   | valid |   | incid.|   | two   |
| API   |   | tests |   | diagn.|   | API   |
| risks |   |       |   | vs log|   | vers. |
|  20pt |   |  25pt |   |  30pt |   |  25pt |
+-------+   +-------+   +-------+   +-------+
               Harder each level ---->
```

### Level 1 -- Contract review (20 points)

The AI scans an API specification and reports potential problems. One report
is invented -- it refers to an endpoint that does not exist. Teams must remove
it and keep only the findings that point to real locations in the spec.

**Real-world parallel:** a developer asks an AI to review an OpenAPI file
before publishing it. The AI flags a security gap that does not actually exist.
If deployed, the team wastes time investigating a ghost problem.

### Level 2 -- Test design (25 points)

The AI proposes negative test cases (what happens when you send bad input).
One test targets an endpoint that does not exist in the API. Teams must filter
out tests for non-existent routes and keep only the ones that target real,
documented operations.

**Real-world parallel:** a CI pipeline runs AI-generated tests. One test calls
a route that never existed, gets a 404, and the team spends an hour debugging
why the "endpoint broke."

### Level 3 -- Incident diagnosis (30 points)

The AI produces two possible explanations for a production incident. Only one
is supported by the actual log file. Teams must select the diagnosis whose
evidence appears verbatim in the logs.

**Real-world parallel:** a team acts on an AI diagnosis that references a DNS
failure that never occurred. The real cause -- a database pool exhaustion -- is
buried in the logs and takes days to find because the team trusted the wrong
candidate.

### Level 4 -- Migration review (25 points)

The team receives two versions of the same API. The AI lists three breaking
changes. One is fabricated -- it claims a field changed type, but both versions
define it identically. Teams must compare the two specs directly to confirm or
reject each claim.

**Real-world parallel:** a team is upgrading a client to a new API version.
They trust an AI summary of what changed. One "change" did not happen. The
client breaks in a way that takes days to trace back to a false report.

---

## How scoring works

```
Team runs:
  python score.py --team "Team Name"
            |
            v
  Automated checks (100 points total)
            |
            v
  +---------------------------+
  |  Scoreboard updates live  |  <-- visible on screen for the whole room
  |  http://localhost:8080    |
  +---------------------------+
            |
            v
  report.html opens in browser
  showing every check pass / fail
  with a hint for each failure
```

Teams can run the scorer as many times as they like. The scoreboard shows
the latest score for each team and auto-refreshes every five seconds.

There is also a visual HTML report for each run that shows exactly which
checks passed and which failed, with a short explanation of what went wrong.

---

## What the room looks like during the event

```
Facilitator screen (projected)
+--------------------------------------------+
|  API Hackathon Scoreboard                  |
|                                            |
|  # | Team        | Score | L1 L2 L3 L4    |
|  1 | Team Alpha  |  85   | 20 25 20 20    |
|  2 | Team Beta   |  70   | 15 20 15 20    |
|  3 | Team Gamma  |  45   | 10 15 10 10    |
|                                            |
|  (click any row for per-check detail)      |
|  (refreshes every 5 seconds)               |
+--------------------------------------------+

Each team's laptop
+--------------------------------------------+
|  workshop.py  (the only file they edit)    |
|                                            |
|  Terminal: python score.py --team "Alpha"  |
|                                            |
|  Browser: report.html                      |
|  showing green / red for each check        |
+--------------------------------------------+
```

---

## What participants walk away with

1. A concrete mental model for why AI output needs verification, not just
   review.
2. A reusable pattern -- check AI claims against authoritative source data
   before acting on them -- that applies to any language or tool.
3. Practical experience with OpenAPI structure, log analysis, and contract
   diffing, which are everyday API engineering skills.
4. Code they wrote themselves that they can adapt to their own pipelines.

---

## Logistics

| Item | Detail |
|---|---|
| Duration | 3 hours (see README for a suggested minute-by-minute agenda) |
| Group size | 8 to 30 participants, teams of 2-3 |
| Prerequisites | Basic Python familiarity, no AI experience required |
| Setup | Python 3.10 or later, no extra packages, no internet required |
| Facilitator effort | Run three commands, then observe and prompt discussion |

---

## The business case in one paragraph

AI coding assistants reduce the time to produce a first draft of almost any
technical artifact. They do not reduce the need for human judgment -- they
shift where that judgment is applied. This hackathon gives teams a safe,
low-stakes environment to discover that gap themselves, develop a habit of
verification, and leave with a concrete technique for doing it. The lesson
takes three hours and generalises to every AI tool the team already uses.
