# Scientific gate — two concurrent workers, one intent

**Status:** 2026-10-29 · experimental Draft PR #1 · PUBLICATION HOLD. This document and code do **not** belong to the archived Zenodo v1.1.1 snapshot. This is same-author bounded verification, **not independent peer review**.

## Research question

The existing crash/retry models have one active executor at a time. Do the positive guarantees survive **two workers** processing the *same stable intent key* concurrently, with **no crash, no timeout and no key expiration**?

Not under a non-atomic check-then-effect-then-mark endpoint. The statement is a familiar check-then-act race; this file provides a small executable witness, **not a novel distributed-systems theorem**.

## Finite operational semantics

`concurrent_effect_model.py` starts with two workers `w0, w1` in `ready`, a single shared remote key `K=False`, and zero committed effects `E=0`. Every step executes one labeled transition. Interleavings are exhaustive over the declared finite transition graph; breadth-first search returns a shortest path to a violation. Both workers represent **one intent**, not two separate legitimate actions.

Three endpoint modes are compared:

1. `check_then_effect_then_mark`: each worker reads `K` separately; when absent it may later commit an effect, then record `K=True`. The read is **not** a reservation or atomic claim.
2. `reserve_then_effect`: the first worker atomically records `K=True` before doing the effect; it can crash in between. This never creates two effects within the model, but a completed dedup response can misstate actual execution.
3. `atomic_effect_and_key`: for a missing key, the effect and key record are changed **in the same abstract indivisible step**. A worker arriving later sees the key and finishes without a second effect.

## Generated results (counts of abstract states; NOT probabilities)

| Protocol | Reachable states | Duplicate effect reachable? | Terminal without external effect reachable? |
| --- | ---: | --- | --- |
| Check → effect → mark | 17 | **YES**, without any crash | No |
| Reserve key → effect | 12 | No | **YES**, after crash |
| Truly atomic effect + key | 4 | No | No |

### Shortest duplicate-effect witness

```text
w0:check-key-absent
w0:commit-effect
w1:check-key-absent
w1:commit-effect
```

At the third step, `K=False` because worker 0 committed the effect but has **not** recorded the key. Therefore worker 1 independently passes the check. Two effects exist after the fourth step for one intent. There are no crashes, retries, network failures or Byzantine operations in this witness. The initial two-worker overlap is sufficient.

### Reservation-before-effect: an opposite failure

```text
w0:reserve-key
w0:crash-before-effect
w1:observe-dedup-key
```

Here the shared key is recorded, both workers are no longer able to commit an effect, but `E=0`. A reservation is therefore not proof that an external effect occurred. The model intentionally has no reservation recovery or lease expiry; a properly designed state machine might recover this intent using additional states and a recovery protocol.

## Proof obligations within the declared transition relation

**P1 (conditional atomic safety).** In the atomic-effect-and-key mode, invariant `I(s) := E(s) = 1[K(s)]` holds for every reachable state. Initially `E=0,K=False`. An atomic-commit transition can occur only while `K=False` and yields `E=1,K=True`. The deduplicated-worker transition leaves both fields unchanged. No other action increments effects, so induction preserves `I`, which implies `E≤1`. The exhaustive enumerator visits all **four** states of this *specific graph* as a secondary check. This proof is **not** a proof that a real endpoint has an atomic linearization point.

**P2 (reserve-first safety is not execution).** The reserve-first mode has no second reservation once `K=True`, hence at most one worker can enter the `claimed` phase and perform one effect. However, a `crash-before-effect` transition from `claimed` permits terminal `E=0`; at-most-once is compatible with **zero** completed effects. An observed key or dedup response cannot itself establish effect existence.

**P3 (check-then-act counterexample).** The four-step witness above is a valid path of the transition relation ending at `E=2`. Therefore `E≤1` is **not invariant** in that mode. This is an existence counterexample, not an estimated failure rate.

## Independent-check boundary

The test suite performs: BFS exploration; a separately implemented DFS reachable-state walk; shortest witness replay; worker-renaming symmetry; explicit graph cardinalities; and exhaustive local successor checks for the atomic-mode invariant. These are meaningful regression checks but **share the same event semantics and authoring process**. Neither a separately authored TLA+ specification nor a qualified external research review has been completed.

## Threat exclusions and scientific limitations

- Exactly **two workers, one stable key and one logical effect**, no real concurrent machine operations: each abstract step is serialized by the model-checker. This does **not** assert actual concurrency is globally serialized; the non-atomic endpoint is specifically decomposed into multiple operations whose interleavings are explored.
- The atomic endpoint is **assumed linearizable** and covers the committed external effect. Merely using a local database transaction or holding an application-level lock does not establish this remote atomicity across systems.
- No key expiration, marker rollback, forgery, authorization changes, duplicate downstream effects, network timeouts, split brain, durable crash recovery, partial compensation, multiple tenant scopes, or policy/version mismatch.
- No fairness/liveness theorem: the 'terminal without effect' claim is scoped to the modeled finite protocol and represents a **reachable deadlock**, not a universal impossibility of eventual recovery.
- No production measurements, probabilities, empirical reliability comparisons or security certification. Counts 17/12/4 depend on the chosen state abstraction and cannot be compared as performance metrics.

## Verified prior art (not claimed as novel)

- Herlihy and Wing, *Linearizability: A Correctness Condition for Concurrent Objects*, ACM TOPLAS (1990), https://doi.org/10.1145/78969.78972 .
- AWS Prescriptive Guidance, *Transactional outbox pattern*, https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html — duplicate delivery and downstream idempotency are explicit considerations.
- Jena, Dalal, and Tishkin, *The Idempotency-Key HTTP Header Field*, `draft-ietf-httpapi-idempotency-key-header-08` (22 October 2026), https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-08 — **work in progress**, not an RFC; server responsibility, uniqueness and expiry are important.

## Reviewer gates

A reviewer should challenge (i) whether the abstract atomic endpoint models a realistic remote effect boundary, (ii) whether omitted concurrency events permit a more serious violation, (iii) whether the new research adds a result beyond established check-then-act and dual-write counterexamples, and (iv) whether these findings belong in a paper as **educational executable countermodels** rather than an originality claim. Independent external review is still a publication blocker.

Reproduce: `python -m unittest discover -s . -p 'test_*.py' -v`; `python concurrent_effect_model.py`.
