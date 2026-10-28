"""CPU-default file interface; the qualified inference/pooling policies are unchanged."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from . import __version__


def interface_identity():
    root = Path(__file__).resolve().parent
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(root.iterdir()) if p.suffix in ('.py', '.json')}
    payload = json.dumps(files, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(payload).hexdigest()


def pool_bundle(source, output):
    """Publish once, or authenticate an already committed identical publication."""
    from paper_reconstruction_contracts import load_bundle
    from .pooling import POLICY, publish_replay
    source, output = Path(source).resolve(), Path(output).resolve()
    implementation = {'release_version': __version__, 'interface_sha256': interface_identity()}
    if output.exists():
        original = load_bundle(source, full=True)
        existing = load_bundle(output, full=True)
        provenance = existing.manifest['provenance']
        if (provenance.get('kind') != 'observable_saved_archive_pool_replay'
                or provenance.get('source_manifest_sha256') != original.manifest['manifest_sha256']
                or provenance.get('implementation') != implementation
                or existing.manifest['configuration'].get('pool_replay') != POLICY
                or existing.manifest['archive'] != original.manifest['archive']
                or existing.manifest['assets'] != original.manifest['assets']):
            raise ValueError('Existing pooled output has different inputs, policy or release interface')
        return {**existing.summary(), 'bundle': str(output), 'reused': True}
    audit = publish_replay(source, output, implementation, policy=POLICY)
    return {**load_bundle(output).summary(), 'bundle': str(output), 'reused': False, 'pool_audit': audit}


def parser():
    result = argparse.ArgumentParser(description='Stage 3 v2: qualified unit-scale evidence; CPU by default')
    result.add_argument('--version', action='version', version=__version__)
    commands = result.add_subparsers(dest='command', required=True)
    verify = commands.add_parser('verify', help='Authenticate frozen models and policy without importing Torch')
    verify.add_argument('--models', type=Path, default=Path('models'))
    for name, help_text in [('infer', 'Publish the frozen native evidence archive'),
                            ('prepare', 'Run native inference and publish the final Stage 4 working pool')]:
        command = commands.add_parser(name, help=help_text)
        for field in ('stage1', 'stage2', 'output'):
            command.add_argument('--'+field, type=Path, required=True)
        command.add_argument('--models', type=Path, default=Path('models'))
        command.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
        command.add_argument('--puzzle-id', default='page')
    pool = commands.add_parser('pool', help='Apply the unchanged support-pose-strata.v1 policy; no model inference')
    pool.add_argument('--input', type=Path, required=True)
    pool.add_argument('--output', type=Path, required=True)
    inspect = commands.add_parser('inspect', help='Fully validate a portable evidence bundle without Torch')
    inspect.add_argument('--bundle', type=Path, required=True)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'verify':
            from paper_reconstruction_stage3.alpha_package import load_package
            from paper_reconstruction_stage3 import __version__ as component_version
            root, manifest = load_package(args.models)
            result = {'status': 'ready', 'release_version': __version__,
                      'component_software_version': component_version, 'default_device': 'cpu',
                      'models_directory': str(root), 'models': [m['name'] for m in manifest['rankers']],
                      'policy_sha256': manifest['manifest_sha256'],
                      'implementation_sha256': manifest['implementation_sha256'],
                      'interface_sha256': interface_identity(), 'training_performed': False}
        elif args.command == 'inspect':
            from paper_reconstruction_contracts import load_bundle
            result = load_bundle(args.bundle, full=True).summary()
        elif args.command == 'pool':
            result = pool_bundle(args.input, args.output)
        else:
            from paper_reconstruction_stage3.alpha_inference import infer
            output = args.output.resolve()
            if args.command == 'prepare':
                for protected in (args.stage1, args.stage2, args.models):
                    protected = protected.resolve()
                    if output.is_relative_to(protected) or protected.is_relative_to(output):
                        raise ValueError('Preparation output overlaps immutable inputs/models')
                native = output/'native'
            else:
                native = output
            result = infer(args.models, args.stage1, args.stage2, native, device=args.device,
                           puzzle_id=args.puzzle_id, progress=lambda message: print(message, file=sys.stderr, flush=True))
            if args.command == 'prepare':
                result = {'native': result, 'consumer': pool_bundle(native, output/'bundle'),
                          'bundle': str(output/'bundle'), 'device': args.device}
        result['release_version'] = __version__
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except KeyboardInterrupt:
        print('Interrupted; committed native caches are preserved. Repeat the identical command to resume.', file=sys.stderr)
        return 130
    except Exception as error:
        print(json.dumps({'status': 'failed', 'release_version': __version__,
                          'error': type(error).__name__+': '+str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
