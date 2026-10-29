# Evidence-Limited Assurance for AI-Agent Execution

**Zenodo DOI:** [10.5281/zenodo.23775426](https://doi.org/10.5281/zenodo.23775426) (repository archive; confirm version metadata on Zenodo record).

**Version 1.1 · Author: Vladislav Naidenko**

A reproducible technical note on when agent-execution evidence is insufficient, when strengthened observations can establish a claim **within explicit trust assumptions**, and how residual risks restore ambiguity.

Read [ARTICLE.md](ARTICLE.md). Run all **10 unit-test methods** using Python 3 (standard library only):

```sh
python -m unittest discover -s . -p 'test_*.py' -v
```

The repository includes three manually constructed counterexample pairs, three conditional-sufficiency scenarios, residual-risk examples and an `INCONSISTENT_EVIDENCE` verdict for impossible observations. These are symbolic finite-world demonstrations, **not implementations** of cryptographic verification, atomic commit, or authorization enforcement. The note has **not** undergone independent peer review.

**Licenses:** Article CC BY 4.0 ([notice](LICENSE-ARTICLE.md)); Python source MIT ([license](LICENSE-CODE.txt)). No private VLADS Future implementation is included.
