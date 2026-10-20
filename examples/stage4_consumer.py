"""Reference Stage 4 process: validate file input independently of Stage 3."""
import argparse
import json
from pathlib import Path
import sys

# This bootstrap is for the example only. A separate Stage 4 project installs
# contracts/stage3_to_stage4/v2/sdk and imports this public package directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'contracts/stage3_to_stage4/v2/sdk/src'))
from paper_reconstruction_contracts import load_bundle

parser = argparse.ArgumentParser(); parser.add_argument('bundle', type=Path)
args = parser.parse_args(); data = load_bundle(args.bundle, full=True)
assert 'torch' not in sys.modules
assert 'paper_reconstruction_stage3' not in sys.modules
print(json.dumps(data.summary(), indent=2))
