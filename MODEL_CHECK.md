# Exhaustive bounded model check — research extension

**Status:** experimental Draft PR #1, **not** included in the archived Zenodo v1.1.1 release. This is finite symbolic analysis, not deployed validation, a cryptographic implementation, or an unbounded impossibility theorem.

## Claim and observation semantics

Let H be all worlds admitted by a **stated finite grammar**; let T(h) be the assumption that a trusted evidence mechanism is authentic and complete (or, for a witness, fresh and bound to the relevant prior checkpoint). Let P(h) be the property computed from the world and O(h) be what the verifier sees.

For evidence o and trust choice t, let C_t(o) = {h in H : O(h) = o and (not t or T(h))}. The verdict is ESTABLISHED when C is nonempty and all members satisfy P; REFUTED when all violate P; NOT_ESTABLISHED when both exist; and INCONSISTENT_EVIDENCE when C is empty. These are **relative logical verdicts**, not probability or confidence scores.

The `trusted()` predicate is an *oracle-side admissibility assumption* about the hidden ground truth. The verifier does not have oracle access to it. In an actual deployment, authentication, completeness, non-bypassability, freshness, crash consistency, trust roots, and log identity need independent evidence or verified enforcement.

## Exhaustively enumerated finite universes

The tool `exhaustive_assurance.py` enumerates the entire Cartesian product of each explicitly restricted trace/evidence grammar; it then **searches** for colliding safe and unsafe histories instead of preselecting the illustrative pairs. The universes cover 20 worlds in total.

| Claim | Enumerated worlds | Trusted worlds | Observation with insufficient information | Necessary strengthened boundary |
| --- | ---: | ---: | --- | --- |
| Authorization at commit | 4 | 2 | An earlier grant and a receipt | Authentic complete policy audit at the execution decision |
| At-most-once effect | 4 | 2 | Receipt for first effect | Authentic, durable and complete ledger for this intent |
| Head monotonicity | 4 | 2 | Current head=1 and local witness=1 | Independent previously attained head bound to this log |
| Prefix continuity | 8 | 4 | Local and witness heights both equal 2 | Independent, authentic checkpoint bound to **content**, not just size |

For each domain, the checks find (a) an ambiguity under baseline evidence even while trusting the strengthened mechanism, (b) established/refuted partitions under **enriched evidence plus the trusted-assumption restriction**, and (c) ambiguity again when that restriction is withdrawn. The trust restriction changes the threat model; it is not an observation the code has proven credible.

**Key correction:** a nondecreasing integer head is weaker than append-only log continuity. A current log `genesis/b` and an earlier witnessed log `genesis/a` have equal heights but incompatible content. A witness containing only `height=2` cannot distinguish them. The prefix example uses exact identity of the full two-record sequence as an idealized token, not a working digital signature or hash-chain consistency proof.

## Limitations and potential invalidating worlds

- **Missing possible histories:** if H omits a valid unsafe history, an apparently unanimous ESTABLISHED verdict may become NOT_ESTABLISHED once that history is restored. A regression test explicitly exhibits this false confidence.
- **Evidence-authenticity assumption:** omitted or fabricated policy/ledger entries and stale or equivocating checkpoints restore indistinguishability despite richer-looking evidence.
- **No real assurance transfer:** the code assumes an atomic complete commit ledger, a trustworthy execution-time audit, and an independent non-rollbackable checkpoint. It does not establish any of these properties in software or hardware.
- **Bounded state grammar:** two possible authorization traces, up to two effects, two head states, and two two-entry prefixes. No concurrency, adversarial scheduling, real cache lifetimes, distributed partition behavior, provenance attacks, fork consistency proofs, signature compromise, or unbounded histories.
- **Identity vs height:** a log prefix comparison is stronger than a scalar index comparison. Actual constructions would need log-ID binding, cryptographic content commitments, and authenticated inclusion/consistency evidence with independent freshness.

## Relevant established mechanisms (not implemented here)

- [RFC 9162, Certificate Transparency v2](https://www.rfc-editor.org/rfc/rfc9162) specifies Merkle-based **consistency proofs** of append-only histories. It also discusses inconsistent views; neither a scalar size nor a local hash alone implements its security model.
- [RFC 9942, COSE Receipts](https://www.rfc-editor.org/rfc/rfc9942) provides verifiable-data-structure proof formats, including inclusion and consistency proofs. A syntactically valid receipt does not by itself prove completeness of *all* agent-caused effects.
- [RFC 9943, SCITT Architecture](https://www.rfc-editor.org/rfc/rfc9943) specifies transparency service/auditor roles and explicit compromise assumptions. This model is not a SCITT implementation or a claim of a missing standard feature.
- [IETF HTTPAPI Idempotency-Key -08](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-08) remains an **Internet-Draft** as of 29 October 2026. It discusses the key uniqueness, payload scope, expiry and server responsibilities relevant to bounding duplicate effects.

The scientific contribution of this PR is the reproducible bounded **countermodel and scope correction**, not a new cryptographic primitive or theorem.

## Reproduction

From a clean checkout of this PR branch:

```bash
python -m unittest discover -s . -p 'test_*.py' -v
python -c "from exhaustive_assurance import model_check; [print(row) for row in model_check()]"
```

The baseline has ten tests, the earlier trace-derived extension adds six, and this exhaustive extension adds ten: **26 unittest methods** (plus parameterized subtests). Matrix CI runs Python 3.10, 3.12, 3.13. Passing tests demonstrates consistency of the stated finite semantics only.

## Publication boundary

These findings should be reviewed in this branch before merging. The stable Zenodo DOI remains a reference to its original archived snapshot; any merged revision will need a distinct versioned release and Zenodo record if it is to be archived.
