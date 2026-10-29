# TextGrain technical assessment and publication-provenance gate

**Status:** internal publication-process assessment, 29 October 2026. **NOT** a method or certification of watermark removal. This document is not part of the scientific contributions of the agent-execution assurance models and should not be inserted into their Related Work section.

## Primary source

Xiang Li, Garrett Wen, Xiaohong Chen, Qi Long, Arzav Jain, Florent Joly, Mike Lam, Qingquan Song and Weijie Su, *textGrain: Entropy-Calibrated Watermarking for Language Model Text*, technical report, 5 October 2026.

Primary source: https://cdn.openai.com/pdf/e9508624-d767-41b6-a26d-e34ca798ada6/textgrain-entropy-calibrated-watermarking-for-language-model-text.pdf

The report describes a **key-dependent statistical watermark introduced during token sampling**. It couples the next-token distribution with keyed randomness through blockwise optimal transport and a KL-regularized entropy-loss budget. Detection reconstructs keyed per-token scores from text, the secret key and the corresponding tokenizer/context parameters; the detector does not need the model's original token probabilities or the generation-time entropy budget. Section 3.2 derives a conditional null distribution of the summed scores under explicit assumptions about independence across scored contexts. A fixed deployed key and finite-precision implementation require empirical calibration; the theoretical null does not guarantee the nominal error rate in every deployment.

## Evidence boundaries

1. The public report **does not identify whether any particular response, model configuration, manuscript or chat in this project was marked**. Nothing in this project confirms the watermark is present or absent.
2. A purported textGrain negative test without access to the relevant secret key, tokenizer, context construction and calibrated detector would be **unverifiable**. Neither an AI-text classifier nor stylistic judgment is an equivalent test.
3. The report is not proof of universal identifiability. Its claims depend on stated mathematical assumptions; detection of a signal, when properly established, is a statistical claim, not a scientific authorship determination.
4. A user request to **guarantee a “bypass”** cannot be treated as a validated publication gate. We cannot promise that formatting a PDF, rewriting an abstract or any unknown transformation will make a document undetectable. We will not falsely certify removal of provenance information.
5. A successful detector-evasion claim would not validate the scientific statements, nor would watermark detection imply that experiments or citations are invalid. **Scientific reproducibility and legitimate author responsibility are separate matters.**

## Publication-quality controls instead of evasion claims

- Final prose is **substantively authored and approved by the named human author**, who reviews every theorem-level claim, methods table, limitation, figure and reference; until that review happens, the manuscript remains Draft.
- Maintain a reproducible code archive at an exact Git SHA, scripts to regenerate figures and a checked claims-to-test map. Avoid inserting automatically generated results not reverified against that SHA.
- Keep a documented AI-assistance log, if used, and disclose AI-tool use **according to the actual target venue's policy**, without inventing a human-only drafting history. This note makes no claim about which particular published words carry a watermark.
- Do not pass automated paraphrasing, translation, style randomization or unverified “humanizer” scores off as proof of human authorship or absence of textGrain. They can compromise technical accuracy and still do not provide a valid detector result.
- An external reviewer should assess the paper's **original contribution, reasoning and reproducibility**, not infer scientific validity from an AI-text detector score.

## Release decision

**HOLD** for final article/DOI submission until independent scientific review, claim-to-experiment reconciliation, manuscript revision and frozen code provenance. The watermark-source investigation is complete at the public-report level; **certified absence or bypass of textGrain remains UNKNOWN**, and must not be asserted.

Proposed AI-assistance disclosure for eventual human review, to be adapted to venue policy and verified before publication:

> AI-based tools assisted with research organization, software fixtures, draft editing, and test/document preparation. The named human author independently reviewed and approved the scientific claims, citations, code, figures, and final manuscript and accepts full responsibility for the content.

The final sentence above is a **template**, not yet an attestation: it must be included only after the named author actually completes the stated checks.
