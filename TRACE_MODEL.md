# Post-release trace model — research extension

**Status:** experimental work after the archived `v1.1.1` release. Not part of that Zenodo snapshot, not independently peer reviewed, and not an implementation of trusted enforcement, atomic commit, or external witnessing.

The original symbolic fixtures assign `safe` to a history and assign its observation strings. This extension addresses that **methodological weakness** by computing the property and observation from separate fields in bounded event traces. Evidence may be incomplete even when events are present. `require_trust=True` limits the set of compatible histories to a completeness/freshness assumption for the relevant evidence mechanism.

| Domain | Property computed from ground-truth trace | Baseline observation | Enriched observation | Trust assumption and failure |
|---|---|---|---|---|
| Execution-time authorization | Whether a `revoke` occurred before `commit` | Earlier grant and a receipt | Policy audit events | Complete authentic revocation audit; missing revocation reintroduces ambiguity |
| At-most-once effects | Whether the intent committed at most one effect | Receipt for first effect | Ledger effect IDs | Ledger covers **every** committed effect; unlogged second effect reintroduces ambiguity |
| Head monotonicity (not full non-rollback) | Whether local head regresses below an earlier, actually attained local head | Local head and local witness | External witnessed head | Witness anchors the highest previously attained head of **this log**, and is fresh and unrollbackable; stale or equivocated witness reintroduces ambiguity |

Each of these three example universes contains two histories satisfying its trust condition (one safe, one unsafe) and a third with incomplete/stale evidence. The companion **exhaustive** model enumerates the full declared bounded world grammar and adds a fourth property: history-prefix continuity at constant head height; see [MODEL_CHECK.md](MODEL_CHECK.md). `classify` quantifies over histories compatible with the observer and chosen threat boundary, including a distinct `INCONSISTENT_EVIDENCE` case when none match.

The strengthened model is still bounded and deliberately stylized: it does not generate unbounded traces, represent concurrency or crashes, prove non-bypassable enforcement, distinguish authenticated from malicious ledger signatures, model external witness equivocation, or implement a protocol. Thus sufficiency remains **conditional on evidence completeness**, which a real system must establish independently. Tests are executable checks of these finite definitions, not validation of the assumptions themselves.

Run: `python -m unittest discover -s . -p 'test_*.py' -v`. The trace file adds six test methods to the previous ten. The separate exhaustive extension adds ten more, for 26 total in this research branch; counting methods does not substitute for scientific review.
