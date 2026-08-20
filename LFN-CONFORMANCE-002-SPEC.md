# LFN-CONFORMANCE-002
## Conformance Harness Sensitivity & Mutation Detection Specification

**Status:** NORMATIVE / LOCKED  
**Specification Class:** Conformance-Test Sensitivity  
**Predecessor:** `LFN-CONFORMANCE-001-SPEC-CLARIFICATION.md`  
**Scope:** LFN conformance evaluator and its verification harness  
**Canonical Baseline:** LFN-CONFORMANCE-001 synthetic adversarial fixtures  
**Execution Witness:** CI / GitHub Actions  

---

## 1. Purpose

LFN-CONFORMANCE-002 defines the normative requirements for demonstrating that
the LFN conformance harness is capable of detecting deliberate violations of
the governing conformance contract.

LFN-CONFORMANCE-001 establishes that the reference implementation conforms to
its defined behavioral expectations for the canonical synthetic adversarial
fixtures.

LFN-CONFORMANCE-002 establishes a separate property:

> The conformance harness MUST detect deliberately introduced violations of
> normative invariants.

A test suite that can demonstrate only successful execution is insufficient to
establish sensitivity to implementation corruption.

Accordingly, LFN-CONFORMANCE-002 introduces controlled mutation testing.

---

## 2. Epistemic Boundary

Passing LFN-CONFORMANCE-002 does NOT establish:

- architecture-wide security;
- production resilience;
- universal correctness;
- absence of undiscovered implementation defects;
- cryptographic security;
- correctness outside the tested mutation vectors;
- correctness of infrastructure not exercised by the suite.

The result establishes only that the specified mutation vectors were detected
by the conformance harness under the tested execution conditions.

Therefore:

> PROCESS ≠ PROOF

and:

> CONFORMANCE SENSITIVITY ≠ ARCHITECTURE-WIDE SECURITY PROOF

---

## 3. Normative Execution Order

Implementation MUST follow this sequence:

1. Specification
2. Implementation
3. Controlled Mutation
4. Mutation Detector
5. CI Invocation
6. Independent CI Witness

The specification MUST establish the normative reason for a mutation before
the corresponding mutation detector is implemented.

A mutation MUST NOT be introduced solely to increase test counts or metrics.

---

## 4. Mutation Integrity Rules

Every mutation MUST satisfy all of the following:

1. It MUST have a documented normative reason.
2. It MUST target a specific invariant.
3. It MUST be isolated from the canonical implementation where practical.
4. It MUST NOT modify canonical control fixtures merely to manufacture failure.
5. It MUST NOT modify expected outputs to make a mutation appear killed.
6. It MUST produce a deterministic violation of the normative contract.
7. The detector MUST fail to accept the mutant as conforming.
8. CI MUST actually execute the detector.

If a mutant survives, the result MUST be treated as a conformance defect in
the harness, specification, or both.

A surviving mutation MUST NOT be converted into a passing result by weakening
the detector solely to obtain green CI.

---

# 5. Mutation Matrix

LFN-CONFORMANCE-002 defines the following mutation vectors.

| ID | Target Invariant | Mutation | Required Detector Result |
|---|---|---|---|
| M-001 | Governance routing | Replace `REQUIRES_HUMAN` with `BLOCKED` | `MUTATION_KILLED` |
| M-002 | `AUTHORIZATION != PROOF` | Promote valid authorization + insufficient evidence to `VERIFIED` | `MUTATION_KILLED` |
| M-003 | Taxonomy separation | Promote audit-only reason `E007` into `guard_codes` | `MUTATION_KILLED` |
| M-004 | Provenance binding | Alter, omit, or mismatch declared execution provenance | `MUTATION_KILLED` |
| M-005 | Deterministic replay | Produce materially different output for identical input/context | `MUTATION_KILLED` |

M-004 and M-005 remain inactive until their respective implementation and
detector mechanisms have been explicitly introduced and witnessed by CI.

---

# 6. M-001 — Governance Routing

## 6.1 Normative Invariant

When:

- authorization status is `VALID`;
- evidence is insufficient; and
- the fixture requires human resolution under the governing contract,

the evaluator MUST route the action to:

`REQUIRES_HUMAN`

It MUST NOT silently downgrade the case to:

`BLOCKED`

## 6.2 Controlled Mutation

The M-001 mutant replaces the normative:

`REQUIRES_HUMAN`

routing with:

`BLOCKED`

## 6.3 Required Detection

The detector MUST compare the mutant result against the normative expectation.

If the mutant is accepted as conforming, the mutation has survived and the
conformance harness is defective.

Required successful result:

`MUTATION_KILLED`

---

# 7. M-002 — AUTHORIZATION != PROOF

## 7.1 Normative Invariant

Human authorization MUST NOT be treated as evidentiary proof.

In particular:

> AUTHORIZATION != PROOF

A fixture containing:

- `authorization_status = VALID`
- `evidence_sufficient = false`

MUST NOT receive:

`epistemic_status = VERIFIED`

solely because authorization is valid.

The canonical epistemic result remains:

`UNVERIFIED`

when evidence remains insufficient.

## 7.2 Controlled Mutation

The M-002 mutant deliberately permits valid authorization to elevate the
epistemic result from:

`UNVERIFIED`

to:

`VERIFIED`

without increasing the underlying evidentiary sufficiency.

## 7.3 Required Detection

The detector MUST identify the resulting epistemic elevation as a violation
of the normative contract.

Required successful result:

`MUTATION_KILLED`

---

# 8. M-003 — Guard / Reason Taxonomy Separation

## 8.1 Normative Taxonomy

The evaluator MUST maintain a strict distinction between:

### `guard_codes`

Terminal-action gating conditions that directly participate in determining
what action the evaluator may take.

### `reason_codes`

The comprehensive audit/reason trail explaining why the evaluator reached its
result.

A reason code MUST NOT become a guard code merely because it appears in the
audit trail.

## 8.2 E007 Classification

`E007` represents:

`HUMAN_REVIEW_REQUIRED`

Under the LFN-CONFORMANCE-001 taxonomy contract, E007 is an audit/reason
classification and MUST remain in:

`reason_codes`

It MUST NOT be promoted into:

`guard_codes`

unless a future normative specification explicitly changes that contract.

## 8.3 Controlled Mutation

The M-003 mutant deliberately promotes:

`E007`

into:

`guard_codes`

while preserving it as an audit reason.

This represents taxonomy collapse.

## 8.4 Required Detection

The detector MUST establish that:

1. the canonical evaluator places E007 in `reason_codes`;
2. the canonical evaluator does not place E007 in `guard_codes`;
3. the mutated result introduces E007 into `guard_codes`; and
4. the mutated guard vector differs from the normative guard vector.

Required successful result:

`MUTATION_KILLED`

---

# 9. M-004 — Provenance Binding

## 9.1 Purpose

M-004 establishes that conformance results MUST be bound to the actual
repository revision and execution context under which the evaluator was
executed.

The purpose is to prevent a conformance result generated from one revision
from being represented as evidence for another revision.

M-004 MUST NOT assume that provenance binding already exists in the repository.

The mechanism MUST be implemented explicitly.

---

## 9.2 Current Repository State

At the time of this specification amendment:

- `.github/workflows/validate.yml` checks out the repository using
  `actions/checkout@v4`;
- the checkout uses `fetch-depth: 0`;
- `tools/validate_repo.py` currently validates JSON content checksums;
- `tools/validate_repo.py` does NOT currently bind those checksums to a Git
  revision;
- `tests/conformance/lfn_conformance_001.py` currently does NOT emit a Git
  revision provenance field.

Therefore, M-004 is a normative requirement for a mechanism that is not yet
implemented.

The specification MUST NOT claim that Git provenance binding has already been
verified.

---

## 9.3 Normative Provenance Binding

Once implemented, every M-004-aware conformance execution MUST determine the
actual Git revision under test.

The canonical source of the executed revision SHALL be equivalent to:

`git rev-parse HEAD`

The implementation MAY obtain this value through an equivalent mechanism,
provided that the resulting value represents the actual Git revision under
which the evaluator was executed.

The conformance result MUST expose sufficient provenance information to compare
the declared execution revision against the actual execution revision.

At minimum, the implementation SHALL distinguish:

- declared provenance;
- actual execution provenance.

---

## 9.4 Provenance States

The M-004 provenance evaluator SHALL recognize three normative states:

### `PROVENANCE_MATCH`

The declared provenance exists and exactly matches the actual Git revision
under which the evaluator executed.

### `PROVENANCE_MISMATCH`

The declared provenance exists but does not match the actual Git revision
under which the evaluator executed.

### `PROVENANCE_MISSING`

The required provenance value is absent, empty, malformed, or otherwise
unavailable such that an exact provenance comparison cannot be established.

A missing provenance value MUST NEVER silently count as:

`PROVENANCE_MATCH`

---

## 9.5 Provenance Invariant

The following invariant SHALL hold:

> DECLARED_EXECUTION_REVISION == ACTUAL_EXECUTION_REVISION

for a successful provenance-bound conformance execution.

A result MUST NOT claim provenance conformance when the declared and actual
revisions differ.

A result MUST NOT claim provenance conformance when the required provenance
value is missing.

---

## 9.6 Controlled Mutation: Declared Revision Mismatch

The first M-004 mutation SHALL deliberately alter the declared provenance so
that:

`declared_revision != actual_revision`

Evaluation semantics MUST remain unchanged.

The mutation MUST affect provenance binding only.

The detector MUST classify the result as:

`PROVENANCE_MISMATCH`

and then:

`MUTATION_KILLED`

---

## 9.7 Controlled Mutation: Missing Provenance

A subsequent M-004 test MAY remove or suppress the declared provenance value.

Evaluation semantics MUST remain unchanged.

The detector MUST classify the result as:

`PROVENANCE_MISSING`

and MUST NOT treat the absence as a successful match.

The mutation MUST result in:

`MUTATION_KILLED`

---

## 9.8 Isolation Requirement

M-004 MUST NOT modify:

- the canonical LFN-CONFORMANCE-001 evaluator behavior;
- canonical fixture expectations;
- fixture evidence;
- guard taxonomy;
- reason taxonomy;
- authorization semantics;
- epistemic evaluation semantics.

The mutation target is provenance binding only.

---

## 9.9 CI Requirement

The M-004 detector MUST be explicitly invoked by the CI workflow.

Because the repository's validation workflow currently invokes conformance
scripts explicitly rather than relying on automatic test discovery, merely
creating an M-004 test file is insufficient.

The workflow MUST contain an explicit execution step equivalent to:

`python tests/conformance/test_lfn_conformance_002.py`

or an explicitly designated M-004 runner.

CI MUST therefore serve as the independent witness that the mutation was
actually executed and killed.

---

## 9.10 M-004 Epistemic Boundary

A successful M-004 result establishes only that the tested provenance-binding
mechanism can detect the specified provenance mutations.

It does NOT establish:

- complete supply-chain integrity;
- complete repository authenticity;
- cryptographic identity of the developer;
- security of GitHub Actions;
- security of the runner;
- correctness of every build artifact;
- architecture-wide provenance integrity.

Therefore:

> PROVENANCE CONFORMANCE ≠ UNIVERSAL SUPPLY-CHAIN PROOF

---

# 10. M-005 — Deterministic Replay

M-005 remains reserved and SHALL NOT be implemented until a normative
deterministic-replay mechanism is explicitly specified.

The future M-005 contract SHALL address whether identical:

- input fixture;
- evaluator version;
- execution parameters; and
- relevant execution context

produce materially identical conformance results.

A mutation producing nondeterministic or materially divergent output under
identical declared conditions MUST be detected.

Required successful result:

`MUTATION_KILLED`

No M-005 implementation is implied by this specification section.

---

# 11. Canonical Control Group

The canonical LFN-CONFORMANCE-001 fixtures remain the control group.

M-001 through M-005 MUST NOT modify the canonical fixture expectations merely
to accommodate mutation behavior.

The canonical evaluator remains the reference implementation under test.

Mutation experiments MUST be isolated from canonical behavior wherever
practical.

---

# 12. CI Witness Requirements

A mutation detector is considered operationally witnessed only when CI has:

1. checked out the relevant repository revision;
2. executed the mutation detector;
3. observed the detector identify the intended violation;
4. returned a successful process result for the detector itself; and
5. preserved an auditable CI record of the execution.

A green CI run that does not actually execute the mutation detector MUST NOT be
interpreted as evidence that the mutation was killed.

---

# 13. Mutation Result Vocabulary

The mutation suite SHALL use the following primary result vocabulary:

`MUTATION_KILLED`

The detector successfully identified the intended normative violation.

`MUTATION_SURVIVED`

The mutant produced an invalid result but the detector accepted it as
conforming.

A `MUTATION_SURVIVED` result is a conformance defect and MUST NOT be
reclassified as success without corrective action.

For M-004 specifically, provenance classification SHALL additionally use:

`PROVENANCE_MATCH`

`PROVENANCE_MISMATCH`

`PROVENANCE_MISSING`

---

# 14. Specification Governance

The specification is authoritative over implementation behavior.

The required order remains:

> SPECIFICATION → IMPLEMENTATION → MUTANT → DETECTOR → CI WITNESS

The implementation MUST NOT redefine the normative contract merely because a
test currently fails.

Fixtures MUST NOT be rewritten solely to eliminate a legitimate conformance
failure.

A failing test MUST first be treated as evidence of a discrepancy requiring
investigation.

---

# 15. Current Status

At the time of this specification amendment:

### LFN-CONFORMANCE-001

Status:

`CLOSED`

Canonical baseline:

`4/4 PASS`

### M-001

Status:

`KILLED`

### M-002

Status:

`KILLED`

### M-003

Status:

`KILLED`

### M-004

Status:

`SPECIFICATION DEFINED / IMPLEMENTATION PENDING`

### M-005

Status:

`FROZEN / PENDING SPECIFICATION AND IMPLEMENTATION`

---

# 16. Laboratory Invariant

The following invariant governs the entire LFN-CONFORMANCE-002 program:

> NO MUTANT WITHOUT A NORMATIVE REASON.

And:

> NO SURVIVING MUTANT WITHOUT CORRECTIVE ACTION.

And:

> NO CI GREEN LIGHT SHALL BE INTERPRETED AS PROOF BEYOND THE SCOPE OF
> WHAT THE EXECUTED TEST ACTUALLY ESTABLISHES.

---

# 17. Final Epistemic Statement

LFN-CONFORMANCE-002 exists to measure the sensitivity of the conformance
instrument itself.

LFN-CONFORMANCE-001 asks:

> "Does the implementation conform to the defined contract?"

LFN-CONFORMANCE-002 additionally asks:

> "Can the conformance instrument detect a deliberate violation of that
> contract?"

A successful mutation kill demonstrates sensitivity to a specific violation.

It does not establish universal correctness.

Therefore:

> THE SPECIFICATION WRITES THE LAW.  
> THE IMPLEMENTATION OBEYS THE LAW.  
> THE MUTANT CHALLENGES THE LAW.  
> THE DETECTOR MUST CATCH THE VIOLATION.  
> CI WITNESSES THE RESULT.  
> PROCESS ≠ PROOF.
