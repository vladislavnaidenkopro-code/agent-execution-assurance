# Evidence-Limited Assurance for AI-Agent Execution

Public, synthetic research materials by **Vladislav Naidenko**. This project studies what authentic execution records can—and cannot—establish about AI-agent authorization, idempotency and audit-log continuity under explicit, bounded assumptions.

## Published research — latest version

**[When Execution Evidence Is Not Enough: Bounded Countermodels for AI-Agent Authorization, Idempotency, and Log Continuity](https://doi.org/10.5281/zenodo.23817318)**

- **Scientific preprint v0.3.4 (30 October 2026):** [10.5281/zenodo.23817318](https://doi.org/10.5281/zenodo.23817318) — corrected literature positioning and bibliography; **not peer-reviewed**.
- **Preprint v0.3.3 (29 October 2026):** [10.5281/zenodo.23784545](https://doi.org/10.5281/zenodo.23784545) — previous version, retained in the Zenodo version history.
- **Concept DOI for all paper versions:** [10.5281/zenodo.23784544](https://doi.org/10.5281/zenodo.23784544).
- **Reproducible research software v1.2.0:** [10.5281/zenodo.23783618](https://doi.org/10.5281/zenodo.23783618) — separate software archive.
- **Previous software snapshot v1.1.1:** [10.5281/zenodo.23775426](https://doi.org/10.5281/zenodo.23775426) — **not** the source of the v0.3.4 research computations.

The v0.3.4 revision corrects scholarly attribution and presentation; it does not introduce a new security theorem, deployed verifier, or new empirical field results. It remains an **unreviewed preprint**.

## Reproduce the published finite-model experiments

**Exact frozen experimental commit:** [`53f1d4963d604b8d6e108386ebd2f4aebbd2daf6`](https://github.com/vladislavnaidenkopro-code/agent-execution-assurance/tree/53f1d4963d604b8d6e108386ebd2f4aebbd2daf6)

The publication cites this immutable commit rather than the current default branch or the moving head of [Draft PR #1](https://github.com/vladislavnaidenkopro-code/agent-execution-assurance/pull/1). With Python 3 standard library:

```sh
git clone https://github.com/vladislavnaidenkopro-code/agent-execution-assurance.git
cd agent-execution-assurance
git checkout 53f1d4963d604b8d6e108386ebd2f4aebbd2daf6
python -m unittest discover -s . -p 'test_*.py' -v
python reproduce_results.py > model_results.json
python -c "import reproduce_results as r; print(r.sha256_manifest(r.model_data()))"
```

At the frozen SHA, **104 unittest methods** passed on Python 3.10, 3.12 and 3.13 in recorded GitHub Actions CI. The deterministic model-results digest is:

```text
107cd7814ed89696f2539373c25b027961d7382beb0aa3820933a73cca761f94
```

[GitHub Actions evidence](https://github.com/vladislavnaidenkopro-code/agent-execution-assurance/actions/runs/40967290732). Unit-test passes and finite-state counts demonstrate only consistency of the **specified synthetic models**, not completeness of a real threat model, independent peer review, security certification or an assurance guarantee for production AI agents.

## Repository version distinction

**The default `main` branch retains the earlier educational v1.1 code and [technical note](ARTICLE.md).** Its **10 unittest methods** are *not* the 104-method research snapshot. To reproduce the published v0.3.4 article, check out the frozen commit above or consult the v1.2.0 software archive, not `main`.

The enlarged research branch is tracked in [Draft PR #1](https://github.com/vladislavnaidenkopro-code/agent-execution-assurance/pull/1). That PR remains open and unmerged; publication of the paper and code archive does **not** imply a PR merge or production approval.

## Scope, provenance and licenses

The public corpus uses bounded observation-equivalence examples, explicit state-space exploration, crash/retry, effect-boundary and audit-log countermodels. Positive model-relative verdicts rely on stated trust assumptions; in particular, an idealized trusted-world predicate is **not** an implemented evidence verifier. No new general impossibility theorem, live-system security guarantee or external scholarly peer review is claimed.

- Research preprint and article text: **CC BY 4.0** ([article license notice](LICENSE-ARTICLE.md)).
- Public synthetic Python research code: **MIT** ([code license](LICENSE-CODE.txt)).
- No proprietary VLADS Future source code, secrets, private system architecture, customer telemetry or production security evidence is included.
