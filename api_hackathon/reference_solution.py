"""Facilitator reference. One clear solution, not the only valid solution.

Design principle used throughout
---------------------------------
Every function follows the same three-step pattern:
  1. Ask the AI for a list of candidates.
  2. Filter each candidate against authoritative, deterministic evidence.
  3. Return only what survives the filter.

The AI is treated as an untrusted source of suggestions, not as an authority.
"""

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _operation(spec, path, method):
    """Look up a single operation in an OpenAPI spec safely.

    Using .get() at every level means a missing path or method returns None
    instead of raising a KeyError. The callers rely on the None-is-falsy
    behaviour to reject any finding that references a non-existent operation.
    This is safer than try/except because it never masks unrelated errors.
    """
    return spec.get("paths", {}).get(path, {}).get(method)


def _pointer_exists(document, pointer: str) -> bool:
    """Resolve an OpenAPI JSON Pointer and report whether it points to
    something real in the document.

    JSON Pointers use "/" as a segment separator and encode a literal "/"
    inside a key as "~1" (and "~" as "~0"). For example:
        "/paths/~1orders/get"  resolves to  document["paths"]["/orders"]["get"]

    Wrapping the traversal in a broad except is deliberate: any traversal
    failure (wrong key type, list index out of range, not a container) means
    the pointer does not resolve, so we return False. Letting an exception
    propagate here would crash scoring for a badly formed AI response.
    """
    value = document
    try:
        for part in pointer.strip("/").split("/"):
            key = part.replace("~1", "/").replace("~0", "~")
            value = value[int(key)] if isinstance(value, list) else value[key]
        return True
    except (KeyError, IndexError, ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Level 1 -- Contract review
# ---------------------------------------------------------------------------

def review_contract(spec: dict, ai) -> list[dict]:
    """Keep only AI findings that are grounded in the OpenAPI contract.

    Two independent checks are required before a finding is kept:

    Check 1 -- operation exists (_operation):
        The AI included a finding for DELETE /customers. That path and method
        do not exist anywhere in the spec. Without this check, the hallucinated
        finding passes through unchanged.

    Check 2 -- evidence pointer resolves (_pointer_exists):
        The AI supplies an evidence_pointer for each finding so humans can
        inspect the exact location it is citing. If that pointer does not
        resolve to a real node in the document, the finding cannot be
        independently verified and should be dropped.

    Combining both checks means an AI response that guesses the right path
    but fabricates the evidence pointer is still rejected. Each claim must
    be independently verifiable from two angles.
    """
    return [
        finding
        for finding in ai.ask("contract_review", spec)
        if _operation(spec, finding["path"], finding["method"])
        and _pointer_exists(spec, finding["evidence_pointer"])
    ]


# ---------------------------------------------------------------------------
# Level 2 -- Negative test design
# ---------------------------------------------------------------------------

def design_negative_tests(spec: dict, ai) -> list[dict]:
    """Keep only test cases that target real operations and expect real errors.

    Check 1 -- operation exists (_operation):
        Same guard as Level 1. The AI proposed a test for DELETE /customers/c-1
        which does not appear in the spec. A test runner executing this case
        would get a 404 from a non-existent route and report a misleading
        failure.

    Check 2 -- expected_status is a known client-error code:
        The invented test expected a 204, which is a success code. Real
        negative tests should produce 4xx responses. Restricting to the
        set {400, 401, 403, 404, 409, 422} rejects both the invented case
        (204) and any AI response that expects a server error (5xx) from
        a test of bad input, which would be a test design flaw.

    Note: the required-fields check is handled by score.py. The solution
    is consistent because all cases returned by the AI fixture already carry
    the required fields; the filter does not need to re-check them.
    """
    allowed_statuses = {400, 401, 403, 404, 409, 422}
    return [
        case
        for case in ai.ask("negative_tests", spec)
        if _operation(spec, case["path"], case["method"])
        and case["expected_status"] in allowed_statuses
    ]


# ---------------------------------------------------------------------------
# Level 3 -- Incident diagnosis
# ---------------------------------------------------------------------------

def diagnose_incident(logs: str, ai) -> dict:
    """Select the one diagnosis whose every evidence fragment appears in logs.

    The AI returns multiple candidate diagnoses. Each carries an "evidence"
    list of exact log fragments that supposedly support the conclusion.

    The verification step checks every fragment with `item in logs`. This is
    a simple substring check: if the exact string does not appear anywhere in
    the log text, the candidate is untrustworthy and is dropped.

    Why require ALL evidence items (using `all`):
        A candidate that cites five log lines but invents one of them is still
        untrustworthy. Requiring every item to be present prevents partial
        matches from passing through.

    Why also check that evidence is non-empty:
        An AI could return a candidate with an empty evidence list. Empty
        evidence means the conclusion has no support at all. Requiring at
        least one evidence item avoids accepting a diagnosis by default.

    The safe fallback:
        If no candidate survives the filter, returning a structured dict
        with cause "Insufficient evidence" is better than raising an exception
        or returning None. The caller always receives a valid dict and can
        decide how to handle inconclusive results.
    """
    candidates = ai.ask("incident_diagnosis", logs)
    supported = [
        candidate
        for candidate in candidates
        if candidate["evidence"] and all(item in logs for item in candidate["evidence"])
    ]
    return supported[0] if supported else {"cause": "Insufficient evidence", "evidence": []}


# ---------------------------------------------------------------------------
# Level 4 -- Migration review
# ---------------------------------------------------------------------------

def review_migration(v1: dict, v2: dict, ai) -> list[dict]:
    """Keep only breaking changes that can be confirmed by diffing v1 and v2.

    The AI reports three change kinds. Each requires a different verification
    strategy because "breaking" means something different in each case.

    "operation_removed":
        A breaking change only if the operation existed in v1 AND is absent
        in v2. Checking both sides prevents accepting a claim that the
        operation was removed when it never existed in v1 to begin with.

    "parameter_became_required":
        A breaking change only if the parameter was truly optional (required
        absent or False) in v1 and truly required (required is True) in v2.
        Reading the actual "required" field from both specs prevents accepting
        a claim where the parameter was already required in v1, which would
        not be a new breaking change.

    "schema_changed":
        A breaking change only if the parameter's schema dict differs between
        versions. Direct dict equality comparison is reliable here because
        JSON schemas are plain dicts. The AI claimed orderId changed from
        integer to string, but both versions define it as {"type": "string"},
        so the schemas are equal and the claim is rejected.

    Why not just trust the "kind" field:
        The AI could assign any kind to any change. The verification logic
        ignores the claim entirely and re-derives the answer from the specs.
        The kind field is used only to choose which verification branch to
        apply, not to accept the claim.
    """
    verified = []
    for change in ai.ask("migration_review", {"v1": v1, "v2": v2}):
        old_op = _operation(v1, change["path"], change["method"])
        new_op = _operation(v2, change["path"], change["method"])

        if change["kind"] == "operation_removed" and old_op and not new_op:
            verified.append(change)
        elif change["kind"] == "parameter_became_required" and old_op and new_op:
            name = change["parameter"]
            old = next(p for p in old_op.get("parameters", []) if p["name"] == name)
            new = next(p for p in new_op.get("parameters", []) if p["name"] == name)
            if not old.get("required", False) and new.get("required", False):
                verified.append(change)
        elif change["kind"] == "schema_changed" and old_op and new_op:
            name = change["parameter"]
            old = next(p for p in old_op.get("parameters", []) if p["name"] == name)
            new = next(p for p in new_op.get("parameters", []) if p["name"] == name)
            if old["schema"] != new["schema"]:
                verified.append(change)
    return verified
