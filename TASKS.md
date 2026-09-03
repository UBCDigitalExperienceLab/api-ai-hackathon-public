# Workshop Tasks

Start with `README.md`. This file is optional extra detail for each level. It is the only level-by-level brief (the old `CHALLENGES.md` short card lived here).

AI output is untrusted input. Your job is not to produce more output; it is to make the output useful and defensible.

**Workflow:**
1. Start the progress page with `python scoreboard.py`, then open the Guide tab at `http://localhost:8081/guide`.
2. Run `python interact.py` to explore a level and ask follow-up questions.
3. Edit `api_hackathon/workshop.py` to add verification logic for that level.
4. Run `python score.py --team "Your team"` to check your progress.

Do not open `api_hackathon/reference_solution.py`. Work only in `workshop.py`.

---

## Level 1 - Filter Hallucinated Contract Findings (20 pts)

The AI returns 4 OpenAPI findings. One is made up -- it claims `DELETE /customers` is publicly accessible, but that path does not exist in the spec at all.

Keep only findings where:
1. The `path` and `method` actually exist in the spec
2. The `evidence_pointer` (a JSON Pointer like `/paths/~1orders/get`) resolves to a real location in the spec.
   Split the pointer on `/` first, then decode `~1` to `/` **inside that key**.
   `/paths/~1orders/get` means `spec["paths"]["/orders"]["get"]`, not `//orders`.

**Tip:** open `http://localhost:8081/api/v1` to browse the real spec in Swagger UI — it shows exactly which paths and methods exist. The API is not running, so "Try it out" won't work; use the spec as a reference only.

**Starter code behaviour:** returns all 4 findings including the hallucination.

---

## Level 2 - Filter Hallucinated Negative Tests (25 pts)

The AI proposes 4 negative test cases. One targets a route that does not exist in v1.

Keep only test cases where:
1. The `path` and `method` exist in the spec
2. The `expected_status` is one of `400`, `401`, `403`, `404`, `409`, or `422`
3. Every case has the required fields: `name`, `method`, `path`, `input`, `expected_status`

**Tip:** open `http://localhost:8081/api/v1` to see which routes exist before deciding which test cases are targeting real endpoints. The API is not running, so "Try it out" won't work; use the spec as a reference only.

**Starter code behaviour:** returns all 4 tests including the invented one.

---

## Level 3 - Incident Diagnosis (30 pts)

The AI returns 2 candidate diagnoses for a production incident. One has evidence that appears
verbatim in `incident.log`. The other references log lines that do not exist anywhere in the file.

Return only the diagnosis where every item in its `evidence` array appears literally in the log text.

**Starter code behaviour:** blindly picks `[0]` from the AI diagnosis list, which is the unsupported DNS claim.

---

## Level 4 - Filter Hallucinated Breaking Changes (25 pts)

The AI reports 3 breaking changes between v1 and v2. One is invented -- it claims a field changed
type, but both specs define it identically.

Verify each claimed change by diffing the two specs directly:
- `operation_removed`: operation exists in v1, gone in v2 -- keep it
- `parameter_became_required`: parameter is optional in v1, required in v2 -- keep it
- `schema_changed`: schemas must actually differ between v1 and v2 -- if they are identical, reject the claim

**Tip:** open `http://localhost:8081/api/v1` and `http://localhost:8081/api/v2` side by side to visually spot what changed before writing the diff logic. The API is not running, so "Try it out" won't work; use the specs as a reference only.

**Starter code behaviour:** returns all 3 changes including the false one.

---

## The Unifying Theme

Every level follows the same pattern: AI produces output, your code verifies it against deterministic
evidence, filter out the unverifiable claims. The fixture AI is fixed; the verification logic is what
teams write and what the progress checks evaluate.

---

## Five-Minute Demonstration

1. Show one unreliable baseline result
2. Explain your verification approach
3. Run the progress check
4. Show one AI mistake your code catches
5. State where this pattern could help in daily API work
