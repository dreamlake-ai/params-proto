#!/usr/bin/env python3
"""Archive and publish a static Dockit build as a real Netlify branch deploy."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import datetime
import re


def token():
    value = os.environ.get('NETLIFY_AUTH_TOKEN')
    if value:
        return value
    candidates = [Path.home() / 'Library/Preferences/netlify/config.json',
                  Path.home() / '.config/netlify/config.json']
    for path in candidates:
        if path.exists():
            config = json.loads(path.read_text())
            return config['users'][config['userId']]['auth']['token']
    raise SystemExit('Set NETLIFY_AUTH_TOKEN or log in with netlify login')


def request(path, credential, data=None, content_type='application/json', method=None):
    req = urllib.request.Request('https://api.netlify.com/api/v1' + path, data=data,
        headers={'Authorization': 'Bearer ' + credential, 'Content-Type': content_type}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f'Netlify HTTP {error.code}: {error.read().decode()}') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path('docs-site/dist/client'))
    parser.add_argument('--site', default='8714f50c-d823-4eff-b674-701225f78bf7')
    parser.add_argument('--branch', required=True)
    parser.add_argument('--archive-dir', type=Path, default=Path('build-archives'))
    parser.add_argument('--production', action='store_true', help='Promote only after the branch deploy is ready')
    args = parser.parse_args()
    if not (args.directory / 'index.html').is_file():
        parser.error('Build directory must contain index.html')
    args.archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    branch_name = re.sub(r'[^A-Za-z0-9._-]', '-', args.branch)
    archive_name = f'params-proto-docs-{branch_name}-{stamp}'
    zip_path = args.archive_dir / (archive_name + '.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(args.directory.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(args.directory))
    sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    zip_path.with_suffix('.zip.sha256').write_text(f'{sha}  {zip_path.name}\n')
    credential = token()
    query = urllib.parse.urlencode({'branch': args.branch, 'title': f'params-proto docs {args.branch}'})
    deploy = request(f'/sites/{args.site}/deploys?{query}', credential, zip_path.read_bytes(), 'application/zip')
    deadline = time.monotonic() + 300
    while deploy['state'] != 'ready':
        if deploy['state'] in ('error', 'failed', 'rejected') or time.monotonic() > deadline:
            raise RuntimeError(f'Deploy {deploy["id"]}: {deploy["state"]}: {deploy.get("error_message")}')
        time.sleep(3)
        deploy = request(f'/deploys/{deploy["id"]}', credential)
    if deploy.get('context') != 'branch-deploy' or deploy.get('branch') not in (args.branch, re.sub(r'[^a-z0-9-]', '-', args.branch.lower())):
        raise RuntimeError(f'Expected retained branch deploy, got {deploy.get("context")} {deploy.get("branch")}')
    result = {key: deploy.get(key) for key in ('id', 'state', 'branch', 'context', 'deploy_ssl_url', 'links')}
    result.update({'archive': zip_path.name, 'sha256': sha})
    if args.production:
        published = request(f'/sites/{args.site}/deploys/{deploy["id"]}/restore', credential, b'', method='POST')
        result['production_url'] = published.get('ssl_url')
    (args.archive_dir / f'{archive_name}.deploy.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
