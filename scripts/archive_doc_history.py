#!/usr/bin/env python3
"""Inventory immutable releases and preserve their original sources and RTD metadata.

Downloaded files are SHA256 verified and held outside Git for release attachment.
Never imports historical Python code. Run from the repository root.
"""
import argparse, concurrent.futures, hashlib, json, pathlib, subprocess, urllib.request


def get(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def canonical(version):
    return 'v' + version.removeprefix('v').replace('-rc', 'rc').replace('rc', '-rc')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', default='history')
    ap.add_argument('--artifacts', default='/tmp/params-proto-history-artifacts')
    args = ap.parse_args()
    output = pathlib.Path(args.output); output.mkdir(parents=True, exist_ok=True)
    artifacts = pathlib.Path(args.artifacts); artifacts.mkdir(parents=True, exist_ok=True)
    pypi = json.loads(get('https://pypi.org/pypi/params-proto/json'))
    rtd = json.loads(get('https://readthedocs.org/api/v3/projects/params-proto/versions/?limit=100'))
    builds = json.loads(get('https://readthedocs.org/api/v3/projects/params-proto/builds/?limit=100'))
    for name, data in [('pypi', pypi), ('readthedocs-versions', rtd), ('readthedocs-builds', builds)]:
        (output / (name + '.json')).write_text(json.dumps(data, indent=2) + '\n')
    tags = {canonical(t): t for t in git('tag').splitlines() if t.startswith('v')}
    versions = {canonical(v): v for v in pypi['releases']}
    records = []
    for name in sorted(tags.keys() | versions.keys()):
        row = {'version': name, 'branch': name}
        if name in tags:
            row.update(source_kind='git-tag', source_ref=tags[name], source_commit=git('rev-parse', tags[name] + '^{commit}'))
            paths = git('ls-tree', '-r', '--name-only', tags[name]).splitlines()
            row['documentation_source'] = 'docs' if any(p.startswith('docs/') for p in paths) else 'README and Python source'
        else:
            row.update(source_kind='pypi-sdist', pypi_version=versions[name])
            distributions = pypi['releases'][versions[name]]
            dist = next((d for d in distributions if d['packagetype'] == 'sdist'), None) or next((d for d in distributions if d['packagetype'] == 'bdist_wheel'), None)
            if dist:
                row['source_kind'] = 'pypi-sdist' if dist['packagetype'] == 'sdist' else 'pypi-wheel'
                row.update(source_url=dist['url'], source_sha256=dist['digests']['sha256'], source_filename=dist['filename'])
            else:
                row.update(source_kind='unavailable', reason='No Git tag or PyPI source distribution')
        records.append(row)
    def archive(row):
        if row['source_kind'] in ('pypi-sdist', 'pypi-wheel'):
            target = artifacts / row['source_filename']
            data = target.read_bytes() if target.exists() else get(row['source_url'])
            if sha(data) != row['source_sha256']:
                raise ValueError('SHA256 mismatch: ' + row['version'])
            target.write_bytes(data)
            row['source_archive'] = target.name
        else:
            target = artifacts / (row['version'] + '-source.tar.gz')
            if row['source_kind'] == 'git-tag':
                subprocess.run(['git', 'archive', '--format=tar.gz', '-o', str(target), row['source_commit']], check=True)
                row.update(source_archive=target.name, source_sha256=sha(target.read_bytes()))
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(archive, records))
    preserved = []
    for version in rtd['results']:
        if not version['built']:
            continue
        slug = version['slug']
        url = f'https://params-proto.readthedocs.io/_/downloads/en/{slug}/htmlzip/'
        row = {'version': slug, 'url': url, 'documentation_url': version['urls']['documentation'], 'rtd_reports_built': True, 'status': 'unavailable'}
        try:
            data = get(url)
            if not data.startswith(b'PK'):
                raise ValueError('Response was not a ZIP archive')
            target = artifacts / (slug + '-original-rtd.zip'); target.write_bytes(data)
            row.update(status='preserved', filename=target.name, sha256=sha(data))
        except Exception as error:
            row['reason'] = str(error)
        preserved.append(row)
    (output / 'versions.json').write_text(json.dumps({'versions': records}, indent=2) + '\n')
    (output / 'original-builds.json').write_text(json.dumps({'builds': preserved}, indent=2) + '\n')
    sums = [f'{sha(p.read_bytes())}  {p.name}' for p in sorted(artifacts.iterdir()) if p.is_file() and p.name != 'SHA256SUMS']
    (artifacts / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')
    print(json.dumps({'versions': len(records), 'source_kinds': {kind: sum(r['source_kind']==kind for r in records) for kind in sorted({r['source_kind'] for r in records})}, 'original_builds_preserved': sum(r['status']=='preserved' for r in preserved), 'artifacts': str(artifacts)}))


if __name__ == '__main__':
    main()
