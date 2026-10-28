"""Run from a checkout with the existing environment; no installation needed."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'contracts/stage3_to_stage4/v2/sdk/src')]
from paper_reconstruction_stage3_release.cli import main

if __name__ == '__main__': raise SystemExit(main())
