# API AI Workshop -- Overview for Decision Makers

This document explains what the workshop is, why it matters, and how it runs.
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

This workshop teaches one practical skill:

> **How to treat AI output as untrusted input and verify it before using it.**

---

## What participants do

Participants work in teams. Each team receives a small Python file with
functions that already work -- they call an AI assistant and return the result.
The result contains deliberate mistakes.

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
  Fixture responses           OpenAPI specs,
  (identical for              log files, two
  every team)                 contract versions
```

Progress checks always use the same fixture responses, so every team faces
the same mistakes. Teams can also talk to a live model through `interact.py`
(Amazon Bedrock, using shared Workshop Studio credentials) to explore a level
before they write code.

---

## The four levels

Each level builds on the same idea.

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

### Level 2 -- Test design (25 points)

The AI proposes negative test cases. One test targets an endpoint that does
not exist. Teams must keep only tests that target real, documented operations.

**Real-world parallel:** a CI pipeline runs AI-generated tests. One test calls
a route that never existed, gets a 404, and the team debugs a ghost failure.

### Level 3 -- Incident diagnosis (30 points)

The AI produces two possible explanations for a production incident. Only one
is supported by the actual log file. Teams must select the diagnosis whose
evidence appears verbatim in the logs.

**Real-world parallel:** a team acts on an AI diagnosis that references a DNS
failure that never occurred.

### Level 4 -- Migration review (25 points)

The team receives two versions of the same API. The AI lists three breaking
changes. One is fabricated -- both versions define the field identically.
Teams must compare the two specs directly.

**Real-world parallel:** a team trusts an AI summary of an API upgrade. One
"change" did not happen. The client breaks in a way that takes days to trace.

---

## How progress checks work

```
Team runs:
  python score.py --team "Team Name"
            |
            v
  Automated checks (100 points total)
            |
            v
  +---------------------------+
  |  Progress page updates    |
  |  http://localhost:8081    |
  +---------------------------+
            |
            v
  report.html opens in browser
  showing every check pass / fail
  with a hint for each failure
```

Teams can run the checker as many times as they like. The progress page
auto-refreshes. A Getting Started guide lives at
`http://localhost:8081/guide`. Swagger pages at `/api/v1` and `/api/v2` are
reference only -- the API is not running.

---

## How a team works

```
Shared Workshop Studio environment
  (credentials for Bedrock activity scripts)
            |
            +-- one person in Studio VS Code (single-user)
            |
            +-- everyone else clones the team fork and edits locally

Each teammate
+--------------------------------------------+
|  workshop.py  (the only file they edit)    |
|  interact.py  (explore a level)            |
|  score.py     (check progress)             |
|  Browser: Guide tab + report.html          |
+--------------------------------------------+
```

Teams share one fork of the public repo and hand in that URL. They must not
open `reference_solution.py` if they want a genuine attempt.

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
| Format | Online setup session, then team work on the four levels |
| Group size | Teams of 2-4 |
| Prerequisites | Basic Python familiarity, no AI experience required |
| Environment | AWS Workshop Studio (shared). Dry-run window: Friday 21 August, 3:00 pm to Monday 24 August, 3:00 pm (Pacific) |
| Local editor | VS Code recommended if not using Studio VS Code (https://code.visualstudio.com/download) |
| Software | Python 3.10+, boto3 for interact.py |
| Facilitator effort | Share the join link, walk through setup, answer questions |

---

## The business case in one paragraph

AI coding assistants reduce the time to produce a first draft of almost any
technical artifact. They do not reduce the need for human judgment -- they
shift where that judgment is applied. This workshop gives teams a safe,
low-stakes environment to discover that gap themselves, develop a habit of
verification, and leave with a concrete technique for doing it. The lesson
generalises to every AI tool the team already uses.
