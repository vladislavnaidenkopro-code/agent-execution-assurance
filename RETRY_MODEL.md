# Crash/retry boundary: a finite-state protocol experiment

**Status:** experimental branch-only extension. This file and its model are **not part of Zenodo v1.1.1** and have not been independently peer reviewed. No production, cryptographic, or third-party code is included.

## Why this matters

The earlier finite-world histories assigned outcomes by choosing valid/invalid evidence cases. Here `retry_protocol_model.py` instead defines a deterministic transition relation and **exhaustively explores reachable protocol states** with breadth-first search (BFS), yielding the shortest counterexample action trace for each violated property.

A single intent and its durable idempotency marker are subjected to **at most two execution attempts and one crash**, with all interleavings permitted by the specified transition system. A crash erases volatile handler progress but not the durable marker or already committed external effects. An acknowledgement is a separate step and can be absent despite a committed effect.

| Protocol | Reachable states (default bounds) | Duplicate effects reachable? | Finished without any effect reachable? |
| --- | ---: | --- | --- |
| Effect → mark | 17 | **Yes** | No |
| Mark → effect | 14 | No | **Yes** |
| Atomic effect + mark | 10 | No | No |

`Effect → mark` allows the sequence `begin-attempt → commit-external-effect → crash-lose-volatile-phase → begin-attempt → commit-external-effect`; the first external effect survives, but the marker was never recorded.

`Mark → effect` avoids this duplicate at the cost of a different failure: `begin-attempt → write-durable-marker → crash-lose-volatile-phase → retry-reads-durable-marker`. The retry suppresses the first effect, which never happened.

In the `atomic` model the effect and the durable marker change **as one indivisible transition**. From the initial state `effects=0, marker=False`, every transition maintains the invariant `effects == int(marker)`, so at-most-once is preserved across crash and retry **within this precise model**. The model still allows a committed effect with a missing acknowledgement.

## Threat boundary and nonclaims

- The atomic transition is **assumed**, not implemented. It is a valid abstraction only when effect and marker truly share a transaction boundary, or the ultimate external effect endpoint itself enforces idempotency. A local ledger transaction does **not** atomically commit an independent external API or payment unless an additional, justified protocol is in place.
- No inference about exactly-once delivery follows: the external effect can commit without an acknowledgement. No general liveness follows: a scheduler might stop, retries may be exhausted, an endpoint might remain unavailable, and the bounded model does not enforce fairness.
- The `finished without any effect` check is a deliberately **narrow finite-state property**, not proof of end-to-end liveness or universal absence of lost requests.
- The failure model has one intent, up to two attempts, one crash, ideal durable storage, no Byzantine agents, no marker expiry/rollback, no concurrency, no key collisions, and no compensating or multiple downstream side effects.
- A passing test here is evidence about these **declared transitions**, not deployment safety. Adversarial events absent from the transition grammar are not covered.

## Reproduction

```sh
python retry_protocol_model.py
python -m unittest discover -s . -p 'test_*.py' -v
```

Each generated counterexample is returned as a shortest path through the model's reachable-state graph. This finite-state result is a more meaningful engineering demonstration than simply assigning safe/unsafe labels to observations, but it remains conditional on the transition relation. The accompanying references remain the [IETF HTTPAPI Idempotency-Key draft](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-08) and standard transaction/idempotency semantics; the draft is not misrepresented as an RFC.

**Scientific review gate:** compare the assumed atomic transition against concrete target-system commit boundaries before claiming any system-level guarantee. The research PR stays Draft until that review.
