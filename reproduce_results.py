"""Canonical figures-and-tables input for the bounded execution-assurance study.

Produces data only: state counts, finite property verdicts, and shortest
counterexample event labels. Does not compute probabilities or prove deployment
security. No external dependencies.
"""
import argparse
import hashlib
import json
from pathlib import Path

import exhaustive_assurance
import retry_protocol_model
import external_effect_model
import external_effect_adversarial
import concurrent_effect_model
import multi_effect_model

def _trace(result):
    return None if result is None else list(result[1])

def model_data():
    worlds = exhaustive_assurance.exhaustive_universes()
    baseline = {
        k: {'admissible_worlds': len(v),
            'baseline_ambiguity_exists': exhaustive_assurance.ambiguous_witness(v) is not None,
            'enriched_trusted_ambiguity_exists': exhaustive_assurance.ambiguous_witness(v, enriched=True) is not None,
            'enriched_untrusted_ambiguity_exists': exhaustive_assurance.ambiguous_witness(v, enriched=True, require_trust=False) is not None}
        for k, v in worlds.items()
    }
    retry = {
        k: {'reachable_states': len(retry_protocol_model.explore(k)),
            'duplicate_trace': _trace(retry_protocol_model.shortest_counterexample(k, 'at_most_once')),
            'missing_effect_trace': _trace(retry_protocol_model.shortest_counterexample(k, 'no_lost_intent'))}
        for k in retry_protocol_model.PROTOCOLS
    }
    external = {
        k: {'reachable_states': len(external_effect_model.explore(k)),
            'duplicate_trace': _trace(external_effect_model.counterexample(k, 'at_most_once')),
            'false_completion_trace': _trace(external_effect_model.counterexample(k, 'no_false_completion'))}
        for k in external_effect_model.MODES
    }
    adversarial = {
        '%s_%s' % (rollback, forged): {
            'reachable_states': len(external_effect_adversarial.explore(
                allow_key_rollback=rollback, allow_forged_success=forged)),
            'duplicate_trace': _trace(external_effect_adversarial.shortest_violation(
                'at_most_once', allow_key_rollback=rollback, allow_forged_success=forged)),
            'false_completion_trace': _trace(external_effect_adversarial.shortest_violation(
                'no_false_completion', allow_key_rollback=rollback, allow_forged_success=forged))}
        for rollback in (False, True) for forged in (False, True)
    }
    concurrent = {
        k: {'reachable_states_two_workers': len(concurrent_effect_model.explore(k)),
            'duplicate_trace_two_workers': _trace(concurrent_effect_model.shortest_witness(
                k, 'at_most_once')),
            'no_effect_terminal_trace': _trace(concurrent_effect_model.shortest_witness(
                k, 'terminal_effect_exists'))}
        for k in concurrent_effect_model.MODES
    }
    downstream = {
        k: {'reachable_states': len(multi_effect_model.explore(k)),
            'primary_duplicate_trace': _trace(multi_effect_model.witness(k, 'primary_at_most_once')),
            'downstream_duplicate_trace': _trace(multi_effect_model.witness(k, 'downstream_at_most_once'))}
        for k in multi_effect_model.MODES
    }
    return {'schema': 'vlads-research-bounded-model-results-v1',
            'disclaimer': 'Finite synthetic state counts and witnesses; not reliability statistics or a deployed security proof',
            'finite_worlds': baseline, 'retry_protocols': retry,
            'external_endpoint': external, 'withdrawn_assumptions': adversarial,
            'two_worker_concurrency': concurrent, 'downstream_fanout': downstream}

def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'))

def sha256_manifest(data):
    return hashlib.sha256(canonical(data).encode('utf-8')).hexdigest()

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', metavar='PATH', help='Assert committed manifest equals current model output')
    args = parser.parse_args(argv)
    data = model_data()
    if args.verify:
        target = json.loads(Path(args.verify).read_text(encoding='utf-8'))
        if target != data:
            raise SystemExit('FAIL: model results differ from manifest')
        print('PASS: manifest matches modeled results; sha256=' + sha256_manifest(data))
    else:
        print(json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
