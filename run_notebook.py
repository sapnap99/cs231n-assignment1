"""Execute a named assignment notebook using this Python interpreter."""
import argparse
import os
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('notebook', choices=['knn', 'softmax', 'two_layer_net', 'features', 'FullyConnectedNets'])
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    os.chdir(root)
    path = root / (args.notebook + '.ipynb')
    nb = nbformat.read(path, as_version=4)
    manager = KernelManager(kernel_name='python3')
    manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
    def progress(cell, cell_index, **kwargs):
        if cell.cell_type == 'code':
            print(f'Running cell {cell_index + 1}/{len(nb.cells)}', flush=True)
    client = NotebookClient(nb, km=manager, timeout=1200,
                            resources={'metadata': {'path': str(root)}},
                            on_cell_start=progress)
    try:
        client.execute()
    finally:
        nbformat.write(nb, path)
    print('Saved executed notebook:', path, flush=True)


if __name__ == '__main__':
    main()
