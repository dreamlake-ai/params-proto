#!/usr/bin/env python3
"""Regenerate topic reference pages with the installed autodoc-py generator."""
from pathlib import Path
import json
from autodoc_py.grouped import generate_grouped

root = Path(__file__).resolve().parents[1]
version = json.loads((root / 'docs-site/version.json').read_text())['version']
count = generate_grouped(
    root / 'src/params_proto', root / 'docs-site/pages/reference',
    'params_proto', root / 'docs-site/api-pages.json', section='API reference',
    source_url=f'https://github.com/dreamlake-ai/params-proto/blob/v{version}/src/params_proto',
    url_prefix='/reference',
)
# Navigation sections are site concerns, independent of generator package releases.
reference = root / 'docs-site/pages/reference'
for page in (reference / 'compatibility').glob('*/+Page.mdx'):
    page.write_text(page.read_text().replace('section: "API reference"', 'section: "Compatibility"'))
(reference / 'compatibility/+Page.mdx').write_text((root / 'docs-site/compatibility-overview.mdx').read_text())
print(f'Generated {count} topic pages; the handwritten overviews are preserved.')
