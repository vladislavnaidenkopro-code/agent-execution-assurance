# Research-data reproducibility gate (Draft PR only)

**Publication status:** HOLD / MAJOR REVISION. No final paper, new software release or Zenodo DOI is implied by this file.

## Purpose

Figures and experimental tables in the final scholarly manuscript must be **generated from a frozen, exact code commit**, not copied from a previous PDF or manually updated as new models are added.

The standalone standard-library command

```sh
python reproduce_results.py > model_results.json
python -m unittest discover -s . -p 'test_*.py' -v
```

creates a structured JSON report of finite model state counts and the **shortest generated violating action paths**. Its domains cover:

- Observational equivalence under bounded finite-world grammars;
- Sequential retry/commit ordering;
- External endpoint idempotency with and without key expiration and non-atomic writes;
- Remote-key rollback and forged-response adversarial expansions;
- Two concurrently executing workers sharing one stable intent;
- A primary transaction with a separately delivered downstream side effect.

The canonical JSON string uses sorted keys, UTF-8 and fixed separators. `sha256_manifest(model_data())` yields a digest of **model results**, not a cryptographic attestation of reviewer independence, data provenance or a Git commit tree.

**Current expected output digest:**

```text
107cd7814ed89696f2539373c25b027961d7382beb0aa3820933a73cca761f94
```

`test_reproduce_results.py` checks that digest and verifies a negative control: modifying a state count causes verification to fail. Any legitimate change to a model that changes this digest requires an explicit claims/figures review. **Never just update the expected digest to turn CI green.**

The reported counts are numbers of reachable **abstract states** for different finite transition grammars, not empirical error rates, performance comparisons, security probabilities, confidence intervals or benchmark scores. The counts must not be plotted as if larger state spaces implied weaker security. For scientific figures, prefer a **claim–assumption–counterexample matrix**, transition diagrams and extracted witness paths. Reserve cardinalities for methodology tables or appendices.

## Three levels of evidence, kept separate

1. **Code reproducibility:** tests and deterministic summaries pass on a recorded code commit in independent execution environments. GitHub Actions 3.10/3.12/3.13 is useful here.
2. **Scientific validity:** predicates, admissible world grammars, evidence assumptions and conclusions are justified by formal argument and a critically assessed threat model. Code tests alone cannot establish this.
3. **Independent scientific review:** an expert outside the authoring process reads and challenges claims, verifies the code at an exact SHA, assesses novelty and provides a written review. This remains **OPEN / BLOCKING**.

## Submission sequence

Independent scientific review and resolution of major comments -> approved code freeze (full SHA) -> rerun CI and this evidence manifest on that SHA -> create a new tagged software release and archive with a **new software DOI** -> regenerate all figures from this source -> revise human-approved LaTeX manuscript -> create a **separate paper/preprint DOI** -> optional external venue submission according to its policies.

The existing Zenodo DOI `10.5281/zenodo.23775426` refers to a previous software snapshot and **cannot identify this unreleased research branch**. An AI-text watermark assessment such as [TextGrain](TEXTGRAIN_PROVENANCE_REVIEW.md) is a separate provenance topic, not validation or invalidation of our security findings.
