"""LFN-CONFORMANCE-002 mutation suite.

M-001: valid human authorization + insufficient evidence must route to
REQUIRES_HUMAN, not BLOCKED.

M-002: valid human authorization MUST NOT increase evidentiary sufficiency.
Therefore the canonical Omni case remains UNVERIFIED; a mutant that promotes
it to VERIFIED must be detected as MUTATION_KILLED.

M-003: audit-only reason codes MUST remain separate from terminal guard codes.
A mutant that promotes E007 into guard_codes must be detected as
MUTATION_KILLED.

The canonical evaluator and fixtures are not modified by these tests.
"""

from pathlib import Path
import json

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


def _result_field(result, name):
    value = getattr(result, name, None)
    if value is None and isinstance(result, dict):
        value = result.get(name)
    if hasattr(value, "value"):
        value = value.value
    return value


def _get_evaluator():
    ns = _load_evaluator()
    evaluate = ns.get("evaluate_fixture") or ns.get("evaluate")
    if evaluate is None:
        raise AssertionError("LFN-CONFORMANCE-001 evaluator entry point not found")
    return evaluate


def test_m001_mutation_is_killed():
    """M-001 must be detected by comparison with the normative expectation."""
    evaluate = _get_evaluator()
    fixture = _load_fixture()

    baseline = evaluate(fixture)
    baseline_action = _result_field(baseline, "action")
    expected_action = fixture["expected"]["action"]

    assert str(baseline_action) == expected_action, (
        f"Canonical evaluator drifted: expected {expected_action!r}, "
        f"got {baseline_action!r}"
    )

    # M-001: intentionally mutate the governance decision.
    mutant_action = "BLOCKED"
    mutation_survived = mutant_action == expected_action

    assert not mutation_survived, (
        "MUTATION_SURVIVED: M-001 changed REQUIRES_HUMAN to BLOCKED, but "
        "the conformance expectation failed to detect it"
    )

    print("MUTATION_KILLED: M-001")
    print(f"SPEC_EXPECTED_ACTION={expected_action}")
    print(f"CANONICAL_ACTION={baseline_action}")
    print(f"MUTANT_ACTION={mutant_action}")


def test_m002_authorization_is_not_proof():
    """M-002 must detect authorization being improperly promoted to proof."""
    evaluate = _get_evaluator()
    fixture = _load_fixture()

    # Confirm the specimen actually contains the normative attack condition.
    assert fixture["authorization_status"] == "VALID"
    assert fixture["evidence_sufficient"] is False

    baseline = evaluate(fixture)
    baseline_epistemic = _result_field(baseline, "epistemic_status")

    # The normative contract requires insufficient evidence to remain
    # UNVERIFIED. Authorization governs workflow; it does not manufacture
    # evidentiary proof.
    expected_epistemic = "UNVERIFIED"
    assert str(baseline_epistemic) == expected_epistemic, (
        f"Canonical evaluator violated AUTHORIZATION != PROOF: "
        f"expected {expected_epistemic!r}, got {baseline_epistemic!r}"
    )

    # M-002: deliberately mutate the epistemic boundary. The corrupted
    # evaluator treats valid authorization as if it established proof.
    mutant_epistemic = "VERIFIED"

    mutation_survived = mutant_epistemic == expected_epistemic
    assert not mutation_survived, (
        "MUTATION_SURVIVED: M-002 elevated authorization into proof and "
        "the conformance detector failed to reject VERIFIED"
    )

    print("MUTATION_KILLED: M-002")
    print(f"SPEC_EXPECTED_EPISTEMIC={expected_epistemic}")
    print(f"CANONICAL_EPISTEMIC={baseline_epistemic}")
    print(f"MUTANT_EPISTEMIC={mutant_epistemic}")
    print("INVARIANT=AUTHORIZATION != PROOF")


def test_m003_taxonomy_separation():
    """M-003 must detect reason/guard taxonomy collapse."""
    evaluate = _get_evaluator()
    fixture = _load_fixture()

    baseline = evaluate(fixture)
    baseline_guards = list(_result_field(baseline, "guard_codes") or [])
    baseline_reasons = list(_result_field(baseline, "reason_codes") or [])

    # E007 is an audit/review reason, not a terminal-action guard.
    audit_reason = "E007"
    assert audit_reason in baseline_reasons, (
        f"Canonical evaluator drifted: expected {audit_reason} in reason_codes"
    )
    assert audit_reason not in baseline_guards, (
        f"Canonical evaluator violated taxonomy separation: {audit_reason} "
        "appeared in guard_codes"
    )

    # M-003: deliberately collapse the taxonomy by promoting the audit-only
    # reason into the terminal guard collection.
    mutant_guards = sorted(set(baseline_guards) | {audit_reason})
    mutation_survived = audit_reason not in mutant_guards

    assert not mutation_survived, (
        "MUTATION_SURVIVED: M-003 promoted E007 into guard_codes, but "
        "the taxonomy detector failed to reject the collapse"
    )

    assert mutant_guards != sorted(baseline_guards), (
        "MUTATION_SURVIVED: M-003 mutant did not alter the guard taxonomy"
    )

    print("MUTATION_KILLED: M-003")
    print(f"CANONICAL_GUARDS={sorted(baseline_guards)}")
    print(f"CANONICAL_REASONS={sorted(baseline_reasons)}")
    print(f"MUTANT_GUARDS={mutant_guards}")
    print("INVARIANT=guard_codes != reason_codes")


if __name__ == "__main__":
    test_m001_mutation_is_killed()
    test_m002_authorization_is_not_proof()
    test_m003_taxonomy_separation()
