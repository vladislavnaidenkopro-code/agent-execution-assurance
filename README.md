# Evidence-Limited Assurance for AI-Agent Execution

**Research branch: UNREVIEWED / Draft PR #1 — publication HOLD**

**Author:** Vladislav Naidenko

This branch extends the published educational v1.1 technical note with bounded state-space and observational-equivalence research models. **It has NOT been archived or externally peer reviewed, and must NOT be cited as the archived v1.1.1 code.**

The earlier repository archive DOI [10.5281/zenodo.23775426](https://doi.org/10.5281/zenodo.23775426) identifies a **previous code snapshot**, not the expanded research branch. The branch is not a proof of security for a deployed AI agent or an original impossibility theorem.

## Start here

- [Scientific publication HOLD and threat models](SCIENTIFIC_GATE.md)
- [Independent external review protocol](REVIEW_PROTOCOL.md)
- [Canonical data generation for figures/tables](REPRODUCIBILITY_GATE.md)
- [Observational equivalence and bounded universes](MODEL_CHECK.md)
- [Crash/retry and external endpoint idempotency](RETRY_MODEL.md) and [EXTERNAL_EFFECT_BOUNDARY.md](EXTERNAL_EFFECT_BOUNDARY.md)
- [Two-worker concurrency and linearization boundary](CONCURRENCY_GATE.md)
- [Distinct primary vs downstream effect obligations](FANOUT_GATE.md)
- [TextGrain provenance analysis (separate from scientific evidence)](TEXTGRAIN_PROVENANCE_REVIEW.md)
- [Optional OWASP Agentic Evidence contribution gate (not submitted)](OWASP_CONTRIBUTION_GATE.md)

## Reproduce the entire experimental branch

Python 3 standard library, no external Python dependencies:

```sh
python -m unittest discover -s . -p 'test_*.py' -v
python reproduce_results.py > model_results.json
python reproduce_results.py --verify model_results.json
```

The research branch currently contains **113 unittest methods** (plus parameterized subtests). GitHub Actions checks Python 3.10, 3.12, and 3.13. The seven OWASP candidate vectors are local experimental fixtures, **not an adopted OWASP format or contribution**. Passing CI and manifest checks establishes reproducibility of **specified finite semantics only**. Independently authored scientific review is outstanding.

## Publication boundaries

Do not merge, publish an updated paper DOI, or represent results as peer reviewed until the critical scientific comments are resolved, code is frozen to a full commit SHA, and an external review is documented. State counts are not observed probabilities, risks, or performance benchmarks. Positive verdicts are conditional on explicit trust and effect-completeness assumptions.

**Licenses:** article CC BY 4.0 ([notice](LICENSE-ARTICLE.md)); public synthetic Python sources MIT ([license](LICENSE-CODE.txt)). No private VLADS Future implementation is included.
