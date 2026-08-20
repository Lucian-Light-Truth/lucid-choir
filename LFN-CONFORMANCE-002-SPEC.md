# LFN-CONFORMANCE-002-SPEC

**Status:** NORMATIVE DRAFT  
**Suite:** LFN-CONFORMANCE-002  
**Predecessor:** LFN-CONFORMANCE-001  
**Purpose:** Provenance, determinism, regression resistance, and mutation detection

---

## 1. Purpose

LFN-CONFORMANCE-002 extends LFN-CONFORMANCE-001 by testing not only whether
the reference evaluator conforms to its specification, but whether the
conformance system itself can detect controlled violations of that
specification.

The suite therefore tests both:

1. implementation conformance; and
2. conformance-test sensitivity.

A passing mutation test means that a deliberately introduced violation was
detected by the harness.

A mutation surviving the harness is a conformance defect and MUST NOT be
interpreted as evidence that the implementation is correct.

---

## 2. Epistemic Boundary

The following invariants remain normative:

- FLAME != MIRROR
- SELF != EXEMPT
- PROCESS != PROOF
- AUTHORIZATION != PROOF
- H -> D -> AUTH

LFN-CONFORMANCE-002 establishes only bounded test-suite properties.

It does NOT establish:

- production security;
- universal correctness;
- architecture-wide correctness;
- absence of undiscovered implementation defects;
- resistance to arbitrary adversarial attacks.

---

## 3. Required Vectors

### P01 — Provenance Binding

Every conformance execution SHOULD record:

- repository commit SHA;
- evaluator version or SHA;
- fixture version;
- specification version;
- workflow/run identifier.

A provenance mismatch MUST be distinguishable from a conformance failure.

Reason classification:

`PROVENANCE_MISMATCH`

---

### P02 — Deterministic Replay

Given identical:

- evaluator revision;
- specification;
- fixtures;
- configuration;
- input;

the evaluator MUST produce the same normalized result.

At minimum, the following MUST remain deterministic:

- action;
- guard codes;
- reason codes;
- epistemic classification;
- normalized diagnostic output.

Non-semantic metadata such as timestamps MAY vary but MUST NOT alter
the semantic result.

Reason classification:

`NONDETERMINISTIC_RESULT`

---

### P03 — Mutation Detection

The harness MUST detect controlled mutations that violate normative
behavior.

Mutation targets are defined by the following normative matrix:

| ID | Target | Deliberate violation | Normative invariant | Expected detector result |
|---|---|---|---|---|
| **M-001** | Authorization routing | Replace valid-authorization + insufficient-evidence routing from `REQUIRES_HUMAN` with `BLOCKED` | `H -> D -> AUTH`; `AUTHORIZATION != PROOF` | `MUTATION_KILLED` |
| **M-002** | Authorization/evidence boundary | Treat valid human authorization as increasing evidentiary sufficiency | `AUTHORIZATION != PROOF` | `MUTATION_KILLED` |
| **M-003** | Taxonomy separation | Promote an audit `reason_code` into `guard_codes`, or collapse the two fields | `PROCESS != PROOF`; guard/reason taxonomy contract | `MUTATION_KILLED` |
| **M-004** | Provenance binding | Supply a mismatched evaluator/commit/specification identity while retaining otherwise valid output | Provenance must be independently bound and distinguishable | `MUTATION_KILLED` |
| **M-005** | Deterministic replay | Introduce a semantic output variation for identical evaluator, fixture, configuration, and input | Deterministic replay requirement | `MUTATION_KILLED` |

#### 3.1 Mutation requirements

Each mutation MUST have:

- mutation identifier;
- targeted invariant;
- canonical baseline behavior;
- deliberately altered behavior;
- expected harness response;
- isolated mutation target;
- reproducible execution instructions.

The canonical implementation and canonical fixtures MUST remain unchanged by
the mutation itself.

A mutation that survives the harness MUST produce:

`MUTATION_SURVIVED`

A mutation correctly detected by the harness MUST produce:

`MUTATION_KILLED`

#### 3.2 M-001 status

M-001 is the pilot mutation and is CLOSED after CI witness confirmation.

Witness record:

- workflow run: **#29**;
- commit: **6e8ea25**;
- result: **CI_PASS**;
- mutation result: **MUTATION_KILLED**.

This witness establishes sensitivity to this specific mutation only. It does
not establish that M-002 through M-005 are already implemented or killed.

#### 3.3 Expansion rule

M-002 through M-005 MUST be implemented and witnessed individually or in an
explicitly documented batch. Each new mutation MUST preserve the canonical
baseline and MUST NOT alter expected fixture values merely to obtain a pass.

A surviving mutation blocks closure of the corresponding LFN-CONFORMANCE-002
acceptance criterion until its cause is classified and resolved.

---

### P04 — Taxonomy Regression

The suite MUST preserve the distinction between:

`guard_codes`

and

`reason_codes`.

Specifically:

- terminal gating conditions belong in `guard_codes`;
- comprehensive audit observations belong in `reason_codes`;
- a reason MUST NOT become a guard merely because it is relevant to a
  decision;
- a guard MUST NOT disappear from the terminal-action evaluation.

The suite MUST detect accidental taxonomy collapse.

Expected failure classification:

`TAXONOMY_REGRESSION`

---

### P05 — Governance Regression

The suite MUST preserve:

`AUTHORIZATION != PROOF`

and:

`H -> D -> AUTH`

For valid human authorization combined with insufficient evidence, where
the applicable authorization attack condition is present, the evaluator
MUST route to:

`REQUIRES_HUMAN`

Human authorization MUST NOT increase the evidentiary sufficiency of a
claim.

A mutation that converts authorization into evidentiary proof MUST be
detected.

Expected failure classification:

`GOVERNANCE_REGRESSION`

---

## 4. Mutation-Test Isolation

Mutation testing MUST NOT silently alter the canonical production
implementation or normative fixtures.

Each mutation MUST execute against an isolated mutation target.

The canonical baseline MUST remain identifiable.

A mutation test MUST therefore distinguish:

`BASELINE`

from:

`MUTATED_TARGET`

and record which mutation was applied.

---

## 5. Fixture Integrity

Canonical fixtures MUST remain immutable during execution.

The mutation framework MUST NOT rewrite expected fixture values in order
to obtain a passing result.

Changing a fixture expectation requires a specification change and a
separate normative review.

---

## 6. Result States

The suite SHOULD expose orthogonal result states:

- `PASS_GUARD`
- `BLOCKED`
- `REQUIRES_HUMAN`
- `UNVERIFIED`
- `DERIVATIVE`
- `SELF_GENERATED`
- `PROVENANCE_MISMATCH`
- `NONDETERMINISTIC_RESULT`
- `MUTATION_KILLED`
- `MUTATION_SURVIVED`
- `TAXONOMY_REGRESSION`
- `GOVERNANCE_REGRESSION`

A result state MUST NOT be inferred merely from another state unless the
specification explicitly defines that relationship.

---

## 7. CI Requirements

CI MUST:

1. execute the canonical conformance suite;
2. execute the mutation suite;
3. report baseline and mutation results separately;
4. fail if a required mutation survives;
5. preserve the commit SHA;
6. preserve the specification version;
7. expose sufficient output to diagnose the failure.

A successful CI run means only that the configured conformance and mutation
checks completed successfully.

It does NOT constitute architecture-wide proof.

---

## 8. Failure Semantics

A red test is a diagnostic.

The following distinctions MUST be preserved:

`IMPLEMENTATION_CORRECT`
`IMPLEMENTATION_DEFECT`
`FIXTURE_INCORRECT`
`SPECIFICATION_AMBIGUOUS`
`PROVENANCE_MISMATCH`
`MUTATION_SURVIVED`
`HARNESS_DEFECT`

The test harness MUST NOT modify expected values automatically in response
to implementation failures.

---

## 9. Acceptance Criteria

LFN-CONFORMANCE-002 is considered conformant only when:

- P01 provenance binding passes;
- P02 deterministic replay passes;
- every required P03 mutation is killed;
- P04 taxonomy regression tests pass;
- P05 governance regression tests pass;
- canonical fixtures remain unchanged;
- CI records the exact tested commit;
- no mutation survives silently.

---

## 10. Normative Rule

The laboratory must be capable of proving its own sensitivity to known
violations.

Therefore:

> A test suite that passes the baseline but allows a required mutation
> to survive is NOT conformant to LFN-CONFORMANCE-002.

The specification precedes implementation.

The implementation follows the specification.

The fixtures encode the specification.

The mutation harness attacks the implementation.

CI witnesses the resulting behavior.

No stage may silently rewrite the authority of another stage.

---

## 11. Closure Boundary

When all acceptance criteria pass, the correct conclusion is:

`LFN-CONFORMANCE-002 = LOCAL CONFORMANCE ACHIEVED`

The following conclusions remain prohibited:

`ARCHITECTURE_PROVEN`
`SECURITY_PROVEN`
`UNIVERSALLY_CORRECT`
`PRODUCTION_SAFE`

Those claims require independent evidence beyond this suite.
