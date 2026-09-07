# params-proto documentation

The current documentation runs on `@dreamlake/dockit` and is published at
https://params-proto.dreamlake.ai. The original Sphinx/MyST sources in `../docs/`
are preserved. This site owns the migrated, editable MDX pages under `pages/`.

```sh
pnpm install --frozen-lockfile
pnpm dev
pnpm build
```

The static output is `dist/client/`, including Pagefind search, Markdown twins,
`llms.txt`, and `llms-full.txt`. `version.json` controls the displayed release and
GitHub edit branch. `public/versions.json` supplies the version switcher; older
entries currently point to existing Read the Docs builds.

`../scripts/migrate_docs.py` bootstraps MyST Markdown into MDX for future migrations.
It converts toctrees, admonitions, terminal ANSI examples, and doc links. Its output
needs editorial review: the current API landing page and sidebar order were curated
after migration. Historical RST and README-only releases need additional conversion
work before bulk migration; do not treat a generated page as a validated release.

The generated Python API pages are committed as static MDX. The generator repository
is https://github.com/dreamlake-ai/autodoc-py. Regeneration should happen explicitly
from the version's source tree, without importing or running historical packages.

To regenerate the API with the published, pinned generator:

```sh
uvx --from 'git+https://github.com/dreamlake-ai/autodoc-py@9108a3f15fd88502f72876a6d478e1d240d444a5' autodoc-py ../src/params_proto --output pages/reference --module params_proto --section 'API reference'
```

After generation, review sidebar order and normalize relative API links to the
`/reference/` route prefix before publishing. The committed snapshot applies these
site-specific adjustments.
