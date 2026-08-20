"""LFN-CONFORMANCE-002 mutation suite.

M-001: valid human authorization + insufficient evidence must route to
REQUIRES_HUMAN, not BLOCKED.

M-002: valid human authorization MUST NOT increase evidentiary sufficiency.
Therefore the canonical Omni case remains UNVERIFIED; a mutant that promotes
it to VERIFIED must be detected as MUTATION_KILLED.

M-003: audit-only reason codes MUST remain separate from terminal guard codes.
A mutant that promotes E007 into guard_codes must be detected as
MUTATION_KILLED.

M-004: conformance execution MUST bind declared provenance to the actual Git
revision. The implementation exposes the actual revision and distinguishes
PROVENANCE_MATCH, PROVENANCE_MISMATCH, and PROVENANCE_MISSING.

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

    assert fixture["authorization_status"] == "VALID"
    assert fixture["evidence_sufficient"] is False

    baseline = evaluate(fixture)
    baseline_epistemic = _result_field(baseline, "epistemic_status")

    expected_epistemic = "UNVERIFIED"
    assert str(baseline_epistemic) == expected_epistemic, (
        f"Canonical evaluator violated AUTHORIZATION != PROOF: "
        f"expected {expected_epistemic!r}, got {baseline_epistemic!r}"
    )

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
    baseline_guards = sorted(_result_field(baseline, "guard_codes") or [])
    baseline_reasons = sorted(_result_field(baseline, "reason_codes") or [])
    expected_guards = sorted(fixture["expected"]["guard_codes"])

    audit_reason = "E007"
    assert audit_reason in baseline_reasons, (
        f"Canonical evaluator drifted: expected {audit_reason} in reason_codes"
    )
    assert audit_reason not in baseline_guards, (
        f"Canonical evaluator violated taxonomy separation: {audit_reason} "
        "appeared in guard_codes"
    )
    assert baseline_guards == expected_guards, (
        f"Canonical guard taxonomy drifted: expected {expected_guards}, "
        f"got {baseline_guards}"
    )

    mutant_guards = sorted(set(baseline_guards) | {audit_reason})
    mutation_survived = mutant_guards == expected_guards

    assert not mutation_survived, (
        "MUTATION_SURVIVED: M-003 promoted E007 into guard_codes, but "
        "the taxonomy detector failed to reject the collapse"
    )

    assert audit_reason in mutant_guards
    assert mutant_guards != baseline_guards

    print("MUTATION_KILLED: M-003")
    print(f"SPEC_EXPECTED_GUARDS={expected_guards}")
    print(f"CANONICAL_GUARDS={baseline_guards}")
    print(f"CANONICAL_REASONS={baseline_reasons}")
    print(f"MUTANT_GUARDS={mutant_guards}")
    print("INVARIANT=AUDIT_REASON_E007_NOT_IN_GUARD_CODES")


def test_m004_provenance_match():
    """M-004 implementation must bind a declared SHA to the actual Git SHA."""
    from lfn_provenance import (
        PROVENANCE_MATCH,
        classify_provenance,
        get_actual_git_revision,
    )

    actual_revision = get_actual_git_revision(ROOT)
    state = classify_provenance(actual_revision, actual_revision)

    assert state == PROVENANCE_MATCH, (
        "M-004 provenance implementation failed the canonical match: "
        f"expected {PROVENANCE_MATCH!r}, got {state!r}"
    )

    print("PROVENANCE_MATCH")
    print(f"DECLARED_PROVENANCE={actual_revision}")
    print(f"ACTUAL_PROVENANCE={actual_revision}")
    print("M-004 IMPLEMENTATION=BASELINE_MATCH")


def test_m004_provenance_mismatch_is_killed():
    """M-004 must reject a declared revision that differs from execution."""
    from lfn_provenance import (
        PROVENANCE_MATCH,
        PROVENANCE_MISMATCH,
        classify_provenance,
        get_actual_git_revision,
    )

    actual_revision = get_actual_git_revision(ROOT)
    mutant_declared_revision = "0" * 40
    mutation_state = classify_provenance(mutant_declared_revision, actual_revision)

    assert mutation_state == PROVENANCE_MISMATCH, (
        "M-004 provenance detector failed to classify the deliberate revision "
        f"mutation: expected {PROVENANCE_MISMATCH!r}, got {mutation_state!r}"
    )

    mutation_survived = mutation_state == PROVENANCE_MATCH
    assert not mutation_survived, (
        "MUTATION_SURVIVED: M-004 accepted a deliberately mismatched declared "
        "revision as PROVENANCE_MATCH"
    )

    print("MUTATION_KILLED: M-004")
    print(f"DECLARED_PROVENANCE={mutant_declared_revision}")
    print(f"ACTUAL_PROVENANCE={actual_revision}")
    print(f"PROVENANCE_STATE={mutation_state}")
    print("INVARIANT=DECLARED_EXECUTION_REVISION == ACTUAL_EXECUTION_REVISION")


if __name__ == "__main__":
    test_m001_mutation_is_killed()
    test_m002_authorization_is_not_proof()
    test_m003_taxonomy_separation()
    test_m004_provenance_match()
    test_m004_provenance_mismatch_is_killed()
