from pathlib import Path
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from paper_reconstruction_contracts import load_bundle, ContractError, compose, map_points
from paper_reconstruction_contracts.validation import validate_schema
from paper_reconstruction_stage3.alpha_package import load_package

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_projective_composition_and_inverse_use_homogeneous_division(self):
        first = np.array([[1., .1, 40.], [.03, 1., -2.], [.0002, -.0001, 1.]])
        second = np.array([[.9, -.2, 12.], [.2, .9, 9.], [-.0001, .0002, 1.]])
        points = np.array([[0., 0.], [100., 80.], [10., 30.]])
        np.testing.assert_allclose(map_points(points, compose(first, second)), map_points(map_points(points, second), first))
        np.testing.assert_allclose(map_points(map_points(points, first), np.linalg.inv(first)), points, atol=1e-10)
        self.assertGreater(np.max(np.abs(map_points(points, first) - (points@first[:2, :2].T+first[:2, 2]))), .1)

    def test_nonfinite_and_singular_matrices_are_rejected(self):
        for h in (np.zeros((3, 3)), [[1, 0, 0], [0, 1, 0], [0, 0, float('nan')]]):
            with self.assertRaises(ContractError): map_points([[0., 0.]], h)

    def test_closed_truth_is_rejected_even_inside_evidence(self):
        with self.assertRaisesRegex(ContractError, 'Closed evaluation'):
            validate_schema({'visual_evidence': {'ground_truth': [1, 2]}}, 'hypothesis')
        with self.assertRaisesRegex(ContractError, 'policy flag'):
            validate_schema({'reference_anchors_used': True}, 'hypothesis')

    def test_reader_is_independently_importable_without_stage3(self):
        sdk = ROOT/'contracts/stage3_to_stage4/v2/sdk/src'
        script = 'import sys; sys.path.insert(0,sys.argv[1]); from paper_reconstruction_contracts import load_bundle; assert "torch" not in sys.modules; assert "paper_reconstruction_stage3" not in sys.modules; print("independent")'
        with tempfile.TemporaryDirectory() as empty:
            env = {'PYTHONPATH': str(sdk)}
            import os
            done = subprocess.run([sys.executable, '-c', script, str(sdk)], cwd=empty, env={**os.environ, **env}, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_frozen_package_needs_no_research_directory(self):
        with patch('sqlite3.connect', side_effect=AssertionError('No research database may be opened')):
            _, m = load_package(ROOT/'models')
        self.assertEqual(len(m['rankers']), 2)
        self.assertTrue(all(r['optimizer_state_included'] is False for r in m['rankers']))

    def test_verify_command_requires_no_torch_import(self):
        script = 'import sys; from paper_reconstruction_stage3.cli import main; code=main(["verify","--models",sys.argv[1]]); assert "torch" not in sys.modules; raise SystemExit(code)'
        done = subprocess.run([sys.executable, '-c', script, str(ROOT/'models')], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)['status'], 'ready')


if __name__ == '__main__': unittest.main()
