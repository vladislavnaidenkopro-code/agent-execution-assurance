import unittest
from counterexamples import World, cases, verdict

class EvidenceTests(unittest.TestCase):
    def test_three_indistinguishable_pairs(self):
        for name, worlds in cases().items():
            with self.subTest(name=name):
                self.assertEqual(worlds[0].observation, worlds[1].observation)
                self.assertNotEqual(worlds[0].property_holds, worlds[1].property_holds)
                self.assertEqual(verdict(worlds), 'NOT_ESTABLISHED')

    def test_positive_and_negative_controls(self):
        w = World(('evidence',), True, 'control')
        n = World(('evidence',), False, 'control')
        self.assertEqual(verdict((w,w)), 'ESTABLISHED_WITHIN_MODEL')
        self.assertEqual(verdict((n,n)), 'REFUTED_WITHIN_MODEL')

    def test_reject_mismatched_observations(self):
        with self.assertRaises(ValueError):
            verdict((World(('a',), True, ''), World(('b',), False, '')))

    def test_reject_empty_set(self):
        with self.assertRaises(ValueError):
            verdict(())

if __name__ == '__main__': unittest.main()
