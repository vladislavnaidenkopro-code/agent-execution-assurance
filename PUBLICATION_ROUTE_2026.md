## Author's revised publication decision — 29 October 2026

**Current paper:** prioritize a scientifically careful, reproducible **non-peer-reviewed technical report** and separate code archive. Finish internal claims/mathematical/bibliographic and reproducibility checks, obtain the named author's manuscript approval, freeze the exact code SHA, then prepare a distinct Zenodo paper record/DOI. Explore TechRxiv and arXiv only if appropriate, and present actual released work on GitHub / LinkedIn after publication. Do not present repository badges or preprint screening as independent academic peer review.

**Journal track:** DEFERRED. No JOT formatting, editor correspondence, journal submission or external reviewer outreach now. At a later date, identify **a different, genuinely journal-suitable research question**, independently justify its novelty and target venue; do not force the present bounded counterexample study into a journal. That future venue will need its own eligibility and preprint-compatibility check. Journal review remains optional for the current work.

**Publication gate:** no manuscript deposit or announcements before in-house scientific correction, frozen version reproducibility, appropriate AI-assistance disclosure and human-author sign-off. Existing v1.1.1 DOI is a previous code archive, not an identifier for the unreleased research branch.

This decision supersedes the earlier conditional JOT-first sequence in the historical planning sections below. No messages or submissions have been sent.

---

# Publication strategy and venue compatibility — 29 October 2026

**Status:** research planning document, NOT a journal submission, preprint or published paper. **No outreach or submission has been sent.**  
**Author:** Vladislav Naidenko  
**Repository policy:** only public synthetic research; no VLADS Future proprietary code, manifests, credentials or internal architecture.

## Decision

Publish a narrowly claimed, reproducible technical research report when its **internal scientific and human-author review gates** pass. Seek **optional journal peer review** in a credible no-fee venue. Do not force an external private review as a prerequisite for public preprint release.

**Critical sequencing exception:** while JOT is a target, **do not post the manuscript to Zenodo/TechRxiv/arXiv before clarifying its preprint policy directly with the journal**. The publicly available JOT instructions prohibit previously published manuscripts but do not explicitly define the status of a not-yet-journal-reviewed Zenodo or TechRxiv preprint. JOT's self-archiving policy allows repository deposits of submitted/accepted/published versions; that alone is not a sufficient answer about a pre-submission posting. Obtain written clarification or consciously deprioritize JOT before first manuscript deposit.

## Venue verification

| Venue | Cost and role | Confirmed preparation requirement | Current decision |
| --- | --- | --- | --- |
| Zenodo | Free archival platform; a published record obtains DOI; use **separate software and paper records**, with related identifiers | Review exact tag/commit, creator, license, software version, release files, and manuscript metadata. DOI is specific to record/version. | **Ready after claims approval and JOT preprint clarification**, not now |
| IEEE TechRxiv | Free moderated **non-peer-reviewed** preprint service; screening is not scholarly acceptance | Complete English manuscript; scope and preprint policy screening; submission before final journal publication | **Secondary preprint dissemination** after checking journal compatibility; do not mirror blindly |
| arXiv | Free moderated scientific preprint repository | Scholarly scope and registration; first-time/new-category submitters may require endorsement | **Conditional option**. Endorsement and moderation are not a review result; avoid mass duplicate uploads |
| Journal of Object Technology (JOT) | **Diamond OA**: no APC for author, free to read; peer-reviewed software/language engineering journal | **Mandatory JOT LaTeX template; PDF-only submission.** Research must be original, technically sound and software-engineering focused. Typical article ~25–30 pages, not a page-length requirement. Journal submission cannot simultaneously be before another **journal**. | **Stretch goal**. Verify preprint policy in writing before posting our paper; current evidence/novelty may not meet originality threshold |
| JOT Software Section | Same journal, different article type | Mature usable model-based engineering tool with published supporting research/community, runnable binary, examples, issue tracker | **NOT suitable** for our current synthetic research fixtures |
| Journal of Open Source Software (JOSS) | No-charge open journal for genuine research software | More than six months public development with sustained iterations, demonstrable research use, appropriate packaging; full AI-use disclosure | **Not eligible at present**. Reassess only after real open-source adoption, not through cosmetic commit activity |
| GitHub | Open research code and release metadata | No private code; public repository is for synthetic fixtures and exact tagged source | **Already in use**. Keep branch Draft until human claims review |
| LinkedIn / portfolio | Professional presentation, NOT scientific publication | Link only to real releases/DOIs with unambiguous status (preprint vs peer review); no misrepresented claims | **After publication**, editorial approval before posts |

## JOT preprint policy: precise open question

JOT's official submission page says a submission **has not been previously published**, uses the JOT LaTeX template, accepts **PDF only**, and permits original research, mature best-practice reports and surveys. Its separate open-access page says authors may deposit *submitted, accepted and published* versions in repositories without embargo. These statements do not directly answer whether a first public manuscript deposit on Zenodo or TechRxiv **before journal submission** counts as prior publication for JOT. IEEE's more permissive preprint policy is not automatically JOT's policy.

**Editorial clarification to request before manuscript upload** (prepare only; do not send automatically):

1. Does JOT consider a publicly DOI-registered Zenodo manuscript, or TechRxiv/arXiv preprint, to be a prohibited *previous publication*?
2. If accepted, may the same work be deposited before submission, provided the journal submission discloses all exact preprint URLs/DOIs and versions?
3. Is a reproducible **bounded countermodel / technical experience report** of known distributed-systems failure modes within JOT's software validation & verification scope, even if it does not claim a novel algorithm or theorem?
4. How should substantial AI-assisted code/model/latex editing be declared under JOT's current author instructions?

Do not treat a non-response as permission. In the absence of clarification, prioritize the **technical preprint path**, knowing this may limit a later JOT submission, or postpone the preprint if JOT remains higher priority.

## Strict manuscript release gates

- **S1 — Claim-to-model agreement.** Every positive result is labeled *within the finite model under assumptions*. Separate event count, honest acknowledgements, liveness and log-prefix continuity.
- **S2 — Prior art.** Confirm bibliographic metadata and the novelty threshold. Distinguish a reproducible **integration of pre-existing counterexamples** from a new theorem or formal method. Explicitly cite Herlihy & Wing 1990, Lamport 2002, RFCs 9162 / 9942 / 9943, the IETF Idempotency-Key **draft**, AWS transactional outbox, and Case's Structural Assurability.
- **S3 — Reproducibility.** Clean-clone full code SHA, CI on 3.10/3.12/3.13, canonical model output + digest, generated figures built from that frozen output, proper code/paper license split. Numerical state counts are *abstract cardinalities, not risk probabilities or benchmark results*.
- **S4 — Human author acceptance.** Named author reads and validates manuscript, signs off claims, sources, and AI assistance statement. Do not falsely claim human review before it occurs.
- **S5 — Venue compatibility.** Resolve JOT preprint ambiguity before publishing the manuscript if the journal path is pursued.
- **S6 — Releasing.** Only after S1–S5: review SHA; create new software release/archival version; use **correct new software version DOI**; then prepare final manuscript and separate paper record/DOI, link both records. Never reuse the old DOI as if it identified Draft PR #1.

External expert commentary may improve quality, but **independent pre-submission review is optional**. The separate journal's reviewer process, if submitted, is distinct from preprint screening.

## Public-policy primary sources checked on 29 October 2026

- JOT home/diamond OA: https://www.jot.fm/
- JOT submissions (mandatory template, scope, originality, PDF, prior-publication language): https://submissions.jot.fm/index.php/jot/about/submissions
- JOT OA / self-archiving: https://www.jot.fm/oa.php
- JOT Software Section eligibility: https://www.jot.fm/software
- IEEE TechRxiv preprint status: https://innovate.ieee.org/techrxiv/
- arXiv endorsement: https://github.com/arXiv/arxiv-docs/blob/develop/source/help/endorsement.md
- Zenodo deposit and DOI versioning: https://help.zenodo.org/docs/deposit/ and https://zenodo.org/help/versioning
- JOSS submission criteria, current: https://joss.readthedocs.io/en/latest/submitting.html

This is a planning record about current policies. Recheck author guidelines immediately before every upload or submission.
