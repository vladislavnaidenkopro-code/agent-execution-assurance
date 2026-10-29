"""Link manuscript table inputs to deterministic live model outputs."""
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
from reproduce_results import model_data, canonical, sha256_manifest, main

EXPECTED_SHA256 = '107cd7814ed89696f2539373c25b027961d7382beb0aa3820933a73cca761f94'

class ReproductionManifestTests(unittest.TestCase):
    def test_manifest_digest_pins_current_model_results(self):
        self.assertEqual(sha256_manifest(model_data()), EXPECTED_SHA256)

    def test_finite_counts_and_nonprobabilistic_claim_scope(self):
        d = model_data()
        self.assertIn('not reliability statistics', d['disclaimer'])
        self.assertEqual(sum(v['admissible_worlds'] for v in d['finite_worlds'].values()), 20)
        self.assertEqual(d['downstream_fanout']['no_downstream_dedup']['reachable_states'], 10)
        self.assertIsNone(d['downstream_fanout']['downstream_atomic_key']['downstream_duplicate_trace'])
        self.assertIsNotNone(d['downstream_fanout']['no_downstream_dedup']['downstream_duplicate_trace'])

    def test_manifest_roundtrip_verification_and_mutation_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'evidence.json'
            d = model_data()
            p.write_text(json.dumps(d), encoding='utf8')
            with redirect_stdout(StringIO()) as buffer:
                main(['--verify', str(p)])
            self.assertIn('PASS: manifest matches', buffer.getvalue())
            d['downstream_fanout']['downstream_atomic_key']['reachable_states'] += 1
            p.write_text(json.dumps(d), encoding='utf8')
            with self.assertRaises(SystemExit) as cm:
                main(['--verify', str(p)])
            self.assertIn('FAIL', str(cm.exception))

    def test_canonical_output_is_stable(self):
        d = model_data()
        self.assertEqual(canonical(d), canonical(json.loads(canonical(d))))
        self.assertEqual(sha256_manifest(d), sha256_manifest(json.loads(canonical(d))))

if __name__ == '__main__':
    unittest.main()
