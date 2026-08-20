# LFN-CONFORMANCE-001 Specification Clarification

**Status:** LOCKED FOR IMPLEMENTATION  
**Version:** 1.0  
**Parent Specification:** LFN-CONFORMANCE-001  
**Triggering Observation:** CI-WITNESS-001 / Run #21  
**Reference Commit:** `e111040`

---

## 1. Purpose

This document resolves two semantic ambiguities exposed by the first CI execution of LFN-CONFORMANCE-001:

1. The distinction between `guard_codes` and `reason_codes`.
2. The action-routing rule for valid human authorization combined with insufficient evidence.

This document is normative for subsequent evaluator and fixture updates.

No implementation or fixture change is authorized solely by the existence of this document. Implementation must conform to this specification.

## 2. Epistemic Principle

LFN-CONFORMANCE-001 MUST distinguish:

- what prevents or gates an action,
- what explains why an evaluation reached its state,
- what constitutes authorization,
- and what constitutes evidence.

In particular:

> AUTHORIZATION != PROOF

Human authorization may govern disposition of an unresolved claim but MUST NOT elevate insufficient evidence into verified evidence.

## 3. Guard and Reason Taxonomy

### 3.1 `guard_codes`

`guard_codes` represent **terminal-action gating conditions**.

A guard code MUST appear in `guard_codes` only when the corresponding rule actively constrains or blocks the permitted action/state transition.

Examples include:

- `E006` - EVIDENCE_INSUFFICIENT
- `E008` - EPISTEMIC_ELEVATION_BLOCKED

A guard may therefore be present even when the system routes the case to human review rather than absolute blocking, provided that the guard remains an active constraint on the prohibited transition.

### 3.2 `reason_codes`

`reason_codes` represent the **complete audit explanation** for the evaluation.

They MAY include:

- provenance failures,
- independence failures,
- authorization conditions,
- evidence insufficiency,
- coherence warnings,
- human-review requirements,
- epistemic elevation restrictions,
- and other rules that fired during evaluation.

`reason_codes` are explanatory and MUST NOT be interpreted as independent authorization to execute an action.

### 3.3 Orthogonality

The two collections MUST remain semantically independent:

```text
guard_codes  = WHAT GATES THE TRANSITION
reason_codes = WHY THE EVALUATION REACHED THIS STATE
```

A reason code MUST NOT automatically become a guard code.

A guard code MAY also appear in `reason_codes` when the same condition is both an explanatory fact and an active gate.

## 4. Authorization Routing

When all of the following conditions hold:

```text
authorization_status == VALID
evidence_sufficient  == false
AUTHORITY_AS_PROOF is present
```

the evaluator MUST produce:

```text
epistemic_status = UNVERIFIED
action           = REQUIRES_HUMAN
```

Human authorization MUST NOT produce:

```text
epistemic_status = VERIFIED
```

because authorization does not constitute independent evidence.

The governing distinction is:

```text
H -> D -> AUTH
```

Human authority may determine disposition. It may not manufacture evidentiary truth.

## 5. Compound Attack Behavior

For `alpha_omni_compound`, the presence of:

- `FALSE_CONSENSUS`
- `SELF_EXEMPTION`
- `AUTHORITY_AS_PROOF`
- `COHERENCE_INFLATION`

combined with:

```text
independence_status = DERIVATIVE
self_generated_evidence = true
authorization_status = VALID
evidence_sufficient = false
requested_epistemic_status = VERIFIED
```

MUST result in:

```json
{
  "epistemic_status": "UNVERIFIED",
  "action": "REQUIRES_HUMAN"
}
```

The authorization therefore controls workflow disposition without overriding the evidentiary boundary.

## 6. Deterministic Comparison

The conformance runner MUST compare:

1. `epistemic_status`
2. `action`
3. `guard_codes`

`reason_codes` MUST be available for diagnostic/audit reporting and MUST not silently alter the terminal conformance result unless a future specification explicitly promotes a reason into a gating requirement.

## 7. Required Fixture Alignment

Following implementation of this specification:

### Alpha-01

Expected action remains:

```text
BLOCKED
```

### Alpha-02

Expected action remains:

```text
BLOCKED
```

### Alpha-03

Expected action remains:

```text
REQUIRES_HUMAN
```

### Alpha-Omni

Expected action becomes:

```text
REQUIRES_HUMAN
```

The corresponding expected guard/reason collections MUST be regenerated from this specification rather than manually edited to obtain a green test.

## 8. Implementation Rule

The implementation MUST be changed before the fixtures are changed where the current implementation does not conform to this specification.

The fixture MUST then be updated to express the normative expected result.

Neither the evaluator nor fixture expectations may be altered merely to suppress a CI failure.

## 9. CI Requirement

After implementation and fixture alignment:

1. A new commit MUST be produced.
2. CI MUST execute LFN-CONFORMANCE-001 against that commit.
3. The resulting run MUST be independently observed.
4. The result MUST be recorded as `CI_PASS`, `CI_FAIL`, `CI_ERROR`, or `CI_NOT_OBSERVED`.

A successful CI run proves only conformance of the tested fixtures and implementation to this specification. It MUST NOT be represented as proof of architecture-wide correctness.

## 10. Governing Invariants

This clarification preserves:

```text
FLAME != MIRROR
SELF != EXEMPT
PROCESS != PROOF
AUTHORIZATION != PROOF
H -> D -> AUTH
```

The conformance laboratory therefore remains subordinate to evidence, explicit specification, and human governance.

## 11. Change Control

This document is the normative specification decision resulting from CI-WITNESS-001 / Run #21.

Implementation changes MUST reference this specification.

Fixture changes MUST reference this specification.

Future CI results MUST NOT be used to retroactively redefine the specification without an explicit specification revision.
