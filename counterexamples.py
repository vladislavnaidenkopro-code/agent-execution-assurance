"""Standalone synthetic epistemic counterexamples. No VLADS product code."""
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class World:
    observation: Tuple[str, ...]
    property_holds: bool
    explanation: str

def verdict(worlds):
    if not worlds:
        raise ValueError('At least one compatible world required')
    if len({w.observation for w in worlds}) != 1:
        raise ValueError('Worlds must be observationally indistinguishable')
    values = {w.property_holds for w in worlds}
    return ('ESTABLISHED_WITHIN_MODEL' if values == {True} else
            'REFUTED_WITHIN_MODEL' if values == {False} else 'NOT_ESTABLISHED')

def cases():
    return {
        'authorization': (
            World(('grant:U:A:R', 'receipt:A:R'), True, 'No revocation before execution'),
            World(('grant:U:A:R', 'receipt:A:R'), False, 'Unobserved revocation before execution')),
        'at_most_once': (
            World(('receipt:intent-I:effect-e1',), True, 'One committed effect'),
            World(('receipt:intent-I:effect-e1',), False, 'Second committed effect, receipt lost')),
        'non_rollback': (
            World(('log-head:c', 'local-witness:c'), True, 'No subsequent history'),
            World(('log-head:c', 'local-witness:c'), False, 'Later history rolled back with witness')),
    }
