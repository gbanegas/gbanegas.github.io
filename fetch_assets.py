#!/usr/bin/env python3
"""Download static assets used by index.html from the still-live Vultr site.

Run BEFORE changing DNS for cryptme.in. Requires only Python 3 stdlib.
"""
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def fetch(path, base, timeout, overwrite):
    if not path.startswith(('/files/', '/images/')) or '..' in Path(path).parts:
        raise ValueError('Invalid asset path: ' + path)
    target = ROOT / path.lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size and not overwrite:
        return ('EXISTS', target.stat().st_size)
    url = base.rstrip('/') + path
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (static site migration)'})
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f'HTTP {response.status}')
        contenttype = response.headers.get('Content-Type', '').lower()
        # Do not inadvertently publish 404 HTML pages saved as PDFs or PNGs.
        with tempfile.NamedTemporaryFile('wb', dir=target.parent, delete=False) as tmp:
            staging = Path(tmp.name)
            try:
                total = 0
                first = b''
                while True:
                    data = response.read(1024*1024)
                    if not data: break
                    if not first: first = data[:16]
                    total += len(data)
                    if total > 100*1024*1024:
                        raise ValueError('Over 100 MiB (GitHub rejects individual files >= 100 MiB)')
                    tmp.write(data)
                if target.suffix.lower() == '.pdf' and not first.startswith(b'%PDF-'):
                    raise ValueError(f'Not a PDF (Content-Type: {contenttype})')
                if target.suffix.lower() == '.png' and not first.startswith(b'\x89PNG\r\n\x1a\n'):
                    raise ValueError(f'Not a PNG (Content-Type: {contenttype})')
                if not total: raise ValueError('Empty download')
            except BaseException:
                staging.unlink(missing_ok=True)
                raise
        staging.replace(target)
        return ('DOWNLOADED', total)


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--base', default='https://www.cryptme.in', help='Still-live website base URL')
    arg.add_argument('--overwrite', action='store_true')
    arg.add_argument('--timeout', type=int, default=25)
    args = arg.parse_args()
    paths=(ROOT/'assets.txt').read_text().splitlines()
    missing=[]
    for i,path in enumerate(paths,1):
        try:
            state,size=fetch(path,args.base,args.timeout,args.overwrite)
            print(f'[{i:02d}/{len(paths)}] {state:10s} {size:>10d} B {path}',flush=True)
        except (HTTPError,URLError,OSError,ValueError) as e:
            print(f'[{i:02d}/{len(paths)}] FAILED {path}: {e}',file=sys.stderr,flush=True)
            missing.append(path)
    (ROOT/'missing_assets.txt').write_text('\n'.join(missing) + ('\n' if missing else ''))
    print(f'\nAssets: {len(paths)-len(missing)} OK, {len(missing)} failed')
    if missing:
        print('Copy missing assets from Vultr into matching paths, then rerun.',file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
