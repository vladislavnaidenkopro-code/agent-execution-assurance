# Scientific gate: threat-model expansion and differential specification

**Date:** 2026-10-29  
**Status:** INTERNAL RESEARCH VALIDATION ONLY — **PUBLICATION HOLD / MAJOR REVISION**  
**Review independence:** All work in this gate was prepared by the same AI-assisted development process. The second specification is differently structured, **not externally independent peer review**. This gate does not authorize publication of the 9-page draft as final.

## 1. Critical distinction: truth-conditioned classification versus evidence verification

The finite-world classifier uses

`C_T(o) = {h in H : O(h)=o and T(h)}`.

Here `T(h)` is a predicate over the **hidden true history**, expressing *assumed* completeness/freshness of observation. An observer cannot generally evaluate `T(h)` from a receipt alone. Hence `ESTABLISHED_WITHIN_MODEL` under `require_trust=True` is an **oracle-conditional mathematical verdict**, not a practical verifier implementation. No cryptographic trust anchor, sound revocation oracle, effect ledger, audit witness, or source of completeness has been built or proved.

For any deployment claim, the missing obligations are: authenticated observation provenance, complete effect coverage, stable intent identity/scope, non-bypassable enforcement, durability, replay-window/key retention, isolation against concurrency, freshness, log identity and continuity, and explicit recovery behavior after loss/rollback. A failure of any critical obligation may expand `H` with worlds missing from this model.

## 2. Full-edge differential check of a second specification

`external_effect_spec.py` declares one guard and one post-state substitution for each of the **13 labeled actions** of the original `external_effect_model.py`. It does **not invoke the original transition function**. The test `test_external_effect_spec.py` compares **the complete labeled outgoing edge set** at every reachable state across **four modes and four different parameter sets**, not merely the counts 36/30/57/44. Tests also deliberately delete a response-loss edge and corrupt the atomic key-recording transition; the comparison detects both mutations.

**What this supports:** the two Python formulations agree under the tested bounded-state grammar, and the test is sensitive to two representative semantic faults.

**What this does not support:** an external formal-verification claim, an independent human review, or the completeness of the grammar. Both formulations could share conceptual errors, especially assumptions about remote persistence and truthful receipts. A separately authored TLA+/Alloy/Lean specification with independent execution/review remains desirable.

## 3. Previously excluded worlds are now explicit transitions

The original `endpoint_atomic_key` model excludes remote dedup-key rollback and forged success responses. `external_effect_adversarial.py` adds these as separately named, bounded actions while preserving all original transitions. It is **not** a statement that a deployed vendor system is vulnerable.

| Remote-key rollback allowed? | Forged response allowed? | Bounded reachable states | At-most-once effect | No false local completion |
| --- | --- | ---: | --- | --- |
| No | No | 30 | HOLDS within model | HOLDS within model |
| Yes | No | 57 | **VIOLATED** | HOLDS within model |
| No | Yes | 44 | HOLDS within model | **VIOLATED** |
| Yes | Yes | 75 | **VIOLATED** | **VIOLATED** |

All counts are **abstract state counts** with two client attempts, one crash budget and at most one instance of each adversarial event. They are not measured probabilities, reliability metrics or system benchmarks.

### Generated, replayable shortest counterexamples

**Dedup-key rollback breaks at-most-once:**

```text
begin-request
remote-commits-effect
response-is-lost
begin-request
adversary-erases-remote-dedup-key
remote-commits-effect
```

At termination of this witness, the same intent has caused two committed external effects.

**Forged success breaks completion inference:**

```text
begin-request
adversary-forges-success-response
mark-local-outbox-done
```

The model reaches `local_done=True` with `remote_effects=0`.

These illustrate how weakening **different trust assumptions** falsifies **different positive claims**. Disabling both added actions reproduces the original graph (30 states). This is a bound-sensitive causal check, not a new impossibility theorem.

## 3A. Parallel-worker threat expansion: no crash needed

A new [finite interleaving checker](CONCURRENCY_GATE.md) explicitly explores 1–4 workers issuing the same intent/key. It falsifies an at-most-once claim when the endpoint separately checks absence, commits an effect, and records the idempotency key. The two-worker shortest path is four steps and requires **no failure**: first worker checks and commits; while its key is still absent, the second worker checks and commits. Three and four concurrent workers can likewise each commit once before any stores the key.

**Positive claim is restricted:** under an assumed single linearizable operation atomically committing the ultimate remote effect and key, the model maintains `E = 1[K]`. Reservation-before-effect prevents duplicates but can lose execution if its reserving worker crashes. Neither result proves atomicity of a deployed external API, and the four-worker finite check is not an unbounded scheduler proof. [Herlihy–Wing (1990)](https://doi.org/10.1145/78969.78972) establishes the existing linearizability framework; no new theoretical priority is claimed.

Independent review must now also cover [R11](REVIEW_PROTOCOL.md) on the exact concurrency/atomicity boundary. All model counts are abstract reachable-state cardinalities, not probabilities.

## 3B. Primary commit versus downstream side-effect coverage

The latest [fanout model](FANOUT_GATE.md) separates a legitimate primary effect P and a different authorized downstream effect D. A single user intent may legitimately require **both**. The appropriate safety claims are `P <= 1` and `D <= 1` separately, not `P+D <= 1`. This matters because a seemingly natural global effect-count bound would reject legitimate workflows.

The bounded checker assumes the primary effect and local intent marker are atomically committed. Nevertheless, lost downstream acknowledgement followed by event redelivery yields `P=1,D=2` when the final downstream endpoint lacks a stable, effective idempotency boundary. Endpoint-side key expiry and crash before key persistence produce separate witnesses. The positive downstream result requires atomic effect+marker at the **final downstream endpoint**, immutable key scope and the absence of uncovered secondary effects. It does **not** follow from the primary transaction.

Four bounded downstream grammars contain 10 / 10 / 20 / 17 abstract states. Sixteen test methods include BFS/DFS agreement, shortest trace replay, conditional positive controls, crash/expiry counterfactuals and explicit evidence that acknowledgement is not a global at-most-once proof. Reviewer [R12](REVIEW_PROTOCOL.md) requires independent inspection of the end-to-end effect coverage.

## 4. Claim-to-evidence contract

| Scientific statement | Exact observation/assumption | Program evidence | Strength |
| --- | --- | --- | --- |
| Compatible safe and unsafe histories imply NOT_ESTABLISHED | Both property values occur in nonempty `C(o)` | `exhaustive_assurance.py`, 20 synthetic worlds | Definitional consequence |
| Equal log height does not guarantee prefix continuity | Two different two-record sequences with the same length | `PrefixContinuityTrace` | Valid bounded counterexample |
| Effect→marker allows duplicate after crash | Remote effect persists; marker not yet durable | `retry_protocol_model.py` BFS | Reachable witness |
| Marker→effect can suppress intended effect | Marker persists; effect absent; retry checks marker | Same | Reachable witness |
| Endpoint atomic key+effect prevents duplicate | True same-boundary atomicity, immutable key, no secondary effects | `external_effect_model.py` | **Conditional**, not verified externally |
| Remote key rollback permits duplicate | Excluded rollback event admitted | `external_effect_adversarial.py` BFS | Reachable witness under expanded model |
| Forged success permits false local completion | Excluded dishonest response admitted | Same | Reachable witness under expanded model |
| Finite retry budget cannot guarantee completion | Two dropped requests and no fairness assumption | `external_effect_model.py` | Bounded negative result, not liveness proof |
| Evidence completeness/authorization at runtime | A hidden `T(h)` condition filters worlds | `trace_assurance.py` | **Oracle-conditional**, no practical verifier |

## 5. Prior art and what is not novel

The methodology is a **reproducible explanatory family of bounded countermodels**. Observation equivalence, crash/dual-write problems, endpoint idempotency, linearizability and log consistency predate this work. Do **not** state a new theorem, protocol, vulnerability, universal safety guarantee, production deployment result or peer-reviewed discovery.

Relevant verified sources:

- M. P. Herlihy and J. M. Wing, *Linearizability: A Correctness Condition for Concurrent Objects*, **ACM TOPLAS 12(3), 463–492 (1990)**, https://doi.org/10.1145/78969.78972 . The present bounded serial model does not verify a concurrent linearization point.
- L. Lamport, *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers*, Addison-Wesley (2002), https://www.microsoft.com/en-us/research/publication/specifying-systems-the-tla-language-and-tools-for-hardware-and-software-engineers/ . The current scripts are **not TLC-checked**.
- Denise M. Case, *Formal Theory: Structural Assurability*, Zenodo, https://doi.org/10.5281/zenodo.23003560 . Earlier related Lean 4 work formalizes claim-relative evidentiary capabilities and observational indistinguishability; priority is not claimed.
- Jena, Dalal, Tishkin, *The Idempotency-Key HTTP Header Field*, **draft-ietf-httpapi-idempotency-key-header-08** (22 Oct 2026), https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-08 . This is an **Internet-Draft, not an RFC**. Resource operators must specify key validity, expiry and enforcement.
- AWS Prescriptive Guidance, *Transactional outbox pattern*, https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html . The pattern acknowledges duplicate delivery and recommends idempotent consumers.

## 6. Publication gates after this change

- **G1 — Mathematical claim scope:** Partially addressed by this document. The original manuscript `v0.1` must be rewritten to distinguish assumption-conditioned assurance from an actual evidence verifier and to separate safety, liveness and truthful acknowledgement.
- **G2 — Finite-model cross-check:** New edge-level differential tests and mutation controls implemented. This is **same-author verification**, not external independence; bounded concurrent workers and downstream effects are now modeled, but unbounded concurrency, multiple kinds of downstream fanout and real remote-integration semantics remain unmodeled.
- **G3 — Prior-art and originality:** Citations cross-checked, but an exhaustive novelty study and external specialist assessment are pending.
- **G4 — External critical review:** **OPEN / BLOCKING.** Must obtain an independent written review of threat-model completeness, proof obligations, claims, mathematics, and reproducibility.
- **G5 — Frozen reviewed software and manuscript:** **OPEN / BLOCKING.** No new release or article DOI before review and version freeze.

**Do not** repurpose the existing Zenodo DOI `10.5281/zenodo.23775426` as a citation to the expanded research PR or its unreleased PDF. Keep PR #1 Draft and keep `main` unchanged except previously published citation metadata.
