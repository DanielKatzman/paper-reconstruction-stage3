"""Fresh CPU Stage2 -> Stage3 -> Stage4 contract check; no evaluation/reference inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(python, arguments, paths, output, label):
    environment = dict(os.environ)
    environment['PYTHONPATH'] = os.pathsep.join(map(str, paths))
    environment['PYTHONDONTWRITEBYTECODE'] = '1'
    environment['CUDA_VISIBLE_DEVICES'] = '-1'
    log = output/(label+'.log')
    start = time.monotonic()
    print(label+': starting; log: '+str(log), flush=True)
    with log.open('wb') as stream:
        process = subprocess.Popen([str(python), '-B', *map(str, arguments)], cwd=ROOT,
                                   env=environment, stdout=stream, stderr=subprocess.STDOUT)
        try:
            while True:
                try:
                    code = process.wait(timeout=15)
                    break
                except subprocess.TimeoutExpired:
                    print(label+': working +'+str(round(time.monotonic()-start))+'s', flush=True)
        except BaseException:
            process.terminate()
            process.wait()
            raise
    if code:
        raise RuntimeError(label+' failed; see '+str(log))
    return {'seconds': time.monotonic()-start, 'log_sha256': sha(log), 'returncode': code}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage2-source', type=Path, required=True)
    parser.add_argument('--stage4-source', type=Path, required=True, help='Stage4 v2.0.5 repository root')
    parser.add_argument('--stage2-python', type=Path, default=Path(sys.executable))
    parser.add_argument('--stage4-python', type=Path, default=Path(sys.executable))
    parser.add_argument('--stage1', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    stage2, stage4, stage1, output = (p.resolve() for p in (args.stage2_source, args.stage4_source, args.stage1, args.output))
    if output.exists():
        parser.error('Use a new integration output directory')
    for protected in (stage2, stage4, stage1, ROOT/'models', ROOT/'src', ROOT/'contracts'):
        if output.is_relative_to(protected) or protected.is_relative_to(output):
            parser.error('Output overlaps a protected input')
    metadata = read(ROOT/'compatibility.json')
    if sha(stage2/'models/release.json') != metadata['upstream']['release_manifest_sha256']:
        raise ValueError('Stage2 model/config release differs')
    downstream = read(stage4/'compatibility.json')
    if downstream['release_version'] != '2.0.5' or downstream['stages']['stage4']['source_sdk_fingerprint'] != metadata['downstream']['source_sdk_fingerprint']:
        raise ValueError('Stage4 release differs from the qualified consumer')
    sdk = ROOT/'contracts/stage3_to_stage4/v2/sdk/src'
    other_sdk = stage4/'contracts/sdk/src'
    for path in (sdk/'paper_reconstruction_contracts').rglob('*'):
        if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts:
            if sha(path) != sha(other_sdk/path.relative_to(sdk)):
                raise ValueError('Stage3 and Stage4 SDK bytes differ')
    capture = stage1/'capture_profile.json'
    profile = ('shared_scale_complete_rectangle_v1.json' if read(capture).get('stage1_masks') == 'generator_exact_bypass'
               else 'shared_scale_complete_rectangle_predicted_v1.json')
    output.mkdir(parents=True)
    logs = output/'logs'
    logs.mkdir()
    timing = {}
    timing['stage2'] = execute(args.stage2_python, [stage2/'scripts/run_stage2_inference.py', '--input', stage1,
        '--output', output/'stage2', '--release', stage2/'models/release.json', '--cpu-threads', '4'],
        [stage2/'src'], logs, 'stage2')
    timing['stage2_verify'] = execute(args.stage2_python, [stage2/'scripts/verify_stage2_output.py',
        '--input', output/'stage2', '--release', stage2/'models/release.json'], [stage2/'src'], logs, 'stage2_verify')
    timing['stage3_prepare'] = execute(sys.executable, [ROOT/'scripts/stage3.py', 'prepare', '--stage1', stage1,
        '--stage2', output/'stage2', '--output', output/'stage3', '--puzzle-id', 'integration'],
        [ROOT/'src', sdk], logs, 'stage3_prepare')
    timing['stage4'] = execute(args.stage4_python, ['-m', 'paper_reconstruction_stage4', 'solve',
        '--bundle', output/'stage3/bundle', '--output', output/'stage4', '--config',
        stage4/'stages/stage4/configs/joint_v21_cut_repair_development.json', '--constraint-profile',
        stage4/'stages/stage4/configs'/profile, '--capture-profile', capture],
        [other_sdk, stage4/'stages/stage4/src'], logs, 'stage4')
    result = read(output/'stage4/result.json')
    if result['implementation']['sha256'] != metadata['downstream']['source_sdk_fingerprint']:
        raise ValueError('Actual Stage4 implementation differs from the declared consumer')
    assessment = read(output/'stage4.assessment/assessment.json')
    status = assessment['layouts'][0]['status']
    if status != 'supported' or not result['layouts'][0]['all_pieces_connected']:
        raise ValueError('Consumer published an unresolved integration case; inspect artifacts')
    import torch
    if torch.version.cuda is not None:
        raise ValueError('Run this qualification with CPU-only Torch installed')
    receipt = {'schema_version': 'stage3.integration-check.v1', 'release_version': '2.0.0',
        'upstream_release': 'v1.0.2', 'downstream_release': 'v2.0.5',
        'stage2_model_manifest_sha256': sha(stage2/'models/release.json'),
        'stage3_bundle_manifest_sha256': read(output/'stage3/bundle/bundle.json')['manifest_sha256'],
        'stage4_result_sha256': sha(output/'stage4/result.json'),
        'sdk_bytes_match': True, 'device': 'cpu', 'torch_version': torch.__version__,
        'torch_cuda_runtime': torch.version.cuda, 'pieces': result['input']['counts']['pieces'],
        'assessment_status': status, 'all_pieces_connected': True, 'references_opened': False,
        'scope': 'Fresh small-case CPU interoperability; not a new thirty-piece accuracy/performance qualification',
        'timing': timing}
    (output/'INTEGRATION.json').write_text(json.dumps(receipt, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    main()
