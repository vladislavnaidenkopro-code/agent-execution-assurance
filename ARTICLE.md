# When Valid AI Agent Evidence Is Not Enough
## Three reproducible counterexamples to overclaiming execution assurance

**Status:** Public technical note, v1.1; independent peer review not performed  
**Author:** Vladislav Naidenko  
**Date:** 29 October 2026

### Abstract
AI-agent systems frequently use authorization records, execution receipts, and audit snapshots to support claims about action safety. These records can be internally consistent without establishing the stronger claim an operator wants to make. We present three minimal, synthetic counterexamples concerning authorization at execution time, at-most-once effects, and log continuity. The central method is observational indistinguishability: construct two possible execution histories that produce the same verifier-visible evidence but differ in the property of interest. In that case, a sound verifier cannot infer the property from those observations alone. We provide a small executable symbolic demonstration of all three counterexamples and state explicit limits on its conclusions. This is an explanatory research note, not a proof about any deployed product or a claim of a new cryptographic protocol.

### 1. Assurance claims must name their assumptions
Let H be a set of histories permitted by a threat model, O(h) the evidence visible to a verifier for history h, and P(h) the security claim. For observation o, define C(o) = {h in H : O(h) = o}. **When C(o) is empty, return INCONSISTENT_EVIDENCE**, rather than applying vacuous universal quantification. For nonempty C(o), a three-valued verdict is:

- **Established within model:** P(h) holds for every h in C(o).
- **Refuted within model:** P(h) fails for every h in C(o).
- **Not established:** C(o) contains both satisfying and violating histories.

The conclusion is conditional on H, O, and the trust assumptions. This three-valued construction is a standard epistemic/model-checking pattern; we do not claim to have invented it.

### 2. Counterexample A — authorization evidence is not execution-time authorization
**Claim:** Action A on resource R was authorized when it executed.

- History H1: permission for (principal U, A, R) is granted; A executes; receipt is recorded.
- History H2: the same permission is granted, then revoked before execution; A executes; receipt is recorded.
- Verifier sees only the original grant and the action receipt; it has no authenticated, complete record of revocations at execution time.

**Observation:** O(H1) = O(H2), while the authorization claim differs. **Verdict:** NOT_ESTABLISHED. A signed grant alone cannot establish the absence of intervening revocation. A possible remedy is a well-defined authorization decision bound to action identity and execution time, with independently justified freshness and revocation semantics; even that requires stated trust assumptions.

### 3. Counterexample B — authentic receipt is not proof of at-most-once execution
**Claim:** One user intent I caused at most one external effect.

- History H1: effect e1 commits; its authentic receipt is delivered.
- History H2: effect e1 commits; a crash or timeout causes a retry; effect e2 also commits; only the receipt for e1 is delivered.
- Verifier sees the same receipt for e1 in both histories, without a trusted completeness guarantee for all effects of I.

**Observation:** O(H1) = O(H2), but at-most-once differs. **Verdict:** NOT_ESTABLISHED. Receipt authenticity supports an existence claim, not an exhaustive count. Duplicate delivery of one receipt must also not be confused with two distinct effects. Real at-most-once guarantees require appropriately scoped idempotency and durable enforcement at the effect boundary, plus assumptions about key reuse, retention, rollback and side effects.

### 4. Counterexample C — local checkpoint is not proof of non-rollback
**Claim:** The audit history has not been rolled back.

- History H1: a local log and its witness database remain at checkpoint c.
- History H2: the system progresses beyond c; an attacker or failure restores both the log and the mutable local witness database to checkpoint c.
- Verifier sees only the restored log and restored witness database, with no independent, non-rollbackable observation of the later checkpoint.

**Observation:** O(H1) = O(H2), but the non-rollback claim differs. **Verdict:** NOT_ESTABLISHED. Hash-chain integrity and a local witness do not establish freshness if both can be restored together. A remote or hardware-protected anchor may narrow the ambiguity only under explicit availability, freshness, anti-equivocation and compromise assumptions.

### 5. Executable demonstration and results
The companion `counterexamples.py` defines three pairs of manually constructed histories. For each pair, the visible observation tuples are equal while the claimed security property has opposite truth values. `verdict` consequently returns `NOT_ESTABLISHED` for all three pairs. The four original unit-test methods also check positive and negative controls, mismatched observations, and empty inputs. Run `python -m unittest discover -s . -p 'test_*.py' -v` in the repository.

**Interpretation:** This is a constructive, conditional demonstration of indistinguishability under deliberately incomplete observation functions. The program does not discover the histories independently, validate cryptographic artifacts, model a deployed verifier, or establish that the same ambiguity holds under a stronger evidence model. Passing unit tests is not independent scientific validation.

### 6. Conditional sufficiency: constructive models and threat boundaries

The preceding pairs establish only insufficiency under a specified observation function. To establish a positive claim, the strengthened observation and threat model must eliminate **all property-violating compatible histories**, not necessarily all but one history. Multiple safe histories may remain compatible.

| Claim | Trusted components and strengthened evidence | Adversary / failure model | Conditional sufficiency and residual risk |
| --- | --- | --- | --- |
| Authorization at execution | Trusted enforcement at the effect boundary, binding intent, action, resource, policy version and a sufficiently fresh revocation decision | Adversary may replay old grants and hide revocations, but cannot bypass or corrupt the enforcer | If every effect passes a non-bypassable check against the authoritative state at its linearization point, permitted histories satisfy authorization. Compromised enforcer, stale replication or policy ambiguity reopens uncertainty. |
| At-most-once per intent | Durable idempotency ledger and effect commit coordinated atomically, with stable intent IDs and key scope | Crash/retry, duplicate requests and lost receipts allowed; ledger rollback, key expiry and untracked side effects excluded for the positive case | If all effects are covered by an atomic deduplication boundary that survives recovery, compatible histories have at most one committed effect per intent. Rollback, retention expiry and out-of-band effects defeat the guarantee. |
| No rollback | Independent fresh witness with authenticated monotonic checkpoints and verifiable continuity | Local log and local witness may be restored; trusted remote witness cannot be rolled back or equivocate | If a fresh authenticated checkpoint proves a later committed state and verifier checks continuity against it, a restored earlier local head is detectable. Compromised witness, stale reads, network partitions and split views remain hazards. |

These are **conditional engineering proof obligations**, not implemented security controls. The included `assurance_models.py` uses symbolic observation strings such as `enforced:policy-v2:allow` and `external-anchor:latest=d`; it does not verify signatures, implement atomic storage, or attest freshness. A positive symbolic verdict must not be interpreted as evidence that a real deployment satisfies the trusted-component assumptions.

The companion `test_assurance_models.py` checks: baseline ambiguity, conditional establishment and refutation under enriched observations, multiple compatible safe histories, residual ambiguity after withdrawing trust, impossible observations, and an empty model. Combined with four earlier test methods, the package has **ten unittest methods**; each method may contain multiple subtests.

### 7. Practical implications
An evidence verifier should distinguish (i) cryptographic validity of individual artifacts, (ii) evidence that an effect exists, (iii) authorization scoped to the actual action and time, (iv) completeness/freshness of observations, and (v) exactly-once or at-most-once per intent. A positive result must identify the premises that make it valid. Where evidence permits both safe and unsafe histories, reporting NOT_ESTABLISHED is more accurate than asserting security or asserting an attack occurred.

### 8. Limitations and nonclaims
- These examples demonstrate logical insufficiency under stated observations; they are not vulnerabilities in any named vendor or OWASP implementation.
- The symbolic code is a teaching and regression fixture, not a secure receipt protocol, independent third-party benchmark, or cryptographic proof.
- Independent originality review and format compatibility with OWASP are outstanding.
- No private VLADS Future source, internal architecture, infrastructure addresses, or production telemetry are included.

### 9. Reproducibility
Use Python 3 standard library only. Clone this repository and run `python -m unittest discover -s . -p "test_*.py" -v`. The symbolic demonstrations are included here; no separate V34 fixture is needed. The examples are intentionally minimal and their claims are conditional on the chosen observations.

### 10. Related work and originality boundary
This note is an educational synthesis, not a new impossibility theorem. It makes three established engineering boundaries concrete for agent-execution evidence:

- **OWASP Agentic Evidence** centers evidence sufficiency, provenance, and the difference between observed records and independently verified claims. Our three synthetic pairs illustrate those boundaries; we do not claim the project is missing these principles. [1]
- **IETF HTTPAPI Idempotency-Key Internet-Draft (-08, 22 October 2026)** explains idempotency keys, key reuse constraints, expiry, and server-side responsibilities. It is a *draft*, not an issued RFC; our receipt example concerns a different, narrower logical question: what can be inferred from one delivered receipt without evidence completeness. [2]
- **RFC 9162, Certificate Transparency Version 2.0 (2021)** documents append-only logs, Merkle consistency proofs, and independent monitoring. Our local-checkpoint counterexample does not invalidate these techniques; it assumes the verifier has no independent non-rollbackable anchor. [3]

**Contribution boundary:** the contribution is a compact, runnable *explanatory fixture* connecting three failure modes under one observation-equivalence presentation. No originality claim is made for the underlying principles, and this bibliography is selective rather than an exhaustive novelty search.

**Additional related standards:** RFC 9942 (COSE Receipts) and RFC 9943 (SCITT Architecture) discuss receipt and transparency architectures. Neither substitutes for an independently justified completeness or freshness assumption. [4] [5]

**References**
[1] OWASP, *Agentic Evidence*, https://github.com/OWASP/Agentic-Evidence (accessed 29 October 2026).
[2] IETF HTTPAPI WG, *The Idempotency-Key HTTP Header Field*, draft-ietf-httpapi-idempotency-key-header-08, 22 October 2026, https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-08 .
[3] Laurie et al., *Certificate Transparency Version 2.0*, RFC 9162, December 2021, https://www.rfc-editor.org/rfc/rfc9162 .
[4] *COSE Receipts*, RFC 9942, https://www.rfc-editor.org/rfc/rfc9942 .
[5] *SCITT Architecture*, RFC 9943, https://www.rfc-editor.org/rfc/rfc9943 .

### 11. Review and scope
This is an author-approved technical note, not a peer-reviewed publication. The references are selective, not an exhaustive originality search. The examples are synthetic and do not evaluate a deployed system.

**Article license:** Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/ .
**Accompanying Python code:** MIT License; see LICENSE-CODE.txt.
