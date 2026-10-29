import unittest

from trace_assurance import (AuthorizationTrace, EffectTrace, RollbackTrace,
                             classify, universes, ESTABLISHED, REFUTED,
                             UNKNOWN, INCONSISTENT)


class TraceAssuranceTests(unittest.TestCase):
    def test_baseline_indistinguishable_under_trust(self):
        for name, worlds in universes().items():
            with self.subTest(name=name):
                self.assertEqual(worlds[0].observe(), worlds[1].observe())
                self.assertNotEqual(worlds[0].safe(), worlds[1].safe())
                self.assertEqual(classify(worlds, worlds[0].observe()), UNKNOWN)

    def test_enriched_evidence_separates_safe_unsafe_under_trust(self):
        for name, worlds in universes().items():
            with self.subTest(name=name):
                self.assertEqual(classify(worlds, worlds[0].observe(True), enriched=True), ESTABLISHED)
                self.assertEqual(classify(worlds, worlds[1].observe(True), enriched=True), REFUTED)

    def test_weakening_trust_reintroduces_same_observation(self):
        for name, worlds in universes().items():
            with self.subTest(name=name):
                self.assertFalse(worlds[2].trusted())
                self.assertEqual(worlds[0].observe(True), worlds[2].observe(True))
                self.assertEqual(classify(worlds, worlds[0].observe(True), enriched=True,
                                          require_trust=False), UNKNOWN)

    def test_trust_constraint_excludes_only_invalid_evidence(self):
        for name, worlds in universes().items():
            with self.subTest(name=name):
                self.assertTrue(worlds[0].trusted())
                self.assertTrue(worlds[1].trusted())
                self.assertFalse(worlds[2].trusted())

    def test_empty_compatible_worlds_are_inconsistent(self):
        for worlds in universes().values():
            self.assertEqual(classify(worlds, ('impossible',)), INCONSISTENT)
        self.assertEqual(classify((), ('impossible',)), INCONSISTENT)

    def test_invalid_traces_rejected(self):
        with self.assertRaises(ValueError):
            AuthorizationTrace(('commit',), ('grant',))
        with self.assertRaises(ValueError):
            EffectTrace(('e1', 'e2', 'e3'), ('e1',))
        with self.assertRaises(ValueError):
            RollbackTrace((1, 3), 1, 1)


if __name__ == '__main__':
    unittest.main()
