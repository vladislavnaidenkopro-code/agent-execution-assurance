"""Finite-world assurance demonstrations, not deployed security mechanisms."""
from dataclasses import dataclass
from typing import Tuple

ESTABLISHED = 'ESTABLISHED_WITHIN_MODEL'
REFUTED = 'REFUTED_WITHIN_MODEL'
UNKNOWN = 'NOT_ESTABLISHED'
INCONSISTENT = 'INCONSISTENT_EVIDENCE'

@dataclass(frozen=True)
class History:
    name: str
    baseline: Tuple[str, ...]
    enriched: Tuple[str, ...]
    safe: bool

def classify(histories, observation, view='baseline'):
    compatible = [h for h in histories if getattr(h, view) == observation]
    if not compatible:
        return INCONSISTENT
    values = {h.safe for h in compatible}
    return ESTABLISHED if values == {True} else REFUTED if values == {False} else UNKNOWN

def scenarios():
    # Enriched evidence represents an assumed trusted mechanism, not a signature implementation.
    return {
        'authorization': (
            History('valid_at_commit', ('grant', 'receipt'), ('enforced:policy-v2:allow',), True),
            History('revoked_before_commit', ('grant', 'receipt'), ('enforced:policy-v2:deny',), False),
            History('different_safe_trace', ('grant', 'receipt'), ('enforced:policy-v2:allow',), True),
        ),
        'at_most_once': (
            History('single_commit', ('receipt:e1',), ('atomic-ledger:intent-I:one-effect',), True),
            History('duplicate_commit', ('receipt:e1',), ('atomic-ledger:intent-I:two-effects',), False),
            History('another_single_commit', ('receipt:e1',), ('atomic-ledger:intent-I:one-effect',), True),
        ),
        'non_rollback': (
            History('never_advanced', ('local-head:c',), ('external-anchor:latest=c',), True),
            History('rolled_back', ('local-head:c',), ('external-anchor:latest=d',), False),
            History('another_never_advanced', ('local-head:c',), ('external-anchor:latest=c',), True),
        ),
    }

def residual_failures():
    # Worlds become observationally equivalent again if the extra trust assumption is withdrawn.
    return {
        'authorization': (
            History('trusted_enforcer', (), ('enforced:allow',), True),
            History('compromised_enforcer', (), ('enforced:allow',), False),
        ),
        'at_most_once': (
            History('durable_ledger', (), ('ledger:one',), True),
            History('ledger_rollback', (), ('ledger:one',), False),
        ),
        'non_rollback': (
            History('fresh_witness', (), ('anchor:c',), True),
            History('stale_or_equivocating_witness', (), ('anchor:c',), False),
        ),
    }
