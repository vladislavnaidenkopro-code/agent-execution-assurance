import unittest
from assurance_models import classify, scenarios, residual_failures, ESTABLISHED, REFUTED, UNKNOWN, INCONSISTENT

class AssuranceModelsTests(unittest.TestCase):
    def test_baseline_is_underdetermined(self):
        for name, histories in scenarios().items():
            with self.subTest(name=name):
                self.assertEqual(classify(histories, histories[0].baseline), UNKNOWN)

    def test_enriched_evidence_sufficient_under_assumptions(self):
        for name, histories in scenarios().items():
            with self.subTest(name=name):
                self.assertEqual(classify(histories, histories[0].enriched, 'enriched'), ESTABLISHED)
                self.assertEqual(classify(histories, histories[1].enriched, 'enriched'), REFUTED)

    def test_multiple_compatible_histories_can_establish(self):
        for name, histories in scenarios().items():
            with self.subTest(name=name):
                compatible = [h for h in histories if h.enriched == histories[0].enriched]
                self.assertEqual(len(compatible), 2)
                self.assertEqual(classify(histories, histories[0].enriched, 'enriched'), ESTABLISHED)

    def test_residual_assumption_failure_reintroduces_ambiguity(self):
        for name, histories in residual_failures().items():
            with self.subTest(name=name):
                self.assertEqual(classify(histories, histories[0].enriched, 'enriched'), UNKNOWN)

    def test_impossible_observation_is_inconsistent(self):
        for histories in scenarios().values():
            self.assertEqual(classify(histories, ('impossible',)), INCONSISTENT)

    def test_empty_model_is_inconsistent(self):
        self.assertEqual(classify((), ('anything',)), INCONSISTENT)

if __name__ == '__main__': unittest.main()
