# Rubric: the four levels in plain language

**The idea:** an AI gives answers. Most are right and some are made up. In every level you write code that checks each AI answer against a trusted file, keeps the ones the file backs up, and drops the rest.

You edit only `api_hackathon/workshop.py`, which has one function per level. The starter code already scores about **55 out of 100**. You earn the rest by removing the wrong answers without losing the right ones.

Check your score any time:

```powershell
python score.py --team "Your Team" --open
```

## Words you will hear

| Term | What it means |
|---|---|
| API | A way for programs to talk to each other. Here: an online shop's Orders API. |
| Endpoint | One thing the API can do, like `GET /orders` (list the orders). |
| Spec (OpenAPI) | The official list of every endpoint. If it's not in the spec, it doesn't exist. |
| Status code | A number the API sends back. `404` means "not found", `401` means "not logged in". |
| Log file | A diary the server writes while it runs. It records what really happened. |
| Breaking change | A change in a new API version that stops old code from working. |

## At a glance

| Level | Trusted file | Keep an AI answer only if… | Points |
|---|---|---|---:|
| 1 | v1 spec | the endpoint and its pointer exist in the spec | 20 |
| 2 | v1 spec | the endpoint exists, the status code is allowed, and all fields are present | 25 |
| 3 | incident log | every line it quotes is in the log, word for word | 30 |
| 4 | v1 and v2 specs | the two specs really differ in that way | 25 |
| | | **Total** | **100** |

## Level 1: Check the AI's notes about the spec (20 points)

Function: `review_contract` · Trusted file: `data/openapi-v1.json` (or the API v1 tab)

- **The AI gives you:** a list of findings, which are comments about endpoints in the spec.
- **Your job:** keep a finding only if its endpoint (path and method) is in the spec and its evidence pointer leads to a real place in the spec.
- **Tip:** `~1` in a pointer means `/`, so `/paths/~1orders/get` points to the `/orders` GET endpoint.

| Check | Points |
|---|---:|
| Each real finding kept (3 × 5) | 15 |
| Made-up finding removed | 5 |

## Level 2: Check the AI's test plan (25 points)

Function: `design_negative_tests` · Trusted file: `data/openapi-v1.json` (or the API v1 tab)

- **The AI gives you:** negative tests, which are requests that should fail, each with the error code it should get back.
- **Your job:** keep a test only if its endpoint is in the spec, its `expected_status` is `400`, `401`, `403`, `404`, `409` or `422`, and it has every required field: `name`, `method`, `path`, `input`, `expected_status`.

| Check | Points |
|---|---:|
| Each valid test kept (3 × 5) | 15 |
| Made-up test removed | 5 |
| Every test has all required fields | 5 |

## Level 3: Check the AI's explanation of an outage (30 points)

Function: `diagnose_incident` · Trusted file: `data/incident.log`

- **The AI gives you:** possible causes of an outage, each with log lines it quotes as proof.
- **Your job:** return the one cause whose quoted lines all appear, word for word, in the log file.
- **Note:** the starter simply takes the first cause, which scores 0 here. That's why this level is worth the most.

| Check | Points |
|---|---:|
| You return the cause the log supports | 20 |
| All its quoted lines are really in the log | 10 |

## Level 4: Check what changed between two versions (25 points)

Function: `review_migration` · Trusted files: `data/openapi-v1.json` and `data/openapi-v2.json` (API v1 and v2 tabs)

- **The AI gives you:** a list of breaking changes between version 1 and version 2.
- **Your job:** compare the two specs yourself and keep a change only if the specs really differ in that way. There are three kinds of change:
  - `operation_removed`: an endpoint is in v1 but gone in v2.
  - `parameter_became_required`: a parameter is optional in v1 and required in v2.
  - `schema_changed`: a data shape is different in v1 and v2. If both are identical, drop the claim.

| Check | Points |
|---|---:|
| Each real change kept (2 × 10) | 20 |
| Made-up change removed | 5 |

## How to work each level

1. **Explore:** run `python interact.py`, pick the level and ask the AI tutor questions.
2. **Look:** open the trusted file, or its tab at `http://localhost:8081`.
3. **Edit:** add your check to the level's function in `workshop.py`.
4. **Score:** run `python score.py --team "Your Team" --open` and see what passes.

**When you get stuck,** look at the score report first, then ask the AI tutor, then open the "Stuck? Open a hint" section for that level in the README. And ask a facilitator.
