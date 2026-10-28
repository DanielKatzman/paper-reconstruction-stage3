"""Create a fresh component environment; CPU-only Torch is the default."""
import argparse
from pathlib import Path
import subprocess
import sys
import venv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--venv', type=Path, default=Path('.venv'))
    parser.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        parser.error('Use Python 3.12 for this qualified release')
    destination = args.venv.resolve()
    if destination.exists():
        parser.error('Choose a new environment; setup does not replace an existing one')
    if sys.platform == 'darwin' and args.device == 'cuda':
        parser.error('CUDA setup is supported on Windows/Linux only')
    root = Path(__file__).resolve().parents[1]
    venv.EnvBuilder(with_pip=True).create(destination)
    python = destination/('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    install = [str(python), '-m', 'pip', 'install']
    if sys.platform == 'darwin':
        subprocess.run([*install, 'torch==2.7.1'], cwd=root, check=True)
    else:
        suffix = 'cpu' if args.device == 'cpu' else 'cu118'
        subprocess.run([*install, 'torch==2.7.1+'+suffix, '--index-url',
                        'https://download.pytorch.org/whl/'+suffix], cwd=root, check=True)
    subprocess.run([*install, '-r', 'requirements.txt'], cwd=root, check=True)
    if args.device == 'cpu':
        subprocess.run([str(python), '-c', 'import torch; assert torch.version.cuda is None, "CPU-only Torch required"'], check=True)
    subprocess.run([str(python), '-B', 'scripts/stage3.py', 'verify'], cwd=root, check=True)


if __name__ == '__main__':
    main()
