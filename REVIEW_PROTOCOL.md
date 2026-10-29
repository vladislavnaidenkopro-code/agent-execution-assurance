# Independent critical review protocol — draft research PR

**Scope:** bounded, synthetic execution-assurance models and the *scientific claims*, not any private VLADS Future implementation. The reviewer must be independent of this authoring process. This checklist **does not establish that review has taken place**.

## Materials to review

1. Read [SCIENTIFIC_GATE.md](SCIENTIFIC_GATE.md): threat-model assumptions, the oracle-relative compatibility predicate, adversarial countermodels and original publication HOLD.
2. Inspect the source files: `counterexamples.py`, `assurance_models.py`, `trace_assurance.py`, `exhaustive_assurance.py`, `retry_protocol_model.py`, `external_effect_model.py`, `external_effect_spec.py`, `external_effect_adversarial.py` and their tests.
3. Review the **currently frozen review target by full Git commit SHA**, not a moving `main` or a DOI for an earlier code release. Record the SHA in the review.
4. Inspect [CONCURRENCY_GATE.md](CONCURRENCY_GATE.md) and its finite interleaving generator. Independently analyze at least one two-worker trace and the claimed atomic invariant before accepting the source code's checks.
5. Read the prior works in the reference section below, then review the manuscript *after* it is updated to agree with the code, not the obsolete PDF v0.1.

## Required falsification questions

| ID | Question to answer explicitly | Acceptance criterion |
| --- | --- | --- |
| R01 | Are compatible-world verdicts conditional on a hidden ground-truth `trusted()` predicate? | The paper must label them **oracle-conditional**; a positive result cannot imply real-world assurance without a justified trusted evidence source. |
| R02 | Do different legitimate histories generate exactly the same baseline evidence but opposite property values? | Independently construct or falsify at least one pair for each of authorization, effect count and log continuity. |
| R03 | Does a scalar log-head comparison conceal same-height history substitution? | The review must distinguish index monotonicity from full prefix consistency (including log identity, signed commitments and fresh witnesses). |
| R04 | Do effect→marker, marker→effect and independent remote APIs preserve the claimed invariants under crash/retry? | Reproduce generated shortest witnesses; explicitly reject a local transaction as proof of remote atomicity. |
| R05 | Does the second event specification validate the same hidden assumptions? | Report shared semantic dependencies and perform at least one reviewer-authored transition mutation or independent re-specification; passing matching tests alone is insufficient. |
| R06 | Do remote-key rollback and forged-success responses invalidate the respective positive claims? | Reproduce independently, or provide a counterargument grounded in the stated model. |
| R07 | Are state counts mistakenly presented as risks, empirical failure rates, performance comparisons, or statistically estimated probabilities? | No such interpretations in figures, tables, abstracts or discussions. |
| R08 | Does the model omit relevant concurrency, multiple external effects, dedup expiry, key collisions, crash consistency, policy revocation and log equivocation? | List omitted-world classes and state which positive conclusions do not transfer without new assumptions. |
| R09 | Is the contribution original relative to pre-existing observational-equivalence, dual-write/idempotency and transparency-log research? | Explicit novelty verdict: original result, reproducible explanatory countermodel, or only pedagogical synthesis; justify using primary sources. |
| R10 | Does the manuscript cite the **same reviewed code version**? | Full commit SHA plus reproducible code archive/tag, CI command/results and a **new** software DOI after version freeze; separate DOI for final manuscript. |
| R11 | Does the at-most-once claim survive concurrent workers with the same intent and key? | Reproduce the zero-crash check-then-effect race for 2, 3, and 4 workers; state the assumed linearization point for the atomic endpoint, the missing-effect hazard for reservation-before-effect, and excluded cross-system semantics. |

## Reproduction procedure

From a **clean clone** of the review SHA on Python 3.10, 3.12 or 3.13:

```sh
python -m unittest discover -s . -p 'test_*.py' -v
python retry_protocol_model.py
python external_effect_model.py
python external_effect_adversarial.py
python -c 'from exhaustive_assurance import model_check; [print(row) for row in model_check()]'
```

Repeat at least one bounded configuration after changing the allowed number of attempts/crashes. Do not rely solely on the GitHub Actions success badge. Record any failed command, dependency issue, missing artifact, incorrect expectation or alternative shortest witness.

## Reviewer deliverables

A written review should contain:

- Reviewer name and relevant expertise (or a nonpublic, verifiable identification retained by the author); clear declaration of independence and conflicts of interest.
- Exact code commit SHA, reproducibility environment, test results and whether a truly independent transition specification was implemented.
- Per-ID R01–R11 assessments: **pass / major revision / cannot determine**, with evidence links and actionable proposed changes.
- Explicit comments on each theorem-level assertion, whether proofs are valid within H and O, and whether H is sufficiently justified for the abstract/claims.
- A novelty and publication-suitability conclusion; suggested venue only if warranted.
- Author responses to all major objections, followed by an explicit reviewer decision after changes.

**Acceptance policy:** an unreviewed chatbot answer, successful CI matrix or same-author differential specification is **not** external scientific peer review. PR remains Draft, final manuscript publication remains on HOLD, until review evidence exists and material objections are addressed.

## Essential reference points

- Herlihy & Wing, *Linearizability: A Correctness Condition for Concurrent Objects* (1990): https://doi.org/10.1145/78969.78972
- Lamport, *Specifying Systems* (2002): https://www.microsoft.com/en-us/research/publication/specifying-systems-the-tla-language-and-tools-for-hardware-and-software-engineers/
- Case, *Formal Theory: Structural Assurability* (2026): https://doi.org/10.5281/zenodo.23003560
- IETF HTTPAPI, `draft-ietf-httpapi-idempotency-key-header-08`, **Internet-Draft** (2026): https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-08
- AWS, *Transactional outbox pattern*: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
- RFC 9162, *Certificate Transparency Version 2.0*: https://www.rfc-editor.org/rfc/rfc9162

This file is a review **protocol**, not a claim that a reviewer has been recruited or that the paper is independently validated.
