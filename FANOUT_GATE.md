# Fanout gate: local intent atomicity is not end-to-end effect atomicity

**Research branch only — PUBLICATION HOLD.** This is a bounded synthetic experiment, not a proof about any deployed system or novel result.

## Scope and formal question

One user intent legitimately causes **two distinguishable effects**: a primary database/action effect P and a downstream notification/webhook/task effect D. Define the safety properties **P-at-most-once**: `P <= 1` and **D-at-most-once**: `D <= 1` separately. There is no general reason to require `P+D <= 1`, because both effects are authorized parts of the workflow. This distinction fixes a potential specification error: counting all side effects as duplicates would reject legitimate fanout.

The model gives the primary handler a strong advantage: `primary_effects=1` and `primary_marker=True` occur in **one indivisible abstract transition**, and this state persists. The downstream event then enters a second effect boundary, whose deduplication rules are examined independently.

## Exhaustive finite results

`multi_effect_model.py` enumerates every reachable state under **one intent, one primary and one downstream effect type, at most two downstream deliveries, at most one remote crash, and at most one downstream key expiry**. The chosen state grammar yields:

| Downstream endpoint contract | Reachable abstract states | P-at-most-once | D-at-most-once |
| --- | ---: | --- | --- |
| No downstream dedup | 10 | HOLDS | **VIOLATED** |
| Remote effect and key committed atomically, never expires | 10 | HOLDS | HOLDS within model |
| Atomic remote key may expire before replay | 20 | HOLDS | **VIOLATED** |
| Downstream effect precedes non-atomic remote key; crash is allowed | 17 | HOLDS | **VIOLATED** |

These counts are **not reliability rates, performance scores, severity values or observed probabilities**.

### Shortest no-dedup counterexample

```text
atomic-primary-effect-and-intent-marker
deliver-outbox-event
commit-downstream-effect
lose-downstream-acknowledgement
deliver-outbox-event
commit-downstream-effect
```

The resulting state has **P=1** and **D=2**. The primary effect and its intent marker remain atomic and durable throughout. Thus proving primary at-most-once says nothing about at-most-once for every downstream effect. A truthful downstream acknowledgement, when delivered, implies existence of both effects in the model; it does not imply D-at-most-once.

### Independent boundary failure modes

- **Key expiry:** a remote endpoint commits D and its key; acknowledgement is lost; the key expires; a second delivery can commit D again.
- **Non-atomic key persistence:** the endpoint commits D, then crashes before recording the downstream dedup key; the retry can commit another D.
- **Atomic downstream key:** under the strong assumption that the final downstream effect and its stable marker are one indivisible durable operation, every reachable state satisfies `D = 1[downstream_marker]`. This is an abstract-model invariant only.

## Scope limitations

The model excludes downstream fanout beyond one effect type, recursion/chained events, simultaneous dispatchers, transaction isolation, malicious success responses, compensation, partial-effect durability, idempotency-key collisions, intent-key scope confusion, policy revocation, network authentication, Byzantine effects, arbitrary event loss, and out-of-band commits. The initial outbox entry is modeled as durably enqueued by the primary commit. The primary transaction and downstream transaction have **no shared atomicity**.

A finite retry budget and the lack of scheduling fairness preclude a general liveness claim. The `downstream_guaranteed` negative control allows zero delivery attempts, giving a reachable state with P=1 and D=0. In the default grammar, arbitrary delivery loss is not represented: a positive liveness claim from that omission would be invalid.

The source contains **16 new unittest methods**: replayed shortest witnesses, no-crash/no-expiry controls, independent BFS/DFS state-set comparison, effect durability monotonicity, truthful-acknowledgement controls and invalid inputs. As of this extension the research branch contains **100 unittest methods** (prior 84 + 16); current CI must be checked separately.

## Scientific contribution boundary

This is a well-known distributed-systems pattern, represented as an auditable finite countermodel. It establishes a useful *scope distinction* between per-intent and per-effect safety, not a new impossibility theorem. Before making a deployment-level assurance claim, define the full set of effects covered by the intended property, enumerate downstream idempotency boundaries and separately substantiate each trust assumption.

Related: [AWS Transactional Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html), [IETF HTTPAPI Idempotency-Key draft -08](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-08), and [Herlihy & Wing 1990](https://doi.org/10.1145/78969.78972). The IETF document is a **draft, not an RFC**. This is **same-author model checking**, not external peer review. No new DOI or final manuscript release is authorized by this model.
