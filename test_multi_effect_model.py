"""Negative and positive controls for one primary + one downstream effect."""
import unittest
from multi_effect_model import State, MODES, explore, transitions, witness, report

class MultiEffectBoundaryTests(unittest.TestCase):
    def test_bounded_graph_cardinalities(self):
        self.assertEqual({m: len(explore(m)) for m in MODES}, {
            'no_downstream_dedup': 10,
            'downstream_atomic_key': 10,
            'downstream_expiring_key': 20,
            'downstream_nonatomic_key': 17,
        })

    def test_primary_intent_atomicity_not_end_to_end_guarantee(self):
        for mode in MODES:
            self.assertIsNone(witness(mode, 'primary_at_most_once'))
            self.assertTrue(all(s.primary_effects <= 1 for s in explore(mode)))
        self.assertIsNotNone(witness('no_downstream_dedup', 'downstream_at_most_once'))

    def test_no_downstream_dedup_duplicate_witness(self):
        bad, trace = witness('no_downstream_dedup', 'downstream_at_most_once')
        self.assertEqual((bad.primary_effects, bad.downstream_effects), (1, 2))
        self.assertEqual(trace, (
            'atomic-primary-effect-and-intent-marker',
            'deliver-outbox-event', 'commit-downstream-effect',
            'lose-downstream-acknowledgement', 'deliver-outbox-event',
            'commit-downstream-effect'))

    def test_atomic_downstream_key_prevents_duplicates(self):
        self.assertIsNone(witness('downstream_atomic_key', 'downstream_at_most_once'))
        for state in explore('downstream_atomic_key'):
            self.assertEqual(state.downstream_effects, int(state.downstream_marker))
            self.assertLessEqual(state.downstream_effects, 1)

    def test_expiring_remote_downstream_marker_allows_duplicate(self):
        bad, trace = witness('downstream_expiring_key', 'downstream_at_most_once')
        self.assertEqual(bad.downstream_effects, 2)
        self.assertIn('expire-downstream-key', trace)
        self.assertEqual(trace.count('commit-downstream-effect'), 2)

    def test_nonatomic_remote_downstream_marker_allows_duplicate(self):
        bad, trace = witness('downstream_nonatomic_key', 'downstream_at_most_once')
        self.assertEqual(bad.downstream_effects, 2)
        self.assertIn('remote-crash-before-key', trace)
        self.assertEqual(trace.count('commit-downstream-before-recording-key'), 2)

    def test_control_no_crash_restores_downstream_safety_for_nonatomic(self):
        self.assertIsNone(witness('downstream_nonatomic_key', 'downstream_at_most_once',
                                  max_server_crashes=0))

    def test_control_no_expiry_restores_downstream_safety(self):
        self.assertIsNone(witness('downstream_expiring_key', 'downstream_at_most_once',
                                  max_key_expirations=0))

    def test_acknowledgement_is_not_forged_in_this_model(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assertIsNone(witness(mode, 'both_effects_if_acknowledged'))
                self.assertTrue(any(s.ack_received for s in explore(mode)))
                self.assertTrue(all(s.downstream_effects >= 1 for s in explore(mode)
                                    if s.ack_received))

    def test_unacknowledged_commits_reachable(self):
        for mode in MODES:
            self.assertTrue(any(s.downstream_effects >= 1 and not s.ack_received
                                for s in explore(mode)))

    def test_no_delivery_budget_invalidates_guaranteed_downstream(self):
        for mode in MODES:
            bad, trace = witness(mode, 'downstream_guaranteed', max_deliveries=0)
            self.assertEqual((bad.primary_effects, bad.downstream_effects), (1, 0))
            self.assertEqual(trace, ('atomic-primary-effect-and-intent-marker',))

    def test_witnesses_replay_exactly(self):
        for mode in MODES:
            for prop in ('primary_at_most_once', 'downstream_at_most_once',
                         'both_effects_if_acknowledged', 'downstream_guaranteed'):
                with self.subTest(mode=mode, prop=prop):
                    result = witness(mode, prop)
                    if result is None:
                        continue
                    dest, actions = result
                    current = State()
                    for action in actions:
                        transitions_by_name = [s for label, s in transitions(current, mode)
                                               if label == action]
                        self.assertEqual(len(transitions_by_name), 1)
                        current = transitions_by_name[0]
                    self.assertEqual(current, dest)
                    self.assertEqual(actions, explore(mode)[dest])

    def test_independent_DFS_reachability(self):
        for mode in MODES:
            seen, stack = set(), [State()]
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                stack.extend(s for _, s in transitions(current, mode))
            self.assertEqual(seen, set(explore(mode)))

    def test_expected_report_truth_values(self):
        rows = report()
        self.assertEqual(len(rows), 4)
        for mode, size, primary, downstream, ack in rows:
            self.assertTrue(primary and ack)
            self.assertGreater(size, 0)
            self.assertEqual(downstream, mode == 'downstream_atomic_key')

    def test_durable_effects_are_monotonic(self):
        for mode in MODES:
            for state in explore(mode):
                for _, nxt in transitions(state, mode):
                    self.assertGreaterEqual(nxt.primary_effects, state.primary_effects)
                    self.assertGreaterEqual(nxt.downstream_effects, state.downstream_effects)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            explore('not-a-mode')
        with self.assertRaises(ValueError):
            transitions(State(), 'downstream_atomic_key', max_deliveries=-1)
        with self.assertRaises(ValueError):
            transitions(State(phase='unknown'), 'downstream_atomic_key')
        with self.assertRaises(ValueError):
            witness('downstream_atomic_key', 'exactly_once_delivery')

if __name__ == '__main__':
    unittest.main()
