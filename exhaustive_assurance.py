"""Exhaustive finite-world checks for synthetic evidence claims.

All combinations in a stated small grammar are enumerated. This is neither a
proof over unbounded histories nor evidence of real-system trust. trusted()
is an assumption of authentic complete evidence, NOT a verified mechanism.
"""
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations, product
from typing import Tuple

from trace_assurance import AuthorizationTrace, EffectTrace, RollbackTrace, classify


@dataclass(frozen=True)
class PrefixContinuityTrace:
    """Equal log height need not imply identical append-only history.

    Witness binds the previously attained prefix; current prefix is visible.
    Exact token identity is idealized. No cryptographic protocol is modeled.
    """
    previous_prefix: Tuple[str, ...]
    current_prefix: Tuple[str, ...]
    witnessed_prefix: Tuple[str, ...]

    ALLOWED = (('genesis', 'a'), ('genesis', 'b'))

    def __post_init__(self):
        if any(x not in self.ALLOWED for x in (
                self.previous_prefix, self.current_prefix, self.witnessed_prefix)):
            raise ValueError('Only the two fixed 2-entry prefixes are allowed')

    def safe(self):
        return self.current_prefix[:len(self.previous_prefix)] == self.previous_prefix

    def trusted(self):
        # ASSUMED: authentic fresh witness for this log's prior actual prefix.
        return self.witnessed_prefix == self.previous_prefix

    def observe(self, enriched=False):
        base = ('local-height:2', 'witness-height:2')
        if not enriched:
            return base
        return base + (
            'local-prefix:' + '/'.join(self.current_prefix),
            'witness-prefix:' + '/'.join(self.witnessed_prefix),
        )


def exhaustive_universes():
    """Every finite product of the explicitly bounded trace/evidence choices.

    Sizes: authorization 2x2=4; effects 2x2=4; head 2x2=4;
    prefix continuity 2x2x2=8. Total 20 synthetic possible worlds.
    """
    auth_events = (('grant', 'commit'), ('grant', 'revoke', 'commit'))
    audits = (('grant',), ('grant', 'revoke'))
    commits = (('e1',), ('e1', 'e2'))
    prefixes = PrefixContinuityTrace.ALLOWED
    return {
        'authorization': tuple(AuthorizationTrace(e, a)
                               for e, a in product(auth_events, audits)),
        'at_most_once': tuple(EffectTrace(actual, ledger)
                              for actual, ledger in product(commits, commits)),
        'head_monotonicity': tuple(
            RollbackTrace(actual, prior, 1, witness)
            for actual, prior in (((1,), 1), ((1, 2), 2))
            for witness in (1, 2)),
        'prefix_continuity': tuple(
            PrefixContinuityTrace(previous, current, witness)
            for previous, current, witness in product(prefixes, prefixes, prefixes)),
    }


def observation_classes(worlds, *, enriched=False, require_trust=True):
    """Partition admissible histories by what the verifier can observe."""
    classes = defaultdict(list)
    for w in worlds:
        if not require_trust or w.trusted():
            classes[w.observe(enriched)].append(w)
    return dict(classes)


def ambiguous_witness(worlds, *, enriched=False, require_trust=True):
    """Compute a safe/unsafe pair with equal observations; never handpick one."""
    for group in observation_classes(
            worlds, enriched=enriched, require_trust=require_trust).values():
        for a, b in combinations(group, 2):
            if a.safe() != b.safe():
                return a, b
    return None


def model_check():
    """Return deterministic rows for each claim and evidence/trust scope."""
    rows = []
    for claim, worlds in exhaustive_universes().items():
        for scope, enriched, require_trust in (
                ('baseline+trusted', False, True),
                ('enriched+trusted', True, True),
                ('enriched+no-trust', True, False)):
            classes = observation_classes(
                worlds, enriched=enriched, require_trust=require_trust)
            verdicts = tuple(classify(worlds, obs, enriched=enriched,
                                      require_trust=require_trust) for obs in classes)
            rows.append((claim, scope, len(worlds),
                         sum(map(len, classes.values())), len(classes), verdicts))
    return rows
