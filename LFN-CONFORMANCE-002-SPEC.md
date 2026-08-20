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

## 9.2 Repository Provenance Mechanism

The repository's provenance mechanism is explicitly implemented by
`tests/conformance/lfn_provenance.py`.

The implementation:

- obtains the actual revision using `git rev-parse HEAD`;
- validates the revision as a 40-character Git SHA;
- exposes `declared_revision` and `actual_revision` for comparison;
- distinguishes `PROVENANCE_MATCH`, `PROVENANCE_MISMATCH`, and
  `PROVENANCE_MISSING`;
- does not alter the canonical LFN-CONFORMANCE-001 evaluator semantics.

The CI workflow checks out the repository with `actions/checkout@v4` and
`fetch-depth: 0`, permitting the provenance mechanism to resolve the actual
revision under test.

`tools/validate_repo.py` remains a static JSON-content validator. Its
`checksum_sha256` mechanism is intentionally distinct from Git provenance
binding.

---

## 9.3 Normative Provenance Binding

Every M-004-aware conformance execution MUST determine the actual Git revision
under test.

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

## 10.1 Purpose

M-005 establishes that the canonical conformance evaluator produces a
repeatable normative decision when the same input fixture is evaluated twice
under the same evaluator and execution conditions.

The core deterministic-replay invariant is:

> `evaluate(F)_1 == evaluate(F)_2`

where equality is defined over the normative semantic result fields rather
than volatile execution metadata.

M-005 exists to detect semantic replay divergence, not to duplicate M-004
provenance binding or static JSON checksum validation.

---

## 10.2 Normative Semantic Replay Surface

For M-005, the following fields constitute the normative semantic replay
surface:

- `epistemic_status`
- `action`
- `guard_codes`
- `reason_codes`

Two evaluations of an identical fixture under identical declared conditions
MUST produce materially identical values for all four fields.

Collection-valued fields MUST be compared according to their semantic
contents. Where the implementation represents these collections as ordered
lists, the evaluator MUST preserve deterministic ordering or the replay
comparison MUST normalize ordering without changing semantic content.

---

## 10.3 Excluded Volatile Metadata

The following categories are NOT part of M-005 semantic replay equality:

- timestamps;
- CI run IDs;
- Git revision identifiers;
- process identifiers;
- filesystem paths that may vary by runner;
- environment metadata not participating in evaluation semantics;
- console formatting or diagnostic logging;
- random nonces or other intentionally volatile execution identifiers.

A difference confined to excluded metadata MUST NOT be classified as
`REPLAY_MISMATCH`.

M-005 MUST remain orthogonal to M-004. Git provenance identifies the revision
under test; deterministic replay establishes repeatability of the evaluator's
normative decision for identical input and conditions.

---

## 10.4 Functional Purity Requirement

For a fixed fixture and fixed evaluation conditions, the evaluator MUST NOT
allow mutable global state, wall-clock time, uncontrolled randomness, or other
unconstrained environmental effects to alter the normative semantic result.

The M-005 detector MUST therefore perform an actual dual evaluation of the
same fixture rather than relying solely on a static expected-output assertion.

The required baseline procedure is:

1. evaluate the fixture once;
2. evaluate the same fixture a second time;
3. extract the four normative semantic fields;
4. compare the two semantic results;
5. require exact semantic equivalence.

A baseline replay that diverges before mutation is a conformance defect and
MUST NOT be hidden by the mutation test.

---

## 10.5 Controlled Mutation

After establishing that the unmutated evaluator produces equivalent semantic
results across the two evaluations, the M-005 detector SHALL introduce an
isolated semantic mutation.

The mutation MUST alter a normative semantic field while leaving the fixture,
canonical evaluator, and unrelated metadata unchanged.

A representative controlled mutation is to alter one replay result field, for
example:

`action = REQUIRES_HUMAN`

to:

`action = BLOCKED`

or another deliberately selected semantic divergence justified by the
applicable conformance invariant.

The mutation MUST produce:

`REPLAY_MISMATCH`

when compared against the unmutated normative replay result.

---

## 10.6 Required Detection

The M-005 detector MUST establish both of the following independently:

1. **Baseline determinism:** the first and second evaluations of the identical
   fixture are semantically equivalent;
2. **Mutation sensitivity:** the deliberate semantic mutation is detected as a
   replay divergence.

The controlled mutation MUST NOT be accepted as equivalent merely because
volatile metadata differs or because the detector compares only a subset of
the normative semantic surface.

Required successful mutation result:

`REPLAY_MISMATCH`

followed by:

`MUTATION_KILLED`

A detector that reports `MUTATION_KILLED` without first proving baseline
replay equivalence is insufficient.

---

## 10.7 Isolation Requirement

M-005 MUST NOT modify:

- canonical fixture expectations;
- canonical evaluator semantics;
- provenance binding semantics;
- static JSON checksum semantics;
- guard/reason taxonomy;
- authorization semantics;
- epistemic evaluation semantics.

The mutation target is deterministic replay sensitivity only.

M-005 MUST remain independent from M-004. A matching Git revision is not proof
of deterministic evaluation, and deterministic evaluation is not proof of
provenance binding.

---

## 10.8 CI Requirement

The M-005 detector MUST be explicitly invoked by CI.

The workflow MUST execute the detector in a manner that guarantees the actual
replay procedure runs in the CI environment. Merely defining a helper function
or test that is not invoked by CI does not constitute an M-005 witness.

CI MUST preserve an auditable record showing:

- baseline replay equivalence;
- the deliberate semantic mutation;
- `REPLAY_MISMATCH` detection; and
- `MUTATION_KILLED: M-005`.

---

## 10.9 M-005 Epistemic Boundary

A successful M-005 result establishes only that the tested evaluator produced
repeatable semantic results for the exercised fixture and that the detector
caught the specified replay mutation.

It does NOT establish:

- deterministic behavior for every possible fixture;
- deterministic behavior across arbitrary software versions;
- deterministic behavior across arbitrary operating systems or runners;
- complete reproducible-build guarantees;
- provenance integrity;
- architecture-wide correctness.

Therefore:

> DETERMINISTIC REPLAY CONFORMANCE ≠ UNIVERSAL REPRODUCIBILITY PROOF

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

For M-005 specifically, replay divergence SHALL use:

`REPLAY_MISMATCH`

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

`KILLED`

Witness:

`Run #38 / c33375f`

### M-005

Status:

`SPECIFICATION LOCKED / IMPLEMENTATION PENDING`

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
