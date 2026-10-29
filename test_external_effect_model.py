"""Bounded state-space tests and shortest counterexample witnesses."""
import unittest
from external_effect_model import (MODES, State, transitions, explore,
                                   counterexample, report)


class ExternalEffectModelTests(unittest.TestCase):
    def test_explicit_bounded_graph_sizes(self):
        expected = {'outbox_only': 36, 'endpoint_atomic_key': 30,
                    'endpoint_expiring_key': 57, 'endpoint_nonatomic_key': 44}
        self.assertEqual({mode: len(explore(mode)) for mode in MODES}, expected)

    def test_outbox_only_has_duplicate_even_without_crashes(self):
        state, trace = counterexample('outbox_only', 'at_most_once',
                                      max_client_crashes=0, max_server_crashes=0)
        self.assertEqual(state.remote_effects, 2)
        self.assertEqual(trace, ('begin-request', 'remote-commits-effect',
                                 'response-is-lost', 'begin-request',
                                 'remote-commits-effect'))

    def test_atomic_endpoint_suppresses_duplicate_with_lost_response(self):
        all_states = explore('endpoint_atomic_key')
        self.assertIsNone(counterexample('endpoint_atomic_key', 'at_most_once'))
        self.assertTrue(any(s.remote_effects == 1 and s.remote_key_recorded
                            and s.phase == 'remote_deduped' for s in all_states))
        self.assertTrue(all(s.remote_effects <= 1 for s in all_states))

    def test_endpoint_expiry_makes_duplicate_effect_reachable(self):
        state, trace = counterexample('endpoint_expiring_key', 'at_most_once')
        self.assertEqual(state.remote_effects, 2)
        self.assertIn('endpoint-idempotency-key-expires', trace)
        self.assertEqual(trace.count('remote-commits-effect'), 2)
        self.assertEqual(state.key_expirations, 1)

    def test_suppress_expiry_restores_bounded_at_most_once(self):
        self.assertIsNone(counterexample('endpoint_expiring_key', 'at_most_once',
                                          max_key_expirations=0))

    def test_nonatomic_endpoint_dedup_has_server_crash_witness(self):
        state, trace = counterexample('endpoint_nonatomic_key', 'at_most_once')
        self.assertEqual(state.remote_effects, 2)
        self.assertIn('remote-server-crashes-before-key-record', trace)
        self.assertEqual(trace.count('remote-effect-before-key-record'), 2)
        self.assertEqual(state.server_crashes, 1)

    def test_no_server_crash_makes_nonatomic_case_safe_within_scope(self):
        self.assertIsNone(counterexample('endpoint_nonatomic_key', 'at_most_once',
                                          max_server_crashes=0))

    def test_no_false_completion_all_modes(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assertIsNone(counterexample(mode, 'no_false_completion'))
                self.assertTrue(all(s.remote_effects > 0 for s in explore(mode)
                                    if s.local_done))

    def test_expired_retries_can_leave_intent_pending(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                state, trace = counterexample(mode, 'finite_retry_noncompletion',
                                               max_client_crashes=0)
                self.assertEqual(state.remote_effects, 0)
                self.assertEqual(state.attempts, 2)
                self.assertEqual(state.phase, 'idle')
                self.assertEqual(trace.count('network-drops-request'), 2)
                self.assertFalse(state.local_done)

    def test_remote_commit_does_not_imply_acknowledgement(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assertTrue(any(s.remote_effects > 0 and not s.local_done
                                    for s in explore(mode)))

    def test_client_crash_preserves_remote_key_and_effect(self):
        states = explore('endpoint_atomic_key')
        committed = next(s for s in states if s.phase == 'remote_committed')
        crashes = [t for label, t in transitions(committed, 'endpoint_atomic_key')
                   if label == 'client-crashes-losing-volatile-progress']
        self.assertEqual(len(crashes), 1)
        self.assertEqual(crashes[0].remote_effects, committed.remote_effects)
        self.assertEqual(crashes[0].remote_key_recorded, committed.remote_key_recorded)
        self.assertEqual(crashes[0].phase, 'idle')

    def test_atomic_invariant_under_bounded_parameter_variation(self):
        for attempts in (1, 2, 3):
            for client_crashes in (0, 1, 2):
                for server_crashes in (0, 1):
                    with self.subTest(a=attempts, c=client_crashes, s=server_crashes):
                        states = explore('endpoint_atomic_key', max_attempts=attempts,
                                         max_client_crashes=client_crashes,
                                         max_server_crashes=server_crashes)
                        self.assertTrue(states)
                        self.assertTrue(all(s.remote_effects == int(s.remote_key_recorded)
                                            for s in states))
                        self.assertTrue(all(s.remote_effects <= 1 for s in states))

    def test_replayed_shortest_witnesses_are_valid_transitions(self):
        for mode in MODES:
            for prop in ('at_most_once', 'no_false_completion',
                         'finite_retry_noncompletion'):
                with self.subTest(mode=mode, prop=prop):
                    result = counterexample(mode, prop)
                    if result is None:
                        continue
                    final, witness = result
                    current = State()
                    for event in witness:
                        matches = [dest for label, dest in transitions(current, mode)
                                   if label == event]
                        self.assertEqual(len(matches), 1, (mode, event, current))
                        current = matches[0]
                    self.assertEqual(current, final)
                    # BFS shortest paths: the action count cannot be beaten.
                    graph = explore(mode)
                    self.assertEqual(graph[final], witness)

    def test_report_matches_reachable_properties(self):
        rows = {row['mode']: row for row in report()}
        self.assertEqual(set(rows), set(MODES))
        self.assertTrue(rows['endpoint_atomic_key']['at_most_once'])
        self.assertFalse(rows['outbox_only']['at_most_once'])
        self.assertFalse(rows['endpoint_expiring_key']['at_most_once'])
        self.assertFalse(rows['endpoint_nonatomic_key']['at_most_once'])
        self.assertTrue(all(row['no_false_completion'] for row in rows.values()))
        self.assertTrue(all(row['uncompleted_with_finite_retries'] for row in rows.values()))

    def test_reject_invalid_modes_and_bounds(self):
        with self.assertRaises(ValueError):
            explore('unsupported')
        with self.assertRaises(ValueError):
            explore('outbox_only', max_attempts=-1)
        with self.assertRaises(ValueError):
            counterexample('outbox_only', 'exactly_once')
        with self.assertRaises(ValueError):
            transitions(State(phase='unknown'), 'outbox_only')
        with self.assertRaises(ValueError):
            transitions(State(local_done=True), 'outbox_only')


    def test_independent_stack_walk_matches_bfs_state_set(self):
        # An independently structured DFS must find exactly the same states.
        for mode in MODES:
            with self.subTest(mode=mode):
                discovered = set()
                stack = [State()]
                while stack:
                    current = stack.pop()
                    if current in discovered:
                        continue
                    discovered.add(current)
                    stack.extend(after for _, after in transitions(current, mode))
                self.assertEqual(discovered, set(explore(mode)))

    def test_remote_effects_and_local_completion_never_rollback(self):
        # Persistence is an *assumption* of this model, made inspectable here.
        for mode in MODES:
            for state in explore(mode):
                for _, following in transitions(state, mode):
                    self.assertGreaterEqual(following.remote_effects,
                                            state.remote_effects)
                    self.assertGreaterEqual(int(following.local_done),
                                            int(state.local_done))

    def test_key_expiration_does_not_undo_remote_effect(self):
        for state in explore('endpoint_expiring_key'):
            for action, following in transitions(state, 'endpoint_expiring_key'):
                if action == 'endpoint-idempotency-key-expires':
                    self.assertEqual(following.remote_effects,
                                     state.remote_effects)
                    self.assertFalse(following.remote_key_recorded)
                    self.assertTrue(state.remote_key_recorded)


if __name__ == '__main__':
    unittest.main()
