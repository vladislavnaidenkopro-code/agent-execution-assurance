"""Differential testing compares every labeled transition over multiple bounds."""
import unittest
from dataclasses import replace
from external_effect_model import State, MODES, explore, transitions
from external_effect_spec import EVENTS, spec_step, spec_edges

class AlternateSpecificationTests(unittest.TestCase):
    def test_full_edge_equivalence_for_all_reachable_states(self):
        for mode in MODES:
            for a,c,s,e in ((1,0,0,0),(2,1,1,1),(3,2,1,1),(2,0,2,2)):
                b=dict(max_attempts=a,max_client_crashes=c,
                       max_server_crashes=s,max_key_expirations=e)
                for state in explore(mode,**b):
                    with self.subTest(mode=mode,bounds=b,state=state):
                        self.assertEqual(frozenset(transitions(state,mode,**b)),
                                         spec_edges(state,mode,**b))
    def test_invalid_specification_input(self):
        with self.assertRaises(ValueError):
            spec_step(State(),'unknown','begin-request')
        with self.assertRaises(ValueError):
            spec_step(State(),'outbox_only','nonexistent')
        with self.assertRaises(ValueError):
            spec_step(State(),'outbox_only','begin-request',max_attempts=-1)
    def test_mutation_missing_lost_response_edge_is_detected(self):
        s=replace(State(),phase='remote_committed',remote_effects=1)
        mutated=frozenset(edge for edge in transitions(s,'outbox_only')
                          if edge[0]!='response-is-lost')
        self.assertNotEqual(mutated,spec_edges(s,'outbox_only'))
    def test_mutation_lost_atomic_key_is_detected(self):
        s=replace(State(),phase='request_ready',attempts=1)
        mutated=frozenset((name,replace(target,remote_key_recorded=False)
                           if name=='remote-commits-effect' else target)
                          for name,target in transitions(s,'endpoint_atomic_key'))
        self.assertNotEqual(mutated,spec_edges(s,'endpoint_atomic_key'))
    def test_all_events_exercised(self):
        found=set()
        for mode in MODES:
            for state in explore(mode):
                found.update(label for label,_ in spec_edges(state,mode))
        self.assertEqual(found,set(EVENTS))

if __name__=='__main__':
    unittest.main()
