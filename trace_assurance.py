"""Bounded trace-derived assurance examples; no production or cryptographic code.

Safety is computed from events rather than assigned to histories. Trusted
observation completeness is an explicit restriction on the admissible worlds.
"""
from dataclasses import dataclass
from typing import Tuple, Union

ESTABLISHED = 'ESTABLISHED_WITHIN_MODEL'
REFUTED = 'REFUTED_WITHIN_MODEL'
UNKNOWN = 'NOT_ESTABLISHED'
INCONSISTENT = 'INCONSISTENT_EVIDENCE'


@dataclass(frozen=True)
class AuthorizationTrace:
    events: Tuple[str, ...]
    policy_audit: Tuple[str, ...]

    def __post_init__(self):
        if self.events not in (('grant', 'commit'), ('grant', 'revoke', 'commit')):
            raise ValueError('The bounded example requires a grant and one commit')
        if self.policy_audit not in (('grant',), ('grant', 'revoke')):
            raise ValueError('Unexpected policy audit sequence')

    def safe(self):
        return 'revoke' not in self.events[:self.events.index('commit')]

    def trusted(self):
        return self.policy_audit == tuple(e for e in self.events if e in ('grant', 'revoke'))

    def observe(self, enriched=False):
        base = ('grant:U:A:R', 'receipt:A:R')
        return base + (('policy-audit:' + ','.join(self.policy_audit),) if enriched else ())


@dataclass(frozen=True)
class EffectTrace:
    commits: Tuple[str, ...]
    ledger: Tuple[str, ...]

    def __post_init__(self):
        if self.commits not in (('e1',), ('e1', 'e2')):
            raise ValueError('The bounded example permits one or two effects')
        if self.ledger not in (('e1',), ('e1', 'e2')):
            raise ValueError('Unexpected ledger contents')

    def safe(self):
        return len(self.commits) <= 1

    def trusted(self):
        return self.ledger == self.commits

    def observe(self, enriched=False):
        base = ('receipt:intent-I:e1',)
        return base + (('ledger:' + ','.join(self.ledger),) if enriched else ())


@dataclass(frozen=True)
class RollbackTrace:
    committed_heads: Tuple[int, ...]
    local_head: int
    witness_head: int

    def __post_init__(self):
        if self.committed_heads not in ((1,), (1, 2)) or self.local_head != 1:
            raise ValueError('The bounded example compares checkpoint 1 with 2')
        if self.witness_head not in (1, 2):
            raise ValueError('Unexpected witness head')

    def safe(self):
        return self.local_head == max(self.committed_heads)

    def trusted(self):
        return self.witness_head == max(self.committed_heads)

    def observe(self, enriched=False):
        base = ('log-head:1', 'local-witness:1')
        return base + (('fresh-external-head:' + str(self.witness_head),) if enriched else ())


Trace = Union[AuthorizationTrace, EffectTrace, RollbackTrace]


def classify(worlds: Tuple[Trace, ...], observation: Tuple[str, ...], *,
             enriched=False, require_trust=True):
    """Quantify over worlds consistent with the chosen observational boundary."""
    candidates = [w for w in worlds if (not require_trust or w.trusted())
                  and w.observe(enriched) == observation]
    if not candidates:
        return INCONSISTENT
    values = {w.safe() for w in candidates}
    if values == {True}:
        return ESTABLISHED
    if values == {False}:
        return REFUTED
    return UNKNOWN


def universes():
    """Generate trace universes, including one dropped/stale evidence case each."""
    return {
        'authorization': (
            AuthorizationTrace(('grant', 'commit'), ('grant',)),
            AuthorizationTrace(('grant', 'revoke', 'commit'), ('grant', 'revoke')),
            AuthorizationTrace(('grant', 'revoke', 'commit'), ('grant',)),
        ),
        'at_most_once': (
            EffectTrace(('e1',), ('e1',)),
            EffectTrace(('e1', 'e2'), ('e1', 'e2')),
            EffectTrace(('e1', 'e2'), ('e1',)),
        ),
        'non_rollback': (
            RollbackTrace((1,), 1, 1),
            RollbackTrace((1, 2), 1, 2),
            RollbackTrace((1, 2), 1, 1),
        ),
    }
