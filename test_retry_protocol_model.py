"""Safety, loss and crash/retry witnesses from explicit state exploration."""
import unittest
from retry_protocol_model import (PROTOCOLS, State, explore, model_report,
                                  shortest_counterexample, successors)


class RetryProtocolModelTests(unittest.TestCase):
    def test_complete_state_graphs_have_only_valid_stages(self):
        for protocol in PROTOCOLS:
            with self.subTest(protocol=protocol):
                states = explore(protocol)
                self.assertTrue(states)
                self.assertTrue(any(s.phase == "finished" for s in states))
                self.assertTrue(all(s.attempts <= 2 and s.crashes <= 1 for s in states))

    def test_effect_then_mark_has_shortest_duplicate_witness(self):
        state, trace = shortest_counterexample("effect_then_mark", "at_most_once")
        self.assertEqual(state.effects, 2)
        self.assertEqual(trace, (
            "begin-attempt", "commit-external-effect", "crash-lose-volatile-phase",
            "begin-attempt", "commit-external-effect"))

    def test_mark_then_effect_avoids_duplicates_but_loses_effect_after_crash(self):
        self.assertIsNone(shortest_counterexample("mark_then_effect", "at_most_once"))
        state, trace = shortest_counterexample("mark_then_effect", "no_lost_intent")
        self.assertEqual((state.effects, state.marker, state.phase), (0, True, "finished"))
        self.assertEqual(trace, (
            "begin-attempt", "write-durable-marker", "crash-lose-volatile-phase",
            "retry-reads-durable-marker"))

    def test_atomic_avoids_both_bounded_failure_classes(self):
        self.assertIsNone(shortest_counterexample("atomic", "at_most_once"))
        self.assertIsNone(shortest_counterexample("atomic", "no_lost_intent"))
        self.assertTrue(any(s.effects == 1 and s.acknowledged for s in explore("atomic")))

    def test_atomic_may_have_unacknowledged_commit(self):
        self.assertTrue(any(s.effects == 1 and not s.acknowledged
                            for s in explore("atomic")))

    def test_crash_restarts_volatile_phase_only(self):
        crashable = [s for s in explore("atomic") if s.phase == "atomic_done"]
        self.assertTrue(crashable)
        s = crashable[0]
        crash = [after for action, after in successors(s, "atomic")
                 if action.startswith("crash")][0]
        self.assertEqual((s.effects, s.marker), (crash.effects, crash.marker))
        self.assertEqual(crash.phase, "idle")

    def test_without_crashes_all_protocols_have_no_reachable_loss_or_duplicate(self):
        for protocol in PROTOCOLS:
            with self.subTest(protocol=protocol):
                states = explore(protocol, max_crashes=0)
                self.assertFalse(any(s.effects > 1 for s in states))
                self.assertFalse(any(s.phase == "finished" and s.effects == 0 for s in states))

    def test_report_consistent_with_exploration(self):
        reports = {r["protocol"]: r for r in model_report()}
        self.assertEqual(set(reports), set(PROTOCOLS))
        self.assertFalse(reports["effect_then_mark"]["at_most_once"])
        self.assertTrue(reports["mark_then_effect"]["at_most_once"])
        self.assertFalse(reports["mark_then_effect"]["terminal_intent_never_lost"])
        self.assertTrue(reports["atomic"]["terminal_intent_never_lost"])

    def test_reject_invalid_input(self):
        with self.assertRaises(ValueError):
            explore("not-a-protocol")
        with self.assertRaises(ValueError):
            successors(State(), "atomic", max_attempts=0)
        with self.assertRaises(ValueError):
            shortest_counterexample("atomic", "exactly_once")

    def test_observation_not_equal_to_outcome(self):
        # A committed external effect can exist without delivered acknowledgement.
        states = explore("effect_then_mark")
        self.assertTrue(any(s.effects > 0 and not s.acknowledged for s in states))


if __name__ == "__main__":
    unittest.main()
