"""Run the lean repository's tests without installing or changing the environment."""
from pathlib import Path
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
paths = [str(ROOT/'src'), str(ROOT/'contracts/stage3_to_stage4/v2/sdk/src')]
sys.path[:0] = paths
os.environ['PYTHONPATH'] = os.pathsep.join(paths)
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tests'), pattern='test_*.py'))
raise SystemExit(not result.wasSuccessful())
