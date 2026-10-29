"""Bounded synthetic primary+downstream effect boundary; no network or product code.

One intent legitimately induces a primary transaction and one downstream effect.
The primary transaction is assumed atomic with its local intent marker;
downstream delivery is a separate transaction with its own dedup boundary.
"""
from collections import deque
from dataclasses import dataclass, replace

MODES = ('no_downstream_dedup', 'downstream_atomic_key',
         'downstream_expiring_key', 'downstream_nonatomic_key')
PHASES = ('initial', 'queued', 'inflight', 'unmarked', 'committed',
          'deduplicated', 'finished')

@dataclass(frozen=True)
class State:
    phase: str = 'initial'
    primary_effects: int = 0
    primary_marker: bool = False
    downstream_effects: int = 0
    downstream_marker: bool = False
    deliveries: int = 0
    server_crashes: int = 0
    key_expirations: int = 0
    ack_received: bool = False

def transitions(state, mode, *, max_deliveries=2, max_server_crashes=1,
                max_key_expirations=1):
    if mode not in MODES or state.phase not in PHASES:
        raise ValueError('Invalid mode/phase')
    if min(max_deliveries, max_server_crashes, max_key_expirations) < 0:
        raise ValueError('Invalid bounds')
    if state.primary_effects < 0 or state.downstream_effects < 0:
        raise ValueError('Invalid effect count')
    if state.phase == 'finished':
        return ()
    result = []
    def add(label, **changes):
        result.append((label, replace(state, **changes)))
    p = state.phase
    if p == 'initial':
        add('atomic-primary-effect-and-intent-marker', phase='queued',
            primary_effects=1, primary_marker=True)
    if p == 'queued' and state.deliveries < max_deliveries:
        add('deliver-outbox-event', phase='inflight', deliveries=state.deliveries+1)
    if p == 'inflight':
        if mode != 'no_downstream_dedup' and state.downstream_marker:
            add('downstream-deduplicates', phase='deduplicated')
        elif mode == 'downstream_nonatomic_key':
            add('commit-downstream-before-recording-key', phase='unmarked',
                downstream_effects=state.downstream_effects+1)
        else:
            add('commit-downstream-effect', phase='committed',
                downstream_effects=state.downstream_effects+1,
                downstream_marker=mode != 'no_downstream_dedup')
    if p == 'unmarked':
        add('persist-downstream-key', phase='committed', downstream_marker=True)
        if state.server_crashes < max_server_crashes:
            add('remote-crash-before-key', phase='queued',
                server_crashes=state.server_crashes+1)
    if p in ('committed', 'deduplicated'):
        add('acknowledge-downstream-delivery', phase='finished', ack_received=True)
        add('lose-downstream-acknowledgement', phase='queued')
    if (mode == 'downstream_expiring_key' and state.downstream_marker
            and state.key_expirations < max_key_expirations):
        add('expire-downstream-key', downstream_marker=False,
            key_expirations=state.key_expirations+1)
    return tuple(result)

def explore(mode, **bounds):
    start = State()
    paths = {start: ()}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        for action, dest in transitions(state, mode, **bounds):
            if dest not in paths:
                paths[dest] = paths[state] + (action,)
                queue.append(dest)
    return paths

def witness(mode, property_name, **bounds):
    if property_name not in ('primary_at_most_once', 'downstream_at_most_once',
                             'both_effects_if_acknowledged', 'downstream_guaranteed'):
        raise ValueError('Unknown property')
    for state, actions in explore(mode, **bounds).items():
        if property_name == 'primary_at_most_once':
            bad = state.primary_effects > 1
        elif property_name == 'downstream_at_most_once':
            bad = state.downstream_effects > 1
        elif property_name == 'both_effects_if_acknowledged':
            bad = state.ack_received and (state.primary_effects != 1 or
                                           state.downstream_effects < 1)
        else:
            bad = (state.primary_effects == 1 and state.downstream_effects == 0
                   and not transitions(state, mode, **bounds))
        if bad:
            return state, actions
    return None

def report():
    return tuple((mode, len(explore(mode)),
                  witness(mode, 'primary_at_most_once') is None,
                  witness(mode, 'downstream_at_most_once') is None,
                  witness(mode, 'both_effects_if_acknowledged') is None)
                 for mode in MODES)

if __name__ == '__main__':
    for row in report(): print(row)
