"""Proposed OWASP Agentic Evidence negative-case fixtures; NOT an OWASP schema.

Cases are generated from the project's existing bounded public synthetic
models. This is a proof-of-concept for prospective maintainer discussion,
not an OWASP contribution, endorsement, security test suite, or attestation.
"""
import json
from dataclasses import asdict

from exhaustive_assurance import exhaustive_universes, ambiguous_witness
from trace_assurance import classify, UNKNOWN
from external_effect_model import counterexample as external_counterexample
from concurrent_effect_model import shortest_witness as concurrent_witness
from multi_effect_model import witness as fanout_witness
from external_effect_adversarial import shortest_violation as adversarial_witness


def _world_pair(domain, claim, needed):
    worlds = exhaustive_universes()[domain]
    pair = ambiguous_witness(worlds, enriched=False, require_trust=True)
    if pair is None:
        raise AssertionError('No ambiguous same-evidence pair for ' + domain)
    left, right = pair
    observed = left.observe(False)
    if observed != right.observe(False) or left.safe() == right.safe():
        raise AssertionError('Malformed safe/unsafe observational collision')
    if classify(worlds, observed, enriched=False, require_trust=True) != UNKNOWN:
        raise AssertionError('Expected NOT_ESTABLISHED under weak observation')
    if left.observe(True) == right.observe(True):
        raise AssertionError('Enriched observations fail to distinguish pair')
    return {
        'id': 'AE-CAND-' + claim,
        'kind': 'observational_collision',
        'claim': needed,
        'basis': 'exhaustive_assurance.py / ' + domain,
        'observed_weak_evidence': list(observed),
        'compatible_worlds': [
            {'world': asdict(world), 'claim_true': world.safe(),
             'enriched_evidence': list(world.observe(True))}
            for world in pair
        ],
        'expected_inference': 'NOT_ESTABLISHED',
        'required_boundary': 'Authenticity and completeness of enriched records are assumptions, not verified by this model.'
    }


def _generated_trace(case_id, claim, basis, result, caveat):
    if result is None:
        raise AssertionError('No negative witness for ' + case_id)
    state, trace = result
    measured = getattr(state, 'base', state)
    if not trace:
        raise AssertionError('Empty witness for ' + case_id)
    return {
        'id': case_id,
        'kind': 'shortest_reachable_counterexample',
        'claim': claim,
        'basis': basis,
        'event_trace': list(trace),
        'expected_inference': 'CLAIM_REFUTED_WITHIN_BOUNDED_MODEL',
        'observed_terminal_counters': {
            'remote_effects': getattr(measured, 'remote_effects', None),
            'downstream_effects': getattr(measured, 'downstream_effects', None),
            'local_done': getattr(measured, 'local_done', None),
        },
        'required_boundary': caveat
    }


def vectors():
    cases = [
        _world_pair('authorization', 'AUTH-001', 'Authorization at commit from grant plus receipt'),
        _world_pair('at_most_once', 'EFFECT-001', 'At-most-once committed effect from one receipt'),
        _world_pair('prefix_continuity', 'LOG-001', 'Append-only prefix continuity from equal log heights'),
        _generated_trace(
            'AE-CAND-RETRY-001', 'Local outbox implies no duplicate remote effect',
            'external_effect_model.py / outbox_only',
            external_counterexample('outbox_only', 'at_most_once',
                                    max_client_crashes=0, max_server_crashes=0),
            'A lost response after a durable external effect permits a retry; no server-side dedup is assumed.'),
        _generated_trace(
            'AE-CAND-RACE-001', 'One intent and shared key prevent concurrent duplicate effects',
            'concurrent_effect_model.py / check_then_effect_then_mark',
            concurrent_witness('check_then_effect_then_mark', 'at_most_once'),
            'Key check and effect are separate operations; two workers can overlap.'),
        _generated_trace(
            'AE-CAND-FANOUT-001', 'Primary atomic intent commit covers downstream at-most-once',
            'multi_effect_model.py / no_downstream_dedup',
            fanout_witness('no_downstream_dedup', 'downstream_at_most_once'),
            'Primary and downstream effects are distinct authorized outcomes; both require separate scope checks.'),
        _generated_trace(
            'AE-CAND-FORGERY-001', 'Reported local completion proves remote effect occurred',
            'external_effect_adversarial.py / forged_success',
            adversarial_witness('no_false_completion',
                                allow_key_rollback=False,
                                allow_forged_success=True),
            'This adversarial extension explicitly withdraws the authentic-success-response assumption.')
    ]
    ids = [case['id'] for case in cases]
    if len(set(ids)) != len(ids):
        raise AssertionError('Duplicate fixture IDs')
    return {
        'format': 'vlads-agentic-evidence-candidate-v1',
        'status': 'INTERNAL_DRAFT_NOT_SUBMITTED_NOT_OWASP_SCHEMA',
        'source': 'public synthetic bounded VLADS Reputation research',
        'target_for_discussion': 'https://github.com/OWASP/Agentic-Evidence',
        'disclaimer': (
            'Negative cases illustrate observability limits and bounded execution safety. '
            'They do not establish exploitability, real-system detection, OWASP endorsement, '
            'or a standardized evidence schema. Maintainer issue and schema mapping needed.'
        ),
        'cases': cases
    }


def main():
    print(json.dumps(vectors(), sort_keys=True, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
