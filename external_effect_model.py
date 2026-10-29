"""Finite-state model: durable local outbox vs independent external side effect.

Public synthetic research fixture. No network, cryptography or product code.
The model deliberately distinguishes client-side persistence from remote effect
commit, response delivery, and the remote endpoint's deduplication boundary.
"""
from collections import deque
from dataclasses import dataclass, replace

MODES = ('outbox_only', 'endpoint_atomic_key', 'endpoint_expiring_key',
         'endpoint_nonatomic_key')
PHASES = ('idle', 'request_ready', 'request_dropped', 'remote_unmarked',
          'remote_committed', 'remote_deduped', 'response_received', 'finished')


@dataclass(frozen=True)
class State:
    remote_effects: int = 0
    remote_key_recorded: bool = False
    local_done: bool = False
    phase: str = 'idle'
    attempts: int = 0
    client_crashes: int = 0
    server_crashes: int = 0
    key_expirations: int = 0


def transitions(state, mode, *, max_attempts=2, max_client_crashes=1,
                max_server_crashes=1, max_key_expirations=1):
    """Enumerate all enabled abstract events from one reachable state."""
    if mode not in MODES:
        raise ValueError('Unknown mode')
    if state.phase not in PHASES or state.attempts < 0 or state.remote_effects < 0:
        raise ValueError('Invalid state')
    if min(max_attempts, max_client_crashes, max_server_crashes, max_key_expirations) < 0:
        raise ValueError('Bounds must be nonnegative')
    if state.local_done and state.phase != 'finished':
        raise ValueError('A completed local intent cannot remain in-flight')
    if state.phase == 'finished':
        return ()

    steps = []
    if state.phase == 'idle' and state.attempts < max_attempts:
        steps.append(('begin-request', replace(state, phase='request_ready',
                                                attempts=state.attempts + 1)))

    if state.phase == 'request_ready':
        steps.append(('network-drops-request', replace(state, phase='request_dropped')))
        if mode != 'outbox_only' and state.remote_key_recorded:
            steps.append(('remote-dedup-suppresses-effect',
                          replace(state, phase='remote_deduped')))
        elif mode == 'endpoint_nonatomic_key':
            steps.append(('remote-effect-before-key-record',
                          replace(state, remote_effects=state.remote_effects + 1,
                                  phase='remote_unmarked')))
        else:
            # A stable endpoint idempotency key is committed atomically with
            # the actual effect in these two *assumed* endpoint modes.
            recorded = mode in ('endpoint_atomic_key', 'endpoint_expiring_key')
            steps.append(('remote-commits-effect',
                          replace(state, remote_effects=state.remote_effects + 1,
                                  remote_key_recorded=recorded,
                                  phase='remote_committed')))

    if state.phase == 'remote_unmarked':
        # Endpoint-side server crash after effect but before dedup record.
        if state.server_crashes < max_server_crashes:
            steps.append(('remote-server-crashes-before-key-record',
                          replace(state, phase='idle',
                                  server_crashes=state.server_crashes + 1)))
        steps.append(('remote-persist-key-record',
                      replace(state, phase='remote_committed',
                              remote_key_recorded=True)))

    if state.phase == 'request_dropped':
        steps.append(('request-times-out', replace(state, phase='idle')))

    if state.phase in ('remote_committed', 'remote_deduped'):
        steps.append(('response-arrives', replace(state, phase='response_received')))
        steps.append(('response-is-lost', replace(state, phase='idle')))

    if state.phase == 'response_received':
        steps.append(('mark-local-outbox-done', replace(state, local_done=True,
                                                       phase='finished')))

    if state.phase in ('request_ready', 'request_dropped', 'remote_committed',
                       'remote_deduped', 'response_received') and \
                       state.client_crashes < max_client_crashes:
        steps.append(('client-crashes-losing-volatile-progress',
                      replace(state, client_crashes=state.client_crashes + 1,
                              phase='idle')))

    if mode == 'endpoint_expiring_key' and state.remote_key_recorded and \
            state.key_expirations < max_key_expirations:
        # Endpoint may forget its key while local intent remains pending;
        # expiration does not roll back a previously committed remote effect.
        steps.append(('endpoint-idempotency-key-expires',
                      replace(state, remote_key_recorded=False,
                              key_expirations=state.key_expirations + 1)))
    return tuple(steps)


def explore(mode, **bounds):
    """BFS returns the shortest event witness for every reachable state."""
    initial = State()
    visited = {initial: ()}
    queue = deque((initial,))
    while queue:
        state = queue.popleft()
        for action, target in transitions(state, mode, **bounds):
            if target not in visited:
                visited[target] = visited[state] + (action,)
                queue.append(target)
    return visited


def counterexample(mode, property_name, **bounds):
    """Return first violating state and shortest action trace or None.

    at_most_once: global safety, remote_effects <= 1.
    no_false_completion: global safety, local_done implies remote_effects >= 1.
    finite_retry_noncompletion: reachable dead end with local pending and no
      effect, disproving guaranteed successful execution with finite attempts.
    """
    if property_name not in ('at_most_once', 'no_false_completion',
                             'finite_retry_noncompletion'):
        raise ValueError('Unknown property')
    for state, actions in explore(mode, **bounds).items():
        if property_name == 'at_most_once':
            bad = state.remote_effects > 1
        elif property_name == 'no_false_completion':
            bad = state.local_done and state.remote_effects == 0
        else:
            bad = (not state.local_done and state.remote_effects == 0
                   and not transitions(state, mode, **bounds))
        if bad:
            return state, actions
    return None


def report():
    results = []
    for mode in MODES:
        states = explore(mode)
        results.append({
            'mode': mode,
            'reachable_states': len(states),
            'at_most_once': counterexample(mode, 'at_most_once') is None,
            'no_false_completion': counterexample(mode, 'no_false_completion') is None,
            'uncompleted_with_finite_retries': counterexample(
                mode, 'finite_retry_noncompletion') is not None,
        })
    return results


if __name__ == '__main__':
    for row in report():
        print(row)
