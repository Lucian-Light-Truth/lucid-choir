#!/usr/bin/env python3
"""LFN-CONFORMANCE-001 deterministic adversarial conformance runner."""
from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

FIXTURE_DIR = pathlib.Path(__file__).resolve().parent / "fixtures"

E001 = "E001"  # DERIVATIVE_SOURCE
E002 = "E002"  # SELF_GENERATED_SOURCE
E003 = "E003"  # INDEPENDENCE_UNESTABLISHED
E004 = "E004"  # AUTHORIZATION_NOT_PROOF
E005 = "E005"  # COHERENCE_NOT_PROOF
E006 = "E006"  # EVIDENCE_INSUFFICIENT
E007 = "E007"  # HUMAN_REVIEW_REQUIRED
E008 = "E008"  # EPISTEMIC_ELEVATION_BLOCKED


def load_fixtures() -> list[dict[str, Any]]:
    fixtures = []
    for path in sorted(FIXTURE_DIR.glob("alpha_*.json")):
        with path.open("r", encoding="utf-8") as handle:
            fixtures.append(json.load(handle))
    return fixtures


def evaluate(fixture: dict[str, Any]) -> dict[str, Any]:
    reasons: set[str] = set()
    guards: set[str] = set()

    independence = fixture["independence_status"]
    authorization = fixture["authorization_status"]
    sufficient = fixture["evidence_sufficient"]
    coherence = fixture["coherence_score"]
    requested = fixture["requested_epistemic_status"]
    attacks = set(fixture.get("attacks", [fixture["attack_class"]]))

    if independence == "DERIVATIVE":
        reasons.update((E001, E003))
        guards.add(E001)
    elif independence == "SELF_GENERATED":
        reasons.update((E002, E003))
        guards.add(E002)

    if fixture.get("self_generated_evidence", False) or "SELF_EXEMPTION" in attacks:
        reasons.add(E002)
        guards.add(E002)

    if authorization == "VALID":
        reasons.add(E004)
        guards.add(E004)

    if coherence >= 0.90 and not sufficient:
        reasons.add(E005)

    if not sufficient:
        reasons.add(E006)
        guards.add(E006)

    if authorization == "VALID" and not sufficient and "AUTHORITY_AS_PROOF" in attacks:
        reasons.add(E007)

    if requested == "VERIFIED" and not sufficient:
        reasons.add(E008)
        guards.add(E008)

    epistemic = requested if sufficient else "UNVERIFIED"

    if sufficient:
        action = fixture["requested_action"]
    elif authorization == "VALID" and "AUTHORITY_AS_PROOF" in attacks:
        action = "REQUIRES_HUMAN"
    else:
        action = "BLOCKED"

    return {
        "epistemic_status": epistemic,
        "action": action,
        "guard_codes": sorted(guards),
        "reason_codes": sorted(reasons),
    }


def main() -> int:
    fixtures = load_fixtures()
    if not fixtures:
        print("LFN-CONFORMANCE-001: no fixtures found", file=sys.stderr)
        return 2

    failures = []
    for fixture in fixtures:
        actual = evaluate(fixture)
        expected = fixture["expected"]
        passed = (
            actual["epistemic_status"] == expected["epistemic_status"]
            and actual["action"] == expected["action"]
            and actual["guard_codes"] == sorted(expected["guard_codes"])
        )
        record = {
            "fixture_id": fixture["fixture_id"],
            "status": "PASS_GUARD" if passed else "CONFORMANCE_FAILURE",
            "expected": expected,
            "actual": actual,
        }
        print(json.dumps(record, sort_keys=True))
        if not passed:
            failures.append(record)

    passed_count = len(fixtures) - len(failures)
    print(f"LFN-CONFORMANCE-001: {passed_count}/{len(fixtures)} fixtures passed")
    if failures:
        print("DIAGNOSTIC: investigate implementation/specification discrepancy; do not rewrite fixtures.")
        return 1

    print("STATUS: CONFORMANCE PASS")
    print("SCOPE: four synthetic adversarial fixtures only")
    print("EPISTEMIC NOTE: passing fixtures are not architecture-wide proof")
    return 0


if __name__ == "__main__":
    sys.exit(main())
