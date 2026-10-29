"""Two-worker bounded interleaving checker for one intent/key.

The workers send the same stable intent key to one abstract endpoint. No
network code, cryptography, durability proof, or production implementation.
"""
from collections import deque
from dataclasses import dataclass

MODES = ('check_then_effect_then_mark', 'reserve_then_effect', 'atomic_effect_and_key')
PHASES = ('ready', 'checked', 'claimed', 'effect_done', 'done', 'crashed')


@dataclass(frozen=True)
class State:
    phases: tuple = ('ready', 'ready')
    marker: bool = False
    effects: int = 0


def transitions(state, mode):
    if mode not in MODES:
        raise ValueError('Unsupported mode')
    if not state.phases or any(p not in PHASES for p in state.phases):
        raise ValueError('Invalid worker phases')
    if not isinstance(state.marker, bool) or state.effects < 0:
        raise ValueError('Invalid durable state')
    result = []
    for idx, phase in enumerate(state.phases):
        def move(action, new_phase, marker=None, effects=0):
            ps = list(state.phases)
            ps[idx] = new_phase
            next_state = State(tuple(ps), state.marker if marker is None else marker,
                               state.effects + effects)
            result.append((f'w{idx}:{action}', next_state))
        if phase == 'ready':
            if state.marker:
                move('observe-dedup-key', 'done')
            elif mode == 'check_then_effect_then_mark':
                move('check-key-absent', 'checked')
            elif mode == 'reserve_then_effect':
                move('reserve-key', 'claimed', marker=True)
            else:
                move('atomic-effect-and-record-key', 'done', marker=True, effects=1)
        elif phase == 'checked' and mode == 'check_then_effect_then_mark':
            move('commit-effect', 'effect_done', effects=1)
        elif phase == 'effect_done' and mode == 'check_then_effect_then_mark':
            move('write-key', 'done', marker=True)
        elif phase == 'claimed' and mode == 'reserve_then_effect':
            move('commit-effect', 'done', effects=1)
            move('crash-before-effect', 'crashed')
    return tuple(result)


def explore(mode, worker_count=2):
    if not isinstance(worker_count, int) or not 1 <= worker_count <= 8:
        raise ValueError('Worker count must be an integer in [1, 8]')
    initial = State(('ready',) * worker_count)
    queue = deque((initial,))
    paths = {initial: ()}
    while queue:
        state = queue.popleft()
        for action, next_state in transitions(state, mode):
            if next_state not in paths:
                paths[next_state] = paths[state] + (action,)
                queue.append(next_state)
    return paths


def shortest_witness(mode, claim, worker_count=2):
    if claim not in ('at_most_once', 'terminal_effect_exists', 'no_false_dedup'):
        raise ValueError('Unknown claim')
    for state, path in explore(mode, worker_count=worker_count).items():
        if claim == 'at_most_once':
            violates = state.effects > 1
        elif claim == 'terminal_effect_exists':
            violates = (not transitions(state, mode) and state.effects == 0)
        else:
            # A worker treats a pre-effect reservation as a completed effect.
            violates = ('done' in state.phases and state.effects == 0)
        if violates:
            return state, path
    return None


def report():
    return tuple({
        'mode': mode,
        'reachable_states': len(explore(mode)),
        'duplicate_effect_witness': shortest_witness(mode, 'at_most_once'),
        'terminal_missing_effect_witness': shortest_witness(mode, 'terminal_effect_exists'),
        'dedup_before_effect_witness': shortest_witness(mode, 'no_false_dedup'),
    } for mode in MODES)


if __name__ == '__main__':
    for line in report():
        print(line)
