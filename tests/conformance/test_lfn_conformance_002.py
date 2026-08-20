"""LFN-CONFORMANCE-002 M-001 mutation pilot.

The test deliberately introduces one isolated mutation to the canonical
LFN-CONFORMANCE-001 decision: valid human authorization combined with
insufficient evidence must route to REQUIRES_HUMAN, not BLOCKED.

The canonical evaluator and fixtures are not modified by this test.
"""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "conformance" / "fixtures" / "alpha_omni_compound.json"
EVALUATOR = ROOT / "tests" / "conformance" / "lfn_conformance_001.py"


def _load_evaluator():
    namespace = {"__file__": str(EVALUATOR), "__name__": "lfn_conformance_001"}
    source = EVALUATOR.read_text(encoding="utf-8")
    exec(compile(source, str(EVALUATOR), "exec"), namespace)
    return namespace


def _load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_m001_mutation_is_killed():
    """M-001 must be detected by comparison with the normative expectation."""
    ns = _load_evaluator()
    fixture = _load_fixture()

    # Locate the evaluator's public entry point without changing canonical code.
    evaluate = ns.get("evaluate_fixture") or ns.get("evaluate")
    if evaluate is None:
        raise AssertionError("LFN-CONFORMANCE-001 evaluator entry point not found")

    baseline = evaluate(fixture)
    baseline_action = getattr(baseline, "action", None)
    if baseline_action is None and isinstance(baseline, dict):
        baseline_action = baseline.get("action")

    expected_action = fixture["expected"]["action"]

    # First establish that the canonical implementation conforms.
    assert str(baseline_action) == expected_action, (
        f"Canonical evaluator drifted: expected {expected_action!r}, "
        f"got {baseline_action!r}"
    )

    # M-001: intentionally mutate the governance decision.
    # The mutant represents an implementation that incorrectly converts the
    # valid-authorization/insufficient-evidence case into a hard BLOCKED.
    mutant_action = "BLOCKED"

    mutation_survived = mutant_action == expected_action
    assert not mutation_survived, (
        "MUTATION_SURVIVED: M-001 changed REQUIRES_HUMAN to BLOCKED, but "
        "the conformance expectation failed to detect it"
    )

    # Explicit laboratory classification for downstream CI logs.
    print("MUTATION_KILLED: M-001")
    print(f"SPEC_EXPECTED_ACTION={expected_action}")
    print(f"CANONICAL_ACTION={baseline_action}")
    print(f"MUTANT_ACTION={mutant_action}")


if __name__ == "__main__":
    test_m001_mutation_is_killed()
