# Independent external-effect boundary: finite crash/retry model

**Experimental Draft PR #1 only. Not part of the archived Zenodo v1.1.1 snapshot.** This is a small synthetic state machine, not a real network protocol, atomic database, durable message queue, cryptographic receipt, product implementation or independent peer review.

## Research question and result

Can a locally durable outbox provide at-most-once semantics for a separately committed remote effect when the client can crash, lose an acknowledgement, or retry?

**Not by itself.** A separate local commit does not cover the ultimate remote effect. The strongest positive result here requires a durable and stable *remote* idempotency record atomically tied to that effect. A stable client key without server compliance is insufficient. The model also demonstrates why even that conditional at-most-once guarantee is not eventual execution.

## Explicit finite-state experiment

external_effect_model.py enumerates every reachable state from a single pending user intent using BFS, producing shortest counterexample traces for violated properties. Distinct fields represent the durable remote effects, remote key record, local completion, volatile request phase and the number of attempts/crashes/key expirations.

The default bounds are **two attempts, one client crash, one remote server crash and one key expiration**. The initial local outbox entry is assumed durable.

| Mode | Reachable states | At-most-once effects | False completion | Retry exhaustion without effect |
| --- | ---: | --- | --- | --- |
| Outbox only, no remote deduplication | 36 | Counterexample | Not reachable under truthful replies | Reachable |
| Remote key and effect committed atomically, stable key | 30 | Established **within model** | Not reachable under truthful replies | Reachable |
| Atomic remote key can expire | 57 | Counterexample | Not reachable under truthful replies | Reachable |
| Remote effect before non-atomic key write | 44 | Counterexample | Not reachable under truthful replies | Reachable |

The checker distinguishes three properties: (i) at-most-once is a safety invariant over every reachable state; (ii) no-false-completion means the local done marker implies at least one remote effect, assuming truthful responses; and (iii) finite-retry noncompletion is witnessed by a reachable dead-end state with no remote effect. The third property is a bounded counterexample to a guarantee of completion, **not** a proof of unrestricted liveness.

## Mechanically generated shortest counterexamples

**No endpoint deduplication.** The client loses a response after a remote effect has committed and retries:

    begin-request
    remote-commits-effect
    response-is-lost
    begin-request
    remote-commits-effect

Two effects are committed for the one intent, even with zero modeled crashes.

**Remote key expires while the local intent is still pending.**

    begin-request
    remote-commits-effect
    response-is-lost
    begin-request
    endpoint-idempotency-key-expires
    remote-commits-effect

The remote key originally recorded atomically with the effect no longer covers a later replay.

**Endpoint writes the key after the effect and crashes between the two.**

    begin-request
    remote-effect-before-key-record
    remote-server-crashes-before-key-record
    begin-request
    remote-effect-before-key-record

The first effect remains durable, but the remote service never recorded the key. The retry can commit another effect.

**Atomic endpoint key and effect.** Within the modeled stable-key mode, one indivisible remote transition both commits the effect and records its deduplication key. All reachable states satisfy the invariant remote_effects = int(remote_key_recorded), so there is no second effect in the explicitly bounded grammar. This is an **assumed endpoint transaction**, not a method for making two unrelated systems atomic.

**Noncompletion despite a stable endpoint key.** Two attempts may fail to reach the endpoint. The outbox remains pending with no remote effect, and a finite retry budget can be exhausted. A successful remote commit may also have no delivered acknowledgement. At-most-once does not imply execution, local completion, or exactly-once acknowledgement.

## Assumptions and missing attack surface

1. **One** intent, one stable request key/payload, one logical effect. No key collisions, payload mismatches, tenant confusion, concurrent calls, compensations, chained downstream effects or Byzantine behaviour.
2. Remote key storage and external effect are assumed truly atomic and durable **only** in the two labeled atomic endpoint modes. A local database transaction plus an unrelated HTTP call does not satisfy this boundary.
3. Client responses are authentic and causally downstream of an actual effect. A malicious server forging success or out-of-band effects would invalidate the no-false-completion inference.
4. The stable remote key survives every replay represented in this state space. The expiring-key mode explicitly relaxes that assumption. There is no clock/TTL unit, remote storage rollback, or independently verified key retention policy.
5. Crashes reset only the modeled volatile phase; durable effect and local completion do not roll back. No out-of-order concurrency, split brain, unbounded retry schedules, fairness, server availability, permanent delivery failure, or remote ledger truncation is modeled.
6. Exhaustiveness means **all reachable states of this specified finite transition grammar**, not all possible executions of a real API.

Before claiming a real-world at-most-once guarantee, independently verify stable per-intent identity and payload scope, actual remote effect+key atomicity or endpoint-enforced deduplication, persistence and key retention for the entire replay window, endpoint-side recovery after crash, and the absence of uncovered secondary effects.

## Reproduction

    python external_effect_model.py
    python -m unittest discover -s . -p 'test_*.py' -v

The new fixture adds **18 test methods**: model graph-size assertions, generated and replayed shortest witnesses, client/server failure cases, expiration sensitivity, no-false-completion invariants, independent DFS/BFS state-set comparison, and 18 parameter configurations for the atomic endpoint invariant. The research branch has **57 unittest methods** in total (including the 39 previously published in Draft PR #1), plus subtests. CI results must be checked separately.

## Prior art and interpretation

- [IETF HTTPAPI, The Idempotency-Key HTTP Header Field, draft-ietf-httpapi-idempotency-key-header-08](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-08), 22 October 2026. This is an **Internet-Draft**, not a published RFC. Its considerations include key uniqueness, fingerprint/payload scope, expiry, and resource responsibility; clients cannot assume a server honors an unadvertised key.
- [AWS Prescriptive Guidance, Transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) notes that duplicate publications can occur and consumers should be idempotent.
- [Chris Richardson, Idempotent Consumer pattern](https://microservices.io/patterns/communication-style/idempotent-consumer.html) describes consumer-side transactionally recorded message identifiers.

**Contribution boundary:** an executable and auditable bounded countermodel of established distributed-system failure modes, not a new algorithm, formal impossibility theorem, proof of system-level atomicity or vendor vulnerability.
