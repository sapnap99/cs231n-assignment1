"""Run in PyCharm to check the selected interpreter and assignment data."""
import importlib
import sys
from pathlib import Path


def main():
    print('Python:', sys.executable)
    print('Version:', sys.version.split()[0])
    missing = []
    packages = {
        'numpy': 'numpy', 'scipy': 'scipy', 'matplotlib': 'matplotlib',
        'PIL': 'pillow', 'imageio': 'imageio', 'notebook': 'notebook',
        'ipykernel': 'ipykernel', 'six': 'six', 'past': 'future',
    }
    for module, package in packages.items():
        try:
            importlib.import_module(module)
            print('OK:', package)
        except ImportError as error:
            print('FAILED:', package, '-', error)
            missing.append(package)
    if missing:
        print('\nInstall into this interpreter with:')
        print(f'"{sys.executable}" -m pip install ' + ' '.join(missing))
        return 1
    from local_setup import prepare
    prepare(download=False)
    from cs231n.data_utils import load_CIFAR_batch
    from cs231n import features
    path = Path(__file__).resolve().parent / 'cs231n/datasets/cifar-10-batches-py/test_batch'
    images, labels = load_CIFAR_batch(str(path))
    assert images.shape == (10000, 32, 32, 3)
    assert labels.shape == (10000,)
    assert labels.min() == 0 and labels.max() == 9
    print('CIFAR-10 test batch:', images.shape, labels.shape)
    print('Environment check passed. Algorithm TODOs still need to be completed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
