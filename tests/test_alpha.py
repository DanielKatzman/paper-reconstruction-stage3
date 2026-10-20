import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from alpha_fixtures import production_many, rows_for
from paper_reconstruction_stage3.alpha_bundle import export_bundle, group_records
from paper_reconstruction_stage3.alpha_inference import FeatureBank, production_inputs, sliding_starts
from paper_reconstruction_stage3.contracts import ContractError, atomic_json, digest
from paper_reconstruction_contracts import load_bundle, relative_file


class AlphaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup); self.root = Path(self.temp.name).resolve()
        self.cfg = production_many(self.root/'inputs')
        self.entries, self.gallery, _ = production_inputs(self.cfg['stage1'], self.cfg['stage2'])
        # The package's checked physical configuration is numerical, without labels.
        self.configuration = {'pose_configuration': {'collision_grid': 24, 'maximum_assembly_collision': .08,
            'cycle_tolerance_px': 8., 'beam_width': 16}, 'policy': {}}

    def export(self, variants=None, output=None):
        output = output or self.root/'bundle'
        m = export_bundle(output, 'synthetic', self.entries, self.gallery, variants or rows_for(self.gallery),
                          provenance={'kind': 'synthetic'}, configuration=self.configuration)
        return output, m

    def test_occurrences_retain_duplicate_aliases_and_support(self):
        variants = rows_for(self.gallery); a = variants['source_control']['records'][0]
        b = copy.deepcopy(a); b['pose']['span_a'] = {'start_px': 1., 'end_px': 10.}; b['pose']['alignment']['query_arc_fraction'] = [.25, .5]
        b['visual_evidence'] = {'informative': True, 'central_correlation': .7}; b['methods']['mlp_start']['weight'] = .6
        variants['source_control']['records'].append(b)
        variants['other_branch'] = {'records': [copy.deepcopy(a)]}
        output, m = self.export(variants); groups = list(load_bundle(output, full=True).hypotheses())
        self.assertEqual((m['counts']['geometries'], m['counts']['occurrences']), (1, 3))
        got = {(r['variant'], r['row_index']): r for r in groups[0]['occurrences']}
        for name, trace in variants.items():
            for index, row in enumerate(trace['records']):
                for key in ('record_id', 'pose', 'methods', 'visual_evidence'):
                    self.assertEqual(got[name, index][key], row[key])

    def test_reverse_direction_maps_to_same_native_pair(self):
        variants = rows_for(self.gallery); row = variants['source_control']['records'][0]; reverse = copy.deepcopy(row)
        reverse['pose'].update(query=1, target=0); reverse['pose']['alignment']['transform'] = np.linalg.inv(row['pose']['alignment']['transform']).tolist()
        variants['source_control']['records'].append(reverse)
        self.assertEqual(len(group_records(self.gallery, variants)), 1)
        output, _ = self.export(variants); load_bundle(output, full=True)

    def test_wrong_canonical_direction_is_rejected(self):
        variants = rows_for(self.gallery); variants['source_control']['records'][0]['canonical_transform_target_b_to_query_a'][0][2] = -40.
        with self.assertRaisesRegex(ContractError, 'direction mismatch'): self.export(variants)

    def test_isolated_zero_candidate_piece_is_retained(self):
        output, m = self.export(); data = load_bundle(output)
        self.assertEqual((m['counts']['pieces'], m['counts']['candidates']), (3, 2))
        self.assertEqual(data.summary()['candidate_graph_components'], [['capture_00', 'capture_01'], ['capture_02']])

    def test_relocation_and_cpu_only_loader(self):
        output, _ = self.export(); relocated = self.root/'relocated'; shutil.copytree(output, relocated)
        script = 'import sys; from paper_reconstruction_contracts import load_bundle; d=load_bundle(sys.argv[1],full=True); assert "torch" not in sys.modules; assert len(d.entries)==3; print("CPU-only relocation passed")'
        done = subprocess.run([sys.executable, '-c', script, str(relocated)], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        manifest_text = (relocated/'bundle.json').read_text()
        self.assertNotIn(str(self.root).replace('\\', '\\\\'), manifest_text)

    def test_native_arrays_are_sanitized(self):
        path = Path(self.entries[0]['arrays_path'])
        with np.load(path, allow_pickle=False) as z: arrays = {k: z[k] for k in z.files}
        np.savez_compressed(path, **arrays, canonical_u=np.full(128, 999))
        output, m = self.export()
        with np.load(output/m['pieces']['capture_00']['contour'], allow_pickle=False) as z:
            self.assertNotIn('canonical_u', z.files); self.assertNotIn('points_xy_source', z.files)

    def test_completed_export_is_immutable_and_idempotent(self):
        output, first = self.export(); before = {p: p.read_bytes() for p in output.rglob('*') if p.is_file()}
        _, second = self.export(); self.assertEqual(first, second)
        self.assertTrue(all(p.read_bytes() == raw for p, raw in before.items()))
        with self.assertRaisesRegex(ContractError, 'different inputs'):
            export_bundle(output, 'changed', self.entries, self.gallery, rows_for(self.gallery), provenance={'kind': 'synthetic'}, configuration=self.configuration)

    def test_interrupted_export_resumes_with_the_same_identity(self):
        from paper_reconstruction_stage3 import alpha_bundle
        original = alpha_bundle.atomic_json
        def interrupted(path, value):
            if Path(path).name == 'working_pool.json': raise KeyboardInterrupt()
            return original(path, value)
        with patch.object(alpha_bundle, 'atomic_json', side_effect=interrupted), self.assertRaises(KeyboardInterrupt): self.export()
        self.assertFalse((self.root/'bundle/bundle.json').exists())
        output, _ = self.export(); load_bundle(output, full=True)

    def test_unknown_nonempty_output_is_rejected(self):
        target = self.root/'occupied'; target.mkdir(); (target/'working_pool.json').write_text('preserve me')
        with self.assertRaisesRegex(ContractError, 'unknown export'): self.export(output=target)
        self.assertEqual((target/'working_pool.json').read_text(), 'preserve me')

    def test_asset_tamper_is_detected(self):
        output, m = self.export(); asset = output/next(iter(m['assets'])); asset.write_bytes(asset.read_bytes()+b'x')
        with self.assertRaisesRegex(ContractError, 'checksum'): load_bundle(output)

    def test_portable_path_escape_is_rejected(self):
        for name in ('../outside', 'C:/outside', '/outside', 'assets\\outside'):
            with self.subTest(name=name), self.assertRaises(ContractError): relative_file(self.root, name)

    def test_duplicate_physical_observation_rejected(self):
        with self.assertRaisesRegex(ContractError, 'one registered'):
            export_bundle(self.root/'bundle', 'synthetic', self.entries+[self.entries[0]], self.gallery,
                          rows_for(self.gallery), provenance={}, configuration=self.configuration)

    def test_empty_candidate_bundle_keeps_complete_inventory(self):
        entries = [{**e, 'candidates': []} for e in self.entries]
        output = self.root/'empty'; m = export_bundle(output, 'empty', entries, [], {}, provenance={}, configuration=self.configuration)
        self.assertEqual(m['counts']['pieces'], 3); self.assertEqual(m['counts']['occurrences'], 0)
        self.assertEqual(len(load_bundle(output, full=True).summary()['candidate_graph_components']), 3)

    def test_stage4_adapter_retains_native_transform(self):
        output, _ = self.export(); data = load_bundle(output, full=True)
        self.assertEqual(data.edges[0]['transform'], [[1., 0., 40.], [0., 1., -1.25], [0., 0., 1.]])
        self.assertEqual(data.edges[0]['a'], 'capture_00')
        self.assertEqual(data.edges[0]['b'], 'capture_01')

    def test_features_and_frozen_scores_match_v0931_control(self):
        from paper_reconstruction_stage3.baselines import BaselineConfig, ObservableInputs
        from paper_reconstruction_stage3.alpha_inference import FrozenRankers
        from paper_reconstruction_stage3.alpha_package import load_package
        root = Path(__file__).resolve().parents[1]
        cfg = production_many(self.root/'parity', pieces=3, zero_last=True, scale=4)
        _, gallery, _ = production_inputs(cfg['stage1'], cfg['stage2'])
        bank = FeatureBank(ObservableInputs(gallery, BaselineConfig()))
        with np.load(root/'tests/v0931_observable_reference.npz', allow_pickle=False) as reference:
            for i in range(2):
                for key, array in bank.features(i).items(): np.testing.assert_array_equal(array, reference[str(i)+'_'+key])
        package, m = load_package(root/'models')
        with patch('sqlite3.connect', side_effect=AssertionError('No label database allowed')):
            scores = FrozenRankers(package, m, 'cpu').score(bank, [(0, 1), (1, 0)], progress=lambda _: None)
        expected = json.loads((root/'tests/v0931_scores.json').read_text())['scores']
        for got, control in zip(scores, expected):
            self.assertEqual((got['query'], got['target']), (control['query'], control['target']))
            for model, score in got['scores'].items(): self.assertAlmostEqual(score, control['scores'][model], places=6)


if __name__ == '__main__': unittest.main()
