"""Bounded falsification and shortest-witness replay for withdrawn trust assumptions."""
import unittest
from external_effect_model import explore as original_explore
from external_effect_adversarial import (AdversarialState,extended_transitions,
                                         explore,report,shortest_violation)

class ThreatModelExpansionTests(unittest.TestCase):
    def test_zero_attacks_exactly_matches_original_endpoint_atomic_graph(self):
        opts=dict(allow_key_rollback=False,allow_forged_success=False)
        worlds=explore(**opts)
        self.assertEqual({w.base for w in worlds},set(original_explore('endpoint_atomic_key')))
        self.assertEqual(len(worlds),30)
    def test_key_rollback_enables_duplicate_external_effect(self):
        state,witness=shortest_violation('at_most_once',allow_forged_success=False)
        self.assertEqual(state.base.remote_effects,2)
        self.assertIn('adversary-erases-remote-dedup-key',witness)
        self.assertEqual(witness.count('remote-commits-effect'),2)
    def test_forged_success_causes_false_local_completion(self):
        state,witness=shortest_violation('no_false_completion',allow_key_rollback=False)
        self.assertTrue(state.base.local_done)
        self.assertEqual(state.base.remote_effects,0)
        self.assertIn('adversary-forges-success-response',witness)
    def test_key_rollback_alone_does_not_forge_completion(self):
        self.assertIsNone(shortest_violation('no_false_completion',
                            allow_key_rollback=True,allow_forged_success=False))
    def test_forgery_alone_does_not_duplicate_remote_effect(self):
        self.assertIsNone(shortest_violation('at_most_once',
                            allow_key_rollback=False,allow_forged_success=True))
    def test_original_assumptions_recover_both_safety_properties(self):
        opts=dict(allow_key_rollback=False,allow_forged_success=False)
        self.assertIsNone(shortest_violation('at_most_once',**opts))
        self.assertIsNone(shortest_violation('no_false_completion',**opts))
    def test_every_generated_witness_is_replayable(self):
        for row in report():
            opts=dict(allow_key_rollback=row['key_rollback'],
                      allow_forged_success=row['forged_success'])
            for key in ('duplicate','false_completion'):
                evidence=row[key]
                if evidence is None:
                    continue
                expected,actions=evidence
                current=AdversarialState()
                for action in actions:
                    next_states=[s for event,s in extended_transitions(current,**opts)
                                 if event==action]
                    self.assertEqual(len(next_states),1)
                    current=next_states[0]
                self.assertEqual(current,expected)
    def test_each_attack_occurs_at_most_once(self):
        for state in explore():
            self.assertLessEqual(state.key_rollbacks,1)
            self.assertLessEqual(state.forged_successes,1)
            self.assertLessEqual(state.base.remote_effects,2)
    def test_effects_remain_durable_under_adversarial_changes(self):
        for state in explore():
            for _,target in extended_transitions(state):
                self.assertGreaterEqual(target.base.remote_effects,state.base.remote_effects)
    def test_enabling_attacks_cannot_shrink_reachable_state_set(self):
        baseline=set(explore(allow_key_rollback=False,allow_forged_success=False))
        rollback=set(explore(allow_key_rollback=True,allow_forged_success=False))
        forgery=set(explore(allow_key_rollback=False,allow_forged_success=True))
        both=set(explore())
        self.assertTrue(baseline<=rollback)
        self.assertTrue(baseline<=forgery)
        self.assertTrue(rollback<=both and forgery<=both)

if __name__=='__main__':
    unittest.main()
