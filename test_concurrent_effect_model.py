import unittest
from concurrent_effect_model import (State, MODES, transitions, explore,
                                     shortest_witness, report)


class TwoWorkerInterleavingTests(unittest.TestCase):
    def test_graph_counts_and_no_duplicate_states(self):
        self.assertEqual({m: len(explore(m)) for m in MODES}, {
            'check_then_effect_then_mark': 17,
            'reserve_then_effect': 12,
            'atomic_effect_and_key': 4,
        })

    def test_nonatomic_check_then_effect_duplicates_without_failure(self):
        state, witness = shortest_witness('check_then_effect_then_mark', 'at_most_once')
        self.assertEqual(state.effects, 2)
        self.assertEqual(len(witness), 4)
        self.assertEqual(witness.count('w0:commit-effect') +
                         witness.count('w1:commit-effect'), 2)
        self.assertFalse(any('crash' in action for action in witness))

    def test_atomic_idempotency_invariant_for_every_reachable_transition(self):
        mode = 'atomic_effect_and_key'
        for state in explore(mode):
            self.assertEqual(state.effects, int(state.marker))
            self.assertLessEqual(state.effects, 1)
            for _, target in transitions(state, mode):
                self.assertEqual(target.effects, int(target.marker))
        self.assertIsNone(shortest_witness(mode, 'at_most_once'))
        self.assertIsNone(shortest_witness(mode, 'terminal_effect_exists'))
        self.assertIsNone(shortest_witness(mode, 'no_false_dedup'))

    def test_reservation_avoids_duplicate_but_permits_lost_effect(self):
        mode = 'reserve_then_effect'
        self.assertIsNone(shortest_witness(mode, 'at_most_once'))
        state, witness = shortest_witness(mode, 'terminal_effect_exists')
        self.assertEqual((state.effects, state.marker), (0, True))
        self.assertIn('w0:crash-before-effect', witness)
        self.assertTrue(all(s.effects <= int(s.marker) for s in explore(mode)))

    def test_dedup_observation_cannot_establish_completed_effect(self):
        state, witness = shortest_witness('reserve_then_effect', 'no_false_dedup')
        self.assertEqual((state.effects, state.marker), (0, True))
        self.assertIn('w1:observe-dedup-key', witness)
        self.assertTrue('done' in state.phases)

    def test_shortest_witness_can_be_replayed_exactly(self):
        for mode in MODES:
            for claim in ('at_most_once', 'terminal_effect_exists', 'no_false_dedup'):
                with self.subTest(mode=mode, claim=claim):
                    result = shortest_witness(mode, claim)
                    if result is None:
                        continue
                    final, witness = result
                    current = State()
                    for action in witness:
                        targets = [target for label, target in transitions(current, mode)
                                   if label == action]
                        self.assertEqual(len(targets), 1)
                        current = targets[0]
                    self.assertEqual(current, final)
                    self.assertEqual(witness, explore(mode)[final])

    def test_independent_depth_first_walk_agrees_with_bfs_set(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                seen, stack = set(), [State()]
                while stack:
                    cur = stack.pop()
                    if cur in seen:
                        continue
                    seen.add(cur)
                    stack.extend(target for _, target in transitions(cur, mode))
                self.assertEqual(seen, set(explore(mode)))

    def test_renaming_workers_preserves_reachable_state_set(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                states = set(explore(mode))
                for state in states:
                    inverted = State(tuple(reversed(state.phases)), state.marker, state.effects)
                    self.assertIn(inverted, states)

    def test_report_and_input_validation(self):
        rows = report()
        self.assertEqual(len(rows), 3)
        self.assertIsNotNone(rows[0]['duplicate_effect_witness'])
        self.assertIsNotNone(rows[1]['terminal_missing_effect_witness'])
        self.assertIsNone(rows[2]['duplicate_effect_witness'])
        with self.assertRaises(ValueError):
            transitions(State(), 'unknown')
        with self.assertRaises(ValueError):
            transitions(State(phases=('unknown', 'ready')), 'atomic_effect_and_key')
        with self.assertRaises(ValueError):
            shortest_witness('atomic_effect_and_key', 'infinite_reliability')


if __name__ == '__main__':
    unittest.main()
