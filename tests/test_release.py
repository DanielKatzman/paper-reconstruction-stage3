import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from alpha_fixtures import production_many, rows_for
from paper_reconstruction_stage3.alpha_bundle import export_bundle
from paper_reconstruction_stage3.alpha_inference import production_inputs
from paper_reconstruction_stage3.unit_scale import configuration, require_rigid
from paper_reconstruction_stage3_release.cli import main, parser, pool_bundle
from paper_reconstruction_contracts import load_bundle

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def native(self, output, puzzle='synthetic'):
        inputs = production_many(self.root/(output.name+'_inputs'))
        entries, gallery, _ = production_inputs(inputs['stage1'], inputs['stage2'])
        export_bundle(output, puzzle, entries, gallery, rows_for(gallery), provenance={},
                      configuration={'pose_configuration': {'maximum_assembly_collision': .08}, 'policy': {}})
        return inputs

    def test_cpu_is_public_default_and_cuda_is_explicit(self):
        for command in ('infer', 'prepare'):
            args = [command, '--stage1', 'one', '--stage2', 'two', '--output', 'out']
            self.assertEqual(parser().parse_args(args).device, 'cpu')
            self.assertEqual(parser().parse_args([*args, '--device', 'cuda']).device, 'cuda')

    def test_qualified_core_sdk_and_models_are_unchanged(self):
        inventory = json.loads((ROOT/'provenance/qualified_sources.json').read_text())
        for name, checksum in inventory['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), checksum, name)

    def test_metadata_pins_upstream_and_downstream_contracts(self):
        metadata = json.loads((ROOT/'compatibility.json').read_text())
        self.assertEqual(metadata['upstream']['release_tag'], 'v1.0.2')
        self.assertEqual(metadata['upstream']['model_release_version'], '1.0.0')
        self.assertEqual(metadata['downstream']['release_tag'], 'v2.0.5')
        self.assertEqual(metadata['downstream']['evidence_schema'], 'stage3.assembly-evidence.v2')
        self.assertEqual(metadata, json.loads((ROOT/'src/paper_reconstruction_stage3_release/compatibility.json').read_text()))

    def test_verify_public_module_does_not_import_torch(self):
        script = ('import sys; from paper_reconstruction_stage3_release.cli import main; '
                  'code=main(["verify","--models",sys.argv[1]]); '
                  'assert "torch" not in sys.modules; raise SystemExit(code)')
        done = subprocess.run([sys.executable, '-B', '-c', script, str(ROOT/'models')], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)['default_device'], 'cpu')

    def test_pool_keeps_archive_supports_and_authenticates_resume(self):
        source, target = self.root/'native', self.root/'pooled'
        self.native(source)
        before = {p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob('*') if p.is_file()}
        first = pool_bundle(source, target)
        second = pool_bundle(source, target)
        self.assertFalse(first['reused'])
        self.assertTrue(second['reused'])
        self.assertEqual(list(load_bundle(source, full=True).hypotheses()), list(load_bundle(target, full=True).hypotheses()))
        self.assertTrue(all((source/p).read_bytes() == value for p, value in before.items()))

    def test_pool_rejects_a_different_source_on_resume(self):
        source, target = self.root/'native', self.root/'pooled'
        self.native(source)
        pool_bundle(source, target)
        other = self.root/'different'
        self.native(other, 'different')
        with self.assertRaisesRegex(ValueError, 'different inputs'):
            pool_bundle(other, target)

    def test_pool_public_interface_requires_no_torch(self):
        source, target = self.root/'native', self.root/'pooled'
        self.native(source)
        script = ('import sys; from paper_reconstruction_stage3_release.cli import main; '
                  'code=main(["pool","--input",sys.argv[1],"--output",sys.argv[2]]); '
                  'assert "torch" not in sys.modules; raise SystemExit(code)')
        done = subprocess.run([sys.executable, '-B', '-c', script, str(source), str(target)], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)['release_version'], '2.0.0')

    def test_prepare_publishes_a_complete_consumer_inventory_on_cpu(self):
        inputs = production_many(self.root/'inputs')
        def infer(models, stage1, stage2, output, **kwargs):
            self.assertEqual(kwargs['device'], 'cpu')
            entries, gallery, _ = production_inputs(stage1, stage2)
            export_bundle(output, 'prepare', entries, gallery, rows_for(gallery), provenance={},
                          configuration={'pose_configuration': {'maximum_assembly_collision': .08}, 'policy': {}})
            return {'status': 'ready', 'device': kwargs['device']}
        with patch('paper_reconstruction_stage3.alpha_inference.infer', side_effect=infer), contextlib.redirect_stdout(io.StringIO()):
            code = main(['prepare', '--stage1', inputs['stage1'], '--stage2', inputs['stage2'], '--output', str(self.root/'job')])
        self.assertEqual(code, 0)
        self.assertEqual(load_bundle(self.root/'job/bundle', full=True).summary()['pieces'], 3)

    def test_continuous_capture_profile_is_supported_without_scale_fitting(self):
        profile = json.loads((ROOT/'profiles/shared_scale_predicted_capture_v1.json').read_text())
        (self.root/'capture_profile.json').write_text(json.dumps(profile))
        config, receipts = configuration(self.root, {'pose_configuration': {}}, [])
        self.assertEqual(config['pose_configuration'], {'family': 'rigid', 'minimum_scale': 1., 'maximum_scale': 1.})
        self.assertEqual(len(receipts), 1)
        angle = .317
        h = np.array([[np.cos(angle), -np.sin(angle), 7.], [np.sin(angle), np.cos(angle), -4.], [0., 0., 1.]])
        np.testing.assert_array_equal(require_rigid(h), h)
        with self.assertRaises(ValueError):
            require_rigid(np.diag([1.01, 1.01, 1.]))

    def test_incompatible_acquisition_is_rejected(self):
        profile = json.loads((ROOT/'profiles/shared_scale_predicted_capture_v1.json').read_text())
        profile['perspective'] = True
        (self.root/'capture_profile.json').write_text(json.dumps(profile))
        with self.assertRaisesRegex(ValueError, 'explicit shared'):
            configuration(self.root, {'pose_configuration': {}}, [])


if __name__ == '__main__':
    unittest.main()
