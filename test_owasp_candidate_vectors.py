"""Regression tests for *unsubmitted* OWASP-aligned negative-case candidates."""
import json
import unittest

from owasp_candidate_vectors import vectors
from exhaustive_assurance import exhaustive_universes
from trace_assurance import classify, UNKNOWN, ESTABLISHED, REFUTED
from external_effect_model import State as Remote, transitions as remote_steps
from concurrent_effect_model import State as Concurrent, transitions as concurrent_steps
from multi_effect_model import State as Fanout, transitions as fanout_steps
from external_effect_adversarial import (AdversarialState,
                                         extended_transitions as adversarial_steps)


class EvidenceGapCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = vectors()
        cls.cases = {case['id']: case for case in cls.bundle['cases']}

    def test_bundle_does_not_impersonate_official_owasp_schema(self):
        self.assertEqual(self.bundle['format'], 'vlads-agentic-evidence-candidate-v1')
        self.assertEqual(self.bundle['status'],
                         'INTERNAL_DRAFT_NOT_SUBMITTED_NOT_OWASP_SCHEMA')
        self.assertIn('not', self.bundle['disclaimer'].lower())
        self.assertEqual(len(self.cases), 7)

    def test_identifier_uniqueness_and_case_shape(self):
        self.assertEqual(len(self.cases), len(self.bundle['cases']))
        for case in self.bundle['cases']:
            self.assertTrue(case['id'].startswith('AE-CAND-'))
            self.assertTrue(case['basis'].endswith('.py') or '.py / ' in case['basis'])
            self.assertTrue(case['required_boundary'])
            self.assertIn(case['expected_inference'],
                          ('NOT_ESTABLISHED', 'CLAIM_REFUTED_WITHIN_BOUNDED_MODEL'))

    def test_colliding_worlds_are_real_safe_unsafe_pairs(self):
        domain_for_case = {
            'AE-CAND-AUTH-001': 'authorization',
            'AE-CAND-EFFECT-001': 'at_most_once',
            'AE-CAND-LOG-001': 'prefix_continuity',
        }
        for case_id, domain in domain_for_case.items():
            with self.subTest(case=case_id):
                case = self.cases[case_id]
                pair = case['compatible_worlds']
                self.assertEqual(len(pair), 2)
                self.assertEqual({w['claim_true'] for w in pair}, {True, False})
                self.assertNotEqual(pair[0]['enriched_evidence'],
                                    pair[1]['enriched_evidence'])
                worlds = exhaustive_universes()[domain]
                observed = tuple(case['observed_weak_evidence'])
                self.assertEqual(classify(worlds, observed, enriched=False,
                                          require_trust=True), UNKNOWN)
                enriched_verdicts = {
                    classify(worlds, tuple(w['enriched_evidence']),
                             enriched=True, require_trust=True)
                    for w in pair
                }
                self.assertEqual(enriched_verdicts, {ESTABLISHED, REFUTED})

    @staticmethod
    def replay(initial, trace, relation):
        state = initial
        for action in trace:
            targets = [next_state for name, next_state in relation(state)
                       if name == action]
            if len(targets) != 1:
                raise AssertionError((action, state, targets))
            state = targets[0]
        return state

    def test_lost_response_remote_duplicate_trace(self):
        case = self.cases['AE-CAND-RETRY-001']
        trace = case['event_trace']
        s = self.replay(Remote(), trace, lambda state: remote_steps(
            state, 'outbox_only', max_client_crashes=0, max_server_crashes=0))
        self.assertEqual(s.remote_effects, 2)
        self.assertEqual(case['observed_terminal_counters']['remote_effects'], 2)
        self.assertIn('response-is-lost', trace)
        self.assertFalse(any('crash' in event for event in trace))

    def test_race_trace_reaches_two_effects_without_failure(self):
        case = self.cases['AE-CAND-RACE-001']
        s = self.replay(Concurrent(), case['event_trace'],
                        lambda state: concurrent_steps(
                            state, 'check_then_effect_then_mark'))
        self.assertEqual(s.effects, 2)
        self.assertEqual(len(case['event_trace']), 4)
        self.assertFalse(any('crash' in event for event in case['event_trace']))

    def test_fanout_duplicate_preserves_primary_atomicity(self):
        case = self.cases['AE-CAND-FANOUT-001']
        s = self.replay(Fanout(), case['event_trace'],
                        lambda state: fanout_steps(state, 'no_downstream_dedup'))
        self.assertEqual(s.primary_effects, 1)
        self.assertTrue(s.primary_marker)
        self.assertEqual(s.downstream_effects, 2)
        self.assertEqual(case['observed_terminal_counters']['downstream_effects'], 2)

    def test_forged_success_is_conditional_on_withdrawn_trust(self):
        case = self.cases['AE-CAND-FORGERY-001']
        s = self.replay(AdversarialState(), case['event_trace'],
                        lambda state: adversarial_steps(state,
                            allow_key_rollback=False,
                            allow_forged_success=True))
        self.assertTrue(s.base.local_done)
        self.assertEqual(s.base.remote_effects, 0)
        self.assertEqual(case['observed_terminal_counters']['remote_effects'], 0)
        self.assertTrue(case['observed_terminal_counters']['local_done'])
        self.assertIn('adversary-forges-success-response', case['event_trace'])

    def test_json_export_is_deterministic_and_public_only(self):
        first = json.dumps(vectors(), sort_keys=True, separators=(',', ':'))
        second = json.dumps(vectors(), sort_keys=True, separators=(',', ':'))
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), self.bundle)
        self.assertNotIn('H:\\OPENAI_WORKSPACE', first)
        self.assertNotIn('production credentials', first.lower())

    def test_each_counterexample_is_explicitly_bounded(self):
        for case in self.bundle['cases']:
            if case['kind'] == 'shortest_reachable_counterexample':
                self.assertEqual(case['expected_inference'],
                                 'CLAIM_REFUTED_WITHIN_BOUNDED_MODEL')
                self.assertTrue(case['event_trace'])
                self.assertTrue(case['required_boundary'])
            else:
                self.assertEqual(case['expected_inference'], 'NOT_ESTABLISHED')


if __name__ == '__main__':
    unittest.main()
