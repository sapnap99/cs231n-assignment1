"""Local notebook setup and verified CIFAR-10 download (no Colab required)."""
from pathlib import Path
import hashlib
import os
import sys
import tarfile
import urllib.request
import time


def download_archive(partial):
    """Resume interrupted downloads and fail visibly instead of hanging."""
    url = 'https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz'
    for attempt in range(5):
        offset = partial.stat().st_size if partial.exists() else 0
        request = urllib.request.Request(url, headers={'Range': f'bytes={offset}-'})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                append = response.status == 206 and offset > 0
                if response.status == 206:
                    content_range = response.headers.get('Content-Range', '')
                    if not content_range.startswith(f'bytes {offset}-'):
                        raise RuntimeError(f'Unexpected server range: {content_range}')
                if not append:
                    offset = 0
                size = response.headers.get('Content-Length')
                total = offset + int(size) if size else None
                last_report = 0
                with partial.open('ab' if append else 'wb') as output:
                    while chunk := response.read(256 * 1024):
                        output.write(chunk)
                        offset += len(chunk)
                        if time.monotonic() - last_report >= 10:
                            print(f'Downloaded {offset / 1048576:.1f} MiB' +
                                  (f' / {total / 1048576:.1f} MiB' if total else ''), flush=True)
                            last_report = time.monotonic()
                if total is not None and offset != total:
                    raise OSError('Incomplete download')
            return
        except (OSError, urllib.error.URLError) as error:
            if attempt == 4:
                raise RuntimeError('Download failed. Run again to resume.') from error
            print(f'Download interrupted; retrying ({attempt + 1}/5): {error}', flush=True)
            time.sleep(2)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'cs231n' / 'datasets'

def prepare(download=True):
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    expected = [f'data_batch_{i}' for i in range(1, 6)] + ['test_batch', 'batches.meta']
    if not all((DATA / 'cifar-10-batches-py' / name).is_file() for name in expected):
        if not download:
            raise FileNotFoundError('CIFAR-10 missing. Run local_setup.py to download it.')
        archive = DATA / 'cifar-10-python.tar.gz'
        if not archive.exists():
            print('Downloading CIFAR-10 (about 163 MB)...', flush=True)
            partial = archive.with_suffix('.part')
            download_archive(partial)
            partial.replace(archive)
        with archive.open('rb') as stream:
            checksum = hashlib.file_digest(stream, 'md5').hexdigest()
        if checksum != 'c58f30108f718f92721af3b95e74349a':
            raise RuntimeError(f'Invalid download: remove {archive} and retry.')
        with tarfile.open(archive) as tar:
            tar.extractall(DATA, filter='data')
    print('Project:', ROOT)
    print('Python:', sys.executable)
    print('CIFAR-10 ready.')

if __name__ == '__main__':
    prepare()
