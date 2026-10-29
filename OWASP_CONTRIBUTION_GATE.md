# OWASP Agentic Evidence — possible narrow research contribution (NOT SUBMITTED)

**Date:** 2026-10-29  
**Decision:** OWASP work **retained as an optional downstream contribution**, not cancelled. Competitions, creating a competing OWASP standard/project, and unapproved outreach remain excluded. The primary deliverable is still the VLADS Reputation research paper/preprint with an exact reproducible software version, not an OWASP deliverable.

## Project fit, established from official sources

- **OWASP Agentic Evidence**, https://github.com/OWASP/Agentic-Evidence, is an incubating project focused on execution reconstruction, evidence sufficiency, provenance, evidence gaps, and synthetic deterministic scenarios. As checked on 29 October 2026, its README calls out **benign execution, retrieval poisoning and tool descriptor modification** as its first three planned scenarios. Its intended JSON schema/MVP may change, and it advises prospective contributors to coordinate through an issue before substantial implementation.
- **OWASP Agent Control Standard (ACS)**, https://genai.owasp.org/resource/agent-control-standard-acs/, describes **runtime middleware hooks and enforcement**. It is complementary and is **not** where our observation-equivalence samples belong.
- **OWASP AISVS**, https://owasp.github.io/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/, is a catalogue of verifiable controls. Our fixtures might eventually reference control categories, but they must not pretend to certify AISVS compliance.

**Non-overlap rule:** contribute specific reproducible **negative evidence-sufficiency test cases**, not a new standard, agent runtime, SIEM, detector, cryptographic guarantee, or duplicate of the OWASP project's planned implementation.

## Prepared local artifact

- `owasp_candidate_vectors.py`: generate **seven** public, synthetic, deterministic research vectors using the *existing* bounded models; JSON is a **VLADS candidate format**, NOT an OWASP versioned schema.
- `test_owasp_candidate_vectors.py`: checks exact observational collisions, derived NOT_ESTABLISHED verdicts, distinct enriched observations, valid shortest-path event witnesses, downstream and concurrent effects, honest limitations and determinism.
- Test command: `python -m unittest discover -s . -p 'test_*.py' -v`; inspection command: `python owasp_candidate_vectors.py`. Verify the actual CI result and exact PR SHA before any external disclosure.

Candidate cases:
1. `AE-CAND-AUTH-001`: same grant/receipt, opposite authorization at commit.
2. `AE-CAND-EFFECT-001`: one receipt, one or multiple actual external commits.
3. `AE-CAND-LOG-001`: same log height with incompatible content prefixes.
4. `AE-CAND-RETRY-001`: client loses reply after effect; remote API without dedup duplicates.
5. `AE-CAND-RACE-001`: two workers pass non-atomic key check and commit twice.
6. `AE-CAND-FANOUT-001`: primary atomic commit, but duplicate downstream side effect.
7. `AE-CAND-FORGERY-001`: forged success response allows a false local completion.

The **first three** map most directly to evidence-sufficiency gaps. The remaining four are supplementary state-machine countermodels that might be outside the maintainers' first-phase scope. Start with a very small subset only if maintainers agree.

## Proposed issue for maintainer feedback — DRAFT, DO NOT POST

**Title:** Proposal: minimal synthetic negative evidence-sufficiency cases for Agentic Evidence MVP

**Body:**

> The project's evidence-gap and deterministic-scenario objectives appear compatible with a small set of synthetic *negative* examples: (1) an apparently valid execution receipt that cannot establish commit-time authorization when a revocation may be missing, (2) a single receipt consistent with one or two committed effects, and (3) equal log heights consistent with a same-height prefix fork.
>
> We have a public research branch with bounded, reproducible Python countermodels and an internal candidate JSON generator. It **does not** claim to implement your evidence schema, cryptographic witnesses, agent runtime or security verifier; positive conclusions remain conditional on stated trusted-evidence assumptions.
>
> Before preparing a focused PR, would maintainers consider negative evidence-sufficiency cases in scope for an initial or later scenario phase? If yes, which existing schema/version and fixture contract should we target, and would one minimal case be a useful first contribution?
>
> No real customer traces, private implementation material or external services are required. We would adapt to the project's documented fixture format rather than proposing a competing standard.

## Gates: do not skip

- **No issue/PR/comment/outreach yet**: require explicit external-contact authorization after the owner reviews the concise proposal and verifies the target project's current roadmap/issues.
- **No publication of private product code** or internal systems; candidate data is synthetic only.
- **No statement of OWASP partnership, project acceptance, endorsement or standard compliance** before the project actually accepts a contribution.
- **No research-release coupling**: OWASP feedback must not block internal scientific validation, manuscript approval, Zenodo publication, or consideration of TechRxiv/arXiv.
- **Check licenses/scope** before upstream transfer: the local MIT source and article CC BY 4.0 notices are not automatically the same as the recipient project's authoritative license requirements.
- **Never confuse evidence with enforcement**: an event/receipt observation cannot prove the intended live runtime property without independently justified trust assumptions and complete effects.

**Success condition:** at most one focused maintainer-approved negative vector is accepted upstream with reproducible tests and correct attribution. Until then the status is **CANDIDATE / NO OWASP CONTRIBUTION MADE**.
