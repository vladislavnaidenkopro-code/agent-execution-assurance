"""Metamorphic checks over all worlds of the declared bounded grammar."""
import unittest

from exhaustive_assurance import (
    PrefixContinuityTrace, exhaustive_universes, observation_classes,
    ambiguous_witness, model_check,
)
from trace_assurance import classify, ESTABLISHED, REFUTED, UNKNOWN, INCONSISTENT


class ExhaustiveModelChecks(unittest.TestCase):
    def test_finite_universe_is_exhaustive_for_declared_grammar(self):
        worlds = exhaustive_universes()
        self.assertEqual({key: len(w) for key, w in worlds.items()}, {
            'authorization': 4, 'at_most_once': 4,
            'head_monotonicity': 4, 'prefix_continuity': 8})
        for name, ws in worlds.items():
            with self.subTest(name=name):
                self.assertEqual(len(set(ws)), len(ws))

    def test_baseline_cannot_establish_claim_in_any_domain(self):
        for name, ws in exhaustive_universes().items():
            with self.subTest(name=name):
                pair = ambiguous_witness(ws)
                self.assertIsNotNone(pair)
                self.assertEqual(pair[0].observe(), pair[1].observe())
                self.assertNotEqual(pair[0].safe(), pair[1].safe())
                self.assertEqual(classify(ws, pair[0].observe()), UNKNOWN)

    def test_trusted_enriched_evidence_separates_bounded_cases(self):
        for name, ws in exhaustive_universes().items():
            with self.subTest(name=name):
                classes = observation_classes(ws, enriched=True)
                self.assertIsNone(ambiguous_witness(ws, enriched=True))
                self.assertTrue(any(w.safe() for w in ws if w.trusted()))
                self.assertTrue(any(not w.safe() for w in ws if w.trusted()))
                for observation, compatible in classes.items():
                    expected = ESTABLISHED if compatible[0].safe() else REFUTED
                    self.assertEqual(classify(ws, observation, enriched=True), expected)

    def test_untrusted_enriched_evidence_is_ambiguous_in_all_domains(self):
        for name, ws in exhaustive_universes().items():
            with self.subTest(name=name):
                collision = ambiguous_witness(ws, enriched=True, require_trust=False)
                self.assertIsNotNone(collision)
                self.assertNotEqual(collision[0].safe(), collision[1].safe())
                self.assertEqual(classify(ws, collision[0].observe(True), enriched=True,
                                          require_trust=False), UNKNOWN)

    def test_refinement_never_merges_previously_separated_worlds(self):
        for name, ws in exhaustive_universes().items():
            for trust in (True, False):
                with self.subTest(name=name, trust=trust):
                    coarse = observation_classes(ws, require_trust=trust)
                    refined = observation_classes(ws, enriched=True, require_trust=trust)
                    for group in refined.values():
                        self.assertEqual(len({w.observe() for w in group}), 1)
                    self.assertEqual(sum(map(len, coarse.values())),
                                     sum(map(len, refined.values())))

    def test_underapproximation_makes_a_false_positive_possible(self):
        for name, ws in exhaustive_universes().items():
            with self.subTest(name=name):
                pair = ambiguous_witness(ws)
                safe = next(w for w in pair if w.safe())
                bad = next(w for w in pair if not w.safe())
                observation = safe.observe()
                self.assertEqual(classify((safe,), observation), ESTABLISHED)
                self.assertEqual(classify((safe, bad), observation), UNKNOWN)

    def test_equal_height_is_not_prefix_continuity(self):
        ws = exhaustive_universes()['prefix_continuity']
        trusted = [w for w in ws if w.trusted()]
        good = next(w for w in trusted if w.safe())
        bad = next(w for w in trusted if not w.safe())
        self.assertEqual(good.observe(), bad.observe())
        self.assertNotEqual(good.observe(True), bad.observe(True))
        self.assertEqual(classify(ws, good.observe()), UNKNOWN)

    def test_impossible_observation_is_not_refutation(self):
        for name, ws in exhaustive_universes().items():
            with self.subTest(name=name):
                self.assertEqual(classify(ws, ('unauthenticated-impossible',),
                                          enriched=True), INCONSISTENT)

    def test_invalid_prefix_rejected(self):
        with self.assertRaises(ValueError):
            PrefixContinuityTrace(('genesis', 'a'), ('genesis', 'c'), ('genesis', 'a'))

    def test_model_check_table_covers_each_scope(self):
        rows = model_check()
        self.assertEqual(len(rows), 12)
        for claim in exhaustive_universes():
            matching = [row for row in rows if row[0] == claim]
            self.assertEqual(len(matching), 3)
            self.assertTrue(all(row[4] > 0 and row[3] > 0 for row in matching))


if __name__ == '__main__':
    unittest.main()
